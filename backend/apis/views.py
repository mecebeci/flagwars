from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from apis.tasks import update_leaderboard_async, calculate_user_statistics

from .models import Country, GameSession
from .serializers import *
import random


# ============================================
# GAME ENDPOINTS
# ============================================

@extend_schema(
    responses={
        201: GameSessionSerializer,
        400: OpenApiResponse(description='Bad request')
    },
    description="Start a new endless game session",
    summary="Start Game"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_game(request):
    # Check if there are countries in database
    if Country.objects.count() < 1:
        return Response(
            {'error': 'No countries in database. Please load country data.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create new game session
    game_session = GameSession.objects.create(
        user=request.user,
        current_country_id=None,
        viewed_countries=[],
        score=0,
        skips_remaining=3,
        skips_used=0,
        is_completed=False
    )
    
    serializer = GameSessionSerializer(game_session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    responses={
        200: QuestionSerializer,
        404: OpenApiResponse(description='No active game found')
    },
    description="Get current or next random flag",
    summary="Get Question"
)
@extend_schema(
    responses={
        200: QuestionSerializer,
        404: OpenApiResponse(description='No active game found')
    },
    description="Get current or next random flag",
    summary="Get Question"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_question(request):
    try:
        game_session = GameSession.objects.filter(
            user=request.user,
            is_completed=False
        ).latest('started_at')
    except GameSession.DoesNotExist:
        return Response(
            {'error': 'No active game found. Please start a new game'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # If there's a current country, return it (user is retrying)
    if game_session.current_country_id:
        try:
            country = Country.objects.get(id=game_session.current_country_id)
        except Country.DoesNotExist:
            country = None
    else:
        country = None
    
    # If no current country, get new random one
    if not country:
        # Get ALL viewed countries (not just last 30)
        viewed_ids = game_session.viewed_countries
        
        # Get total countries count
        total_countries = Country.objects.count()
        
        # Check if all countries have been viewed
        if len(viewed_ids) >= total_countries:
            # ALL COUNTRIES COMPLETED! Auto-finish game
            time_elapsed = (timezone.now() - game_session.started_at).total_seconds()
            game_session.time_elapsed_seconds = int(time_elapsed)
            game_session.is_completed = True
            game_session.completed_at = timezone.now()
            game_session.save()
            
            # Trigger leaderboard update
            from apis.tasks import update_leaderboard_async, calculate_user_statistics
            update_leaderboard_async.delay(request.user.id, game_session.score)
            calculate_user_statistics.delay(request.user.id)
            
            return Response(
                {
                    'game_completed': True,
                    'message': 'Congratulations! You have seen all flags!',
                    'final_score': game_session.score,
                    'total_countries': total_countries,
                    'countries_viewed': len(viewed_ids)
                },
                status=status.HTTP_200_OK
            )
        
        # Get random UNVIEWED country
        country = Country.objects.exclude(id__in=viewed_ids).order_by('?').first()
        
        if not country:
            return Response(
                {'error': 'No countries found in database'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Set as current country
        game_session.current_country_id = country.id
        game_session.save()
    
    # Return question data (country name HIDDEN)
    flag_url = country.flag_image.url if country.flag_image else None
    
    # Calculate progress
    total_countries = Country.objects.count()
    unique_viewed = len(game_session.viewed_countries)
    remaining = total_countries - unique_viewed
    
    return Response({
        'id': country.id,
        'code': country.code,
        'flag_image_url': flag_url,
        'score': game_session.score,
        'skips_remaining': game_session.skips_remaining,
        'countries_viewed': unique_viewed,
        'total_countries': total_countries,
        'remaining': remaining,
        'session_id': game_session.id
    }, status=status.HTTP_200_OK)

@extend_schema(
    request=AnswerSerializer,
    responses={200: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request):
    serializer = AnswerSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    answer = serializer.validated_data['answer'].strip().lower()

    try:
        game_session = GameSession.objects.filter(
            user=request.user,
            is_completed=False
        ).latest('started_at')
    except GameSession.DoesNotExist:
        return Response(
            {'error': 'No active game found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not game_session.current_country_id:
        return Response(
            {'error': 'No current question. Please call /game/question/ first.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        country = Country.objects.get(id=game_session.current_country_id)
    except Country.DoesNotExist:
        return Response(
            {'error': 'Country not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Build list of correct answers
    correct_answers = [country.name.lower()] + [alias.lower() for alias in country.aliases]
    
    # FLEXIBLE MATCHING: Also accept if answer is contained in name
    # Example: "taiwan" matches "Taiwan, Province of China"
    is_correct = answer in correct_answers
    
    # If not exact match, check if user's answer is a significant part of the name
    if not is_correct and len(answer) >= 4:
        country_name_lower = country.name.lower()
        # Check if answer is the first word of the country name
        first_word = country_name_lower.split(',')[0].strip()
        if answer == first_word:
            is_correct = True

    if is_correct:
        game_session.score += 1
        game_session.viewed_countries.append(country.id)
        game_session.current_country_id = None
        game_session.save()
        
        return Response({
            'correct': True,
            'correct_answer': country.name,
            'score': game_session.score,
            'message': 'Correct! Moving to next flag...',
            'auto_advance': True
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'correct': False,
            'correct_answer': country.name,
            'score': game_session.score,
            'message': 'Incorrect. Try again or skip.',
            'auto_advance': False
        }, status=status.HTTP_200_OK)


@extend_schema(
    responses={200: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def skip_question(request):
    """
    Skip current question (max 3 times per game)
    """
    try:
        game_session = GameSession.objects.filter(
            user=request.user,
            is_completed=False
        ).latest('started_at')
    except GameSession.DoesNotExist:
        return Response(
            {'error': 'No active game found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if skips remaining
    if game_session.skips_remaining <= 0:
        return Response(
            {'error': 'No skips remaining. You must answer or give up.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Use a skip
    game_session.skips_remaining -= 1
    game_session.skips_used += 1
    
    # Add current country to viewed (if exists)
    if game_session.current_country_id:
        game_session.viewed_countries.append(game_session.current_country_id)
    
    # Clear current country (will get new one on next /question/ call)
    game_session.current_country_id = None
    game_session.save()
    
    return Response({
        'message': 'Question skipped. Moving to next flag...',
        'skips_remaining': game_session.skips_remaining,
        'skips_used': game_session.skips_used,
        'score': game_session.score
    }, status=status.HTTP_200_OK)


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'time_elapsed_seconds': {
                    'type': 'integer',
                    'description': 'Elapsed time in seconds from frontend timer'
                }
            }
        }
    },
    responses={
        200: GameSessionSerializer,
        404: OpenApiResponse(description='No active game found')
    },
    description="Give up and finish the game",
    summary="Give Up / Finish Game"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def finish_game(request):
    """
    End the current game session (Give Up)
    """
    try:
        game_session = GameSession.objects.filter(
            user=request.user,
            is_completed=False
        ).latest('started_at')
    except GameSession.DoesNotExist:
        return Response(
            {'error': 'No active game found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # ⏱️ Get elapsed time from frontend timer (more accurate than backend calculation)
    frontend_time = request.data.get('time_elapsed_seconds')
    
    if frontend_time is not None:
        # Use frontend timer value
        game_session.time_elapsed_seconds = int(frontend_time)
    else:
        # Fallback: Calculate elapsed time from backend (if frontend didn't send it)
        time_elapsed = (timezone.now() - game_session.started_at).total_seconds()
        game_session.time_elapsed_seconds = int(time_elapsed)
    
    # Mark as completed
    game_session.is_completed = True
    game_session.completed_at = timezone.now()
    game_session.save()
    
    # Update leaderboard with final score
    update_leaderboard_async.delay(request.user.id, game_session.score)
    calculate_user_statistics.delay(request.user.id)
    
    # Prepare response
    serializer = GameSessionSerializer(game_session)
    
    # Calculate stats
    time_elapsed = game_session.time_elapsed_seconds
    flags_per_minute = (len(game_session.viewed_countries) / time_elapsed * 60) if time_elapsed > 0 else 0
    
    return Response({
        'message': 'Game completed successfully',
        'game': serializer.data,
        'stats': {
            'final_score': game_session.score,
            'countries_viewed': len(game_session.viewed_countries),
            'skips_used': game_session.skips_used,
            'time_seconds': game_session.time_elapsed_seconds,
            'flags_per_minute': round(flags_per_minute, 1)
        }
    }, status=status.HTTP_200_OK)


# ============================================
# LEADERBOARD & STATS
# ============================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def game_history(request):
    """Get user's game history"""
    games = GameSession.objects.filter(user=request.user).order_by('-started_at')
    serializer = GameSessionSerializer(games, many=True)

    return Response({
        'count': games.count(),
        'games': serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def random_country(request):
    """Get random country (for testing/home page)"""
    country = Country.objects.order_by('?').first()
    
    if not country:
        return Response(
            {'error': 'No countries found in database'}, 
            status=404
        )
    
    flag_url = country.flag_image.url if country.flag_image else None
    
    return Response({
        'id': country.id,
        'name': country.name,
        'code': country.code,
        'flag_image_url': flag_url,
    })

@extend_schema(
    responses={
        200: LeaderboardEntrySerializer(many=True),
    },
    description="Get top 10 players ranked by their best performance (score DESC, time ASC). One entry per user.",
    summary="Global Leaderboard - Top 10 Players"
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_leaderboard(request):    
    # Get all completed sessions, grouped by best performance per user
    from django.db.models import OuterRef, Subquery
    
    # Subquery to find each user's best session
    # Best = highest score, then fastest time
    best_sessions = GameSession.objects.filter(
        user=OuterRef('user'),
        is_completed=True
    ).order_by(
        '-score',
        'time_elapsed_seconds'
    ).values('id')[:1]
    
    # Get the actual best session for each user
    leaderboard = GameSession.objects.filter(
        id__in=Subquery(best_sessions),
        is_completed=True
    ).select_related('user').order_by(
        '-score',
        'time_elapsed_seconds',
        'completed_at'
    )[:10]
    
    serializer = LeaderboardEntrySerializer(leaderboard, many=True)
    
    # Add rank to each entry
    leaderboard_data = []
    for rank, entry in enumerate(serializer.data, start=1):
        leaderboard_data.append({
            'rank': rank,
            **entry
        })
    
    return Response({
        'leaderboard': leaderboard_data,
        'total_entries': len(leaderboard_data)
    }, status=status.HTTP_200_OK)