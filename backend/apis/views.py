from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from apis.tasks import send_welcome_email, update_leaderboard_async, calculate_user_statistics

from .models import Country, GameSession, UserFlagProgress
from .serializers import *
import random

@extend_schema(
    request=StartGameSerializer,
    responses={
        201: GameSessionSerializer,
        400: OpenApiResponse(description='Bad request - Invalid game mode or not enough countries')
    },
    description="Start a new game session. Choose between 'quiz' mode (10 pre-selected questions) or 'flashcard' mode (endless learning).",
    summary="Start Game Session"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_game(request):
    # Validate input
    serializer = StartGameSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    game_mode = serializer.validated_data['game_mode']
    
    if game_mode == 'quiz':
        # Original logic: pre-select 10 questions
        all_countries = Country.objects.all()
        
        if all_countries.count() < 10:
            return Response(
                {'error': 'Not enough countries in database. Please load country data.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        random_countries = random.sample(list(all_countries), 10)
        question_ids = [country.id for country in random_countries]
        
        game_session = GameSession.objects.create(
            user=request.user,
            game_mode='quiz',
            questions=question_ids,
            total_questions=10,
            current_question=0,
            score=0
        )
    
    else:  # flashcard mode
        # No pre-selected questions - endless mode
        game_session = GameSession.objects.create(
            user=request.user,
            game_mode='flashcard',
            questions=[],
            viewed_countries=[],
            total_questions=0,  # Unlimited
            current_question=0,
            score=0,
            flags_viewed=0
        )
    
    serializer = GameSessionSerializer(game_session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@extend_schema(
    responses={
        200: QuestionSerializer,
        404: OpenApiResponse(description='No active game found'),
        400: OpenApiResponse(description='Game is completed')
    },
    description="Get next question for the active game session. Returns country data with or without name based on game mode.",
    summary="Get Next Question"
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
    
    if game_session.game_mode == 'quiz':
        # Original quiz logic
        if game_session.current_question >= game_session.total_questions:
            return Response(
                {'error': 'Game is completed. Please start a new game.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        current_index = game_session.current_question
        country_id = game_session.questions[current_index]
        
        try:
            country = Country.objects.get(id=country_id)
        except Country.DoesNotExist:
            return Response(
                {'error': 'Country not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = QuestionSerializer(country)
        data = serializer.data
        data['question_number'] = current_index + 1
        data['total_questions'] = game_session.total_questions
        data['session_id'] = game_session.id
        
        return Response(data, status=status.HTTP_200_OK)
    
    else:  # flashcard mode
        # Get random country (excluding recently viewed ones for variety)
        viewed_ids = game_session.viewed_countries[-20:] if game_session.viewed_countries else []
        
        if viewed_ids:
            country = Country.objects.exclude(id__in=viewed_ids).order_by('?').first()
        else:
            country = Country.objects.order_by('?').first()
        
        if not country:
            # If all countries viewed, reset and get any random one
            country = Country.objects.order_by('?').first()
        
        if not country:
            return Response(
                {'error': 'No countries found in database'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Track viewed country
        game_session.viewed_countries.append(country.id)
        game_session.flags_viewed += 1
        game_session.save()
        
        # Return flag with country name visible
        flag_url = country.flag_image.url if country.flag_image else None
        
        return Response({
            'id': country.id,
            'name': country.name,  # Visible in flashcard mode!
            'code': country.code,
            'flag_emoji': country.flag_emoji,
            'flag_image_url': flag_url,
            'flags_viewed': game_session.flags_viewed,
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
            user = request.user,
            is_completed = False
        ).latest('started_at')
    except GameSession.DoesNotExist:
        return Response(
            {'error': 'No active game found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if game_session.current_question >= game_session.total_questions:
        return Response(
            {'error': 'Game is already completed'},
            status= status.HTTP_400_BAD_REQUEST
        )
    
    current_index = game_session.current_question
    country_id = game_session.questions[current_index]

    try:
        country = Country.objects.get(id=country_id)
    except Country.DoesNotExist:
        return Response(
            {'error': 'Country not found.'},
            status = status.HTTP_404_NOT_FOUND
        )
    
    correct_answer = [country.name.lower()] + [alias.lower() for alias in country.aliases]
    is_correct = answer in correct_answer

    if is_correct:
        game_session.score += 1

    game_session.current_question += 1

    if game_session.current_question >= game_session.total_questions:
        game_session.is_completed = True
        game_session.completed_at = None

    game_session.save()

    return Response({
        'correct' : is_correct,
        'correct_answer' : country.name,
        'score' : game_session.score,
        'current_question': game_session.current_question,
        'total_question' : game_session.total_questions,
        'is_completed' : game_session.is_completed
    }, status=status.HTTP_200_OK)



@extend_schema(
    responses={
        200: GameSessionSerializer,
        404: OpenApiResponse(description='No active game found')
    },
    description="Finish the active game session. Calculates final score and updates leaderboard.",
    summary="Finish Game"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def finish_game(request):
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
    
    # Calculate elapsed time
    time_elapsed = (timezone.now() - game_session.started_at).total_seconds()
    game_session.time_elapsed_seconds = int(time_elapsed)
    
    if game_session.game_mode == 'flashcard':
        # Flashcard scoring: flags_viewed is already tracked
        # Score formula: flags_viewed * 10 + time bonus
        base_score = game_session.flags_viewed * 10
        
        # Time bonus: faster = better (max 300 bonus points)
        # If completed in under 60 seconds, get bonus
        time_bonus = max(0, 300 - int(time_elapsed))
        
        game_session.score = base_score + time_bonus
    
    # else: quiz mode score already tracked in submit_answer
    
    game_session.is_completed = True
    game_session.completed_at = timezone.now()
    game_session.save()

    # Update leaderboard and stats
    update_leaderboard_async.delay(request.user.id, game_session.score)
    calculate_user_statistics.delay(request.user.id)

    # Prepare response data
    serializer = GameSessionSerializer(game_session)
    
    response_data = {
        'message': 'Game completed successfully',
        'game': serializer.data
    }
    
    # Add extra stats for flashcard mode
    if game_session.game_mode == 'flashcard':
        flags_per_minute = (game_session.flags_viewed / time_elapsed * 60) if time_elapsed > 0 else 0
        response_data['stats'] = {
            'flags_viewed': game_session.flags_viewed,
            'time_seconds': game_session.time_elapsed_seconds,
            'flags_per_minute': round(flags_per_minute, 1),
            'final_score': game_session.score
        }
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def game_history(request):
    games = GameSession.objects.filter(user=request.user).order_by('-started_at') # reversed order
    serializer = GameSessionSerializer(games, many=True)

    return Response({
        'count': games.count(),
        'games' : serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def global_leaderboard(request):
    from apis.services import LeaderboardService
    from users.models import User

    try:
        leadearboard_service = LeaderboardService()

        top_players = leadearboard_service.get_top_player(limit=100)
        
        if not top_players:
            return Response({
                'leaderboard': [],
                'message': 'No leaderboard data available'
            }, status=status.HTTP_200_OK)
        
        user_ids = [player['user_id'] for player in top_players]
        users = User.objects.filter(id__in=user_ids).values('id', 'username')
        user_map = {user['id']: user['username'] for user in users}

        for player in top_players:
            player['username'] = user_map.get(player['user_id'], 'Unknown')
        
        return Response({
            'leaderboard': top_players,
            'total_players': len(top_players)
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve leaderboard: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_leaderboard_rank(request):
    from apis.services import LeaderboardService
    
    try:
        leaderboard_service = LeaderboardService()
        
        
        user_rank_data = leaderboard_service.get_user_rank(request.user.id)
        
        if not user_rank_data:
            return Response({
                'message': 'You are not on the leaderboard yet. Finish a game to get ranked!',
                'rank': None,
                'score': 0
            }, status=status.HTTP_200_OK)
        
        
        total_players = leaderboard_service.redis_client.zcard(
            LeaderboardService.LEADERBOARD_KEY
        )
        
        return Response({
            'rank': user_rank_data['rank'],
            'user_id': request.user.id,
            'username': request.user.username,
            'score': user_rank_data['score'],
            'total_players': total_players
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve your rank: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def random_country(request):
    country = Country.objects.order_by('?').first()
    
    if not country:
        return Response(
            {'error': 'No countries found in database'}, 
            status=404
        )
    
    # Get the full URL from the ImageField
    flag_url = country.flag_image.url if country.flag_image else None
    
    return Response({
        'id': country.id,
        'name': country.name,
        'code': country.code,
        'flag_emoji': country.flag_emoji,
        'flag_image_url': flag_url,
    })

from .services import LeitnerService

@extend_schema(
    responses={200: UserFlagProgressSerializer(many=True)},
    description="Get flags that are due for review (spaced repetition)",
    summary="Get Due Flags for Review"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_due_flags(request):
    limit = int(request.query_params.get('limit', 10))
    
    due_flags = LeitnerService.get_due_flags(request.user, limit=limit)
    serializer = UserFlagProgressSerializer(due_flags, many=True)
    
    return Response({
        'count': due_flags.count(),
        'due_flags': serializer.data
    }, status=status.HTTP_200_OK)


@extend_schema(
    request=ReviewAnswerSerializer,
    responses={200: UserFlagProgressSerializer},
    description="Submit a review answer for a flag",
    summary="Submit Review Answer"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_review(request):
    serializer = ReviewAnswerSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    country_id = serializer.validated_data['country_id']
    is_correct = serializer.validated_data['is_correct']
    
    try:
        progress = LeitnerService.process_review(
            user=request.user,
            country_id=country_id,
            is_correct=is_correct
        )
        
        result_serializer = UserFlagProgressSerializer(progress)
        
        return Response({
            'message': 'Review processed successfully',
            'progress': result_serializer.data,
            'moved_to_box': progress.box_number,
            'next_review': progress.next_review_date,
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    responses={200: dict},
    description="Get learning statistics and progress overview",
    summary="Get Learning Statistics"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_learning_stats(request):
    stats = LeitnerService.get_learning_stats(request.user)
    
    return Response(stats, status=status.HTTP_200_OK)


@extend_schema(
    responses={201: UserFlagProgressSerializer(many=True)},
    description="Add new flags to learning queue (Box 1)",
    summary="Add New Flags to Learn"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_new_flags(request):
    limit = int(request.data.get('limit', 10))
    
    new_flags = LeitnerService.add_new_flags_to_learn(request.user, limit=limit)
    serializer = UserFlagProgressSerializer(new_flags, many=True)
    
    return Response({
        'message': f'Added {len(new_flags)} new flags to learn',
        'new_flags': serializer.data
    }, status=status.HTTP_201_CREATED)