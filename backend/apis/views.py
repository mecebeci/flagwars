from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Country, GameSession
from .serializers import *
import random


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_game(request):
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
        questions=question_ids,
        total_questions=10,
        current_question=0,
        score=0
    )

    serializer = GameSessionSerializer(game_session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_question(request):
    try:
        game_session = GameSession.objects.filter(
            user = request.user,
            is_completed = False
        ).latest('started_at')
    except GameSession.DoesNotExist:
        return Response(
            {'error': 'No active game found. Please start a new game'},
            status=status.HTTP_404_NOT_FOUND
        )
    
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
    
    game_session.is_completed = True
    game_session.save()

    serializer = GameSessionSerializer(game_session)
    return Response({
        'message': 'Game completed successfully',
        'game': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def game_history(request):
    games = GameSession.objects.filter(user=request.user).order_by('-started_at') # reversed order
    serializer = GameSessionSerializer(games, many=True)

    return Response({
        'count': games.count(),
        'games' : serializer.data
    }, status=status.HTTP_200_OK)