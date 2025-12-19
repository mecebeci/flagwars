from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_welcome_email(user_id):
    from users.models import User

    try:
        user = User.objects.get(id=user_id)
        
        subject = 'Welcome to Flag Wars!'
        message = f'Hello {user.username},\n\nWelcome to Flag Wars! Get ready to test your geography knowledge.\n\nGood luck!\n\nThe Flag Wars Team'
        from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@flagwars.com'
        recipient_list = [user.email]
        
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )

        return f'Welcome email sent to {user.email}'
    
    except User.DoesNotExist:
        return f'User with id {user_id} does not exist'
    except Exception as e:
        return f'Error sending email: {str(e)}'
    

@shared_task
def update_leaderboard_async(user_id, score):
    from apis.services import LeaderboardService
    
    try:
        leaderboard = LeaderboardService()

        success = leaderboard.add_score(user_id, score)

        if not success:
            return f'Failed to update leaderboard for user {user_id}'
        
        user_rank = leaderboard.get_user_rank(user_id)

        if user_rank:
            return f'Leaderboard updated: User {user_id} now has score {score}, rank #{user_rank["rank"]}'
        else:
            return f'Leaderboard updated: User {user_id} score {score} (rank unavailable)'
    except Exception as e:
        return f'Error updating leaderboard: {str(e)}'

@shared_task
def calculate_user_statistics(user_id):
    from apis.models import GameSession
    from django.db.models import Avg, Max, Sum
    import redis
    from django.conf import settings
    import json
    
    try:
        # Query completed game sessions for this user
        user_sessions = GameSession.objects.filter(
            user_id=user_id,
            is_completed=True
        )
        
        # Get count first
        total_games = user_sessions.count()
        
        # Handle case where user has no completed games
        if total_games == 0:
            stats_data = {
                'user_id': user_id,
                'total_games': 0,
                'avg_score': 0.0,
                'best_score': 0,
                'total_score': 0,
                'total_questions': 0,
                'accuracy': 0.0
            }
        else:
            # Calculate statistics safely
            stats = user_sessions.aggregate(
                avg_score=Avg('score'),
                best_score=Max('score'),
                total_score=Sum('score')
            )
            
            # Calculate total questions by counting viewed countries across all sessions
            total_questions = sum(len(session.viewed_countries) for session in user_sessions)
            
            # Extract values with defaults
            avg_score = float(stats.get('avg_score') or 0)
            best_score = int(stats.get('best_score') or 0)
            total_score = int(stats.get('total_score') or 0)
            
            # Calculate accuracy percentage
            accuracy = (total_score / total_questions * 100) if total_questions > 0 else 0.0
            
            stats_data = {
                'user_id': user_id,
                'total_games': total_games,
                'avg_score': round(avg_score, 2),
                'best_score': best_score,
                'total_score': total_score,
                'total_questions': total_questions,
                'accuracy': round(accuracy, 2)
            }
        
        # Cache statistics in Redis (expires in 1 hour)
        redis_client = redis.Redis(
            host='redis',
            port=6379,
            password=settings.REDIS_PASSWORD if hasattr(settings, 'REDIS_PASSWORD') else None,
            decode_responses=True
        )
        
        cache_key = f'flagwars:user_stats:{user_id}'
        redis_client.setex(
            cache_key,
            3600,
            json.dumps(stats_data)
        )
        
        return f'Statistics calculated for user {user_id}: {stats_data}'
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f'Error calculating statistics: {str(e)}\n{error_details}'
    

@shared_task
def calculate_daily_stats():
    from users.models import User
    from apis.models import GameSession
    from datetime import timedelta
    from django.utils import timezone
    
    try:
        week_ago = timezone.now() - timedelta(days=7)
        active_users = GameSession.objects.filter(
            started_at__gte=week_ago,
            is_completed=True
        ).values_list('user_id', flat=True).distinct()
        
        for user_id in active_users:
            calculate_user_statistics.delay(user_id)
        
        return f'Daily stats calculation queued for {len(active_users)} active users'
        
    except Exception as e:
        return f'Error in daily stats calculation: {str(e)}'
    
@shared_task
def cleanup_old_sessions():
    from apis.models import GameSession
    from datetime import timedelta
    from django.utils import timezone
    
    try:
        cutoff_time = timezone.now() - timedelta(hours=24)
        deleted_count, _ = GameSession.objects.filter(
            is_completed=False,
            started_at__lt=cutoff_time
        ).delete()
        
        return f'Cleanup completed: {deleted_count} old incomplete sessions deleted'
        
    except Exception as e:
        return f'Error in cleanup: {str(e)}'
    

@shared_task
def generate_leaderboard_snapshot():
    from apis.services import LeaderboardService
    import json
    from django.core.cache import cache
    from datetime import datetime
    
    try:
        leaderboard_service = LeaderboardService()
        top_players = leaderboard_service.get_top_players(limit=100)
        
        snapshot_key = f'leaderboard_snapshot_{datetime.now().strftime("%Y%m%d")}'
        cache.set(snapshot_key, top_players, timeout=86400 * 7)
        
        return f'Leaderboard snapshot saved: {len(top_players)} players'
        
    except Exception as e:
        return f'Error generating snapshot: {str(e)}'