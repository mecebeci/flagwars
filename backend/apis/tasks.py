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
    import redis
    from django.conf import settings

    try:
        redis_client = redis.Redis(
            host='redis',
            port=6379,
            password=settings.REDIS_PASSWORD if hasattr(settings, 'REDIS_PASSWORD') else None,
            decode_responses=True
        )

        leaderboard_key = 'flagwars:leaderboard'
        redis_client.zadd(leaderboard_key, {str(user_id): score})

        rank = redis_client.zrevrank(leaderboard_key, str(user_id))
        actual_rank = rank + 1 if rank is not None else None

        return f'Leaderboard updated: User {user_id} now has score {score}, rank #{actual_rank}'
    
    except redis.RedisError as e:
        return f'Redis error updating leaderboard: {str(e)}'
    except Exception as e:
        return f'Error updating leaderboard: {str(e)}'
    

@shared_task
def calculate_user_statistics(user_id):
    """
    Calculate and cache user statistics from their game history.
    Computes total games, average score, best score, etc.
    """
    from apis.models import GameSession
    from django.db.models import Count, Avg, Max, Sum
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
                total_score=Sum('score'),
                total_questions=Sum('total_questions')
            )
            
            # Extract values with defaults
            avg_score = float(stats.get('avg_score') or 0)
            best_score = int(stats.get('best_score') or 0)
            total_score = int(stats.get('total_score') or 0)
            total_questions = int(stats.get('total_questions') or 0)
            
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
    from apis.models import GameSession
    from django.db.models import Count, Avg, Max, Sum
    import redis
    from django.conf import settings
    import json
    
    try:
        user_sessions = GameSession.objects.filter(
            user_id=user_id,
            is_completed=True
        )
        
        stats = user_sessions.aggregate(
            total_games=Count('id'),
            avg_score=Avg('score'),
            total_score=Sum('score'),
            total_questions=Sum('total_questions')  
        )
        
        if stats['total_games'] == 0:
            stats_data = {
                'user_id': user_id,
                'total_games': 0,
                'avg_score': 0,
                'best_score': 0,
                'total_score': 0,
                'total_questions': 0,
                'accuracy': 0.0
            }
        else:
            total_score = stats['total_score'] or 0
            total_questions = stats['total_questions'] or 1 
            accuracy = (total_score / total_questions) * 100 if total_questions > 0 else 0.0
            
            stats_data = {
                'user_id': user_id,
                'total_games': stats['total_games'],
                'avg_score': round(float(stats['avg_score'] or 0), 2),
                'best_score': stats['best_score'] or 0,
                'total_score': total_score,
                'total_questions': stats['total_questions'] or 0,
                'accuracy': round(accuracy, 2)
            }
        
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
        
    except GameSession.DoesNotExist:
        return f'No game sessions found for user {user_id}'
    except Exception as e:
        return f'Error calculating statistics: {str(e)}'