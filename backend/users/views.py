from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Avg, Sum, Max, Min
from .serializers import *
from apis.tasks import send_welcome_email


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Trigger async welcome email task
        send_welcome_email.delay(user.id)

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserStatsView(APIView):
    """Get current user's profile statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Query all user's sessions
        all_sessions = GameSession.objects.filter(user=user)
        completed_sessions = all_sessions.filter(is_completed=True)
        
        # Calculate total flags viewed from JSONField
        total_flags_viewed = sum(len(session.viewed_countries) for session in completed_sessions)
        
        # Calculate statistics
        stats = {
            'total_games': all_sessions.count(),
            'completed_games': completed_sessions.count(),
            'best_score': completed_sessions.aggregate(Max('score'))['score__max'] or 0,
            'best_time': completed_sessions.filter(score__gt=0).aggregate(Min('time_elapsed_seconds'))['time_elapsed_seconds__min'] or 0,
            'average_score': completed_sessions.aggregate(Avg('score'))['score__avg'] or 0,
            'total_correct_answers': completed_sessions.aggregate(Sum('score'))['score__sum'] or 0,
            'total_flags_viewed': total_flags_viewed,
            'member_since': user.date_joined
        }
        
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)


class RecentGamesView(APIView):
    """Get current user's recent game history"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        recent_games = GameSession.objects.filter(
            user=request.user,
            is_completed=True
        ).order_by('-completed_at')[:10]
        
        serializer = RecentGameSerializer(recent_games, many=True)
        return Response(serializer.data)