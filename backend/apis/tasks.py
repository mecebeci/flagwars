"""
Celery tasks for asynchronous background processing.

This module contains all Celery tasks for the Flag Wars application, including:
- Email notifications
- Leaderboard updates
- User statistics calculation
- Scheduled maintenance tasks
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_welcome_email(user_id: int) -> str:
    """
    Send a welcome email to a newly registered user.

    This task is triggered asynchronously after user registration to avoid
    blocking the registration API response.

    Args:
        user_id: The unique identifier of the user to send the email to.

    Returns:
        Success message with the email address, or error message if failed.

    Example:
        >>> send_welcome_email.delay(user_id=42)
        <AsyncResult: task_id>
    """
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

        logger.info(f'Welcome email sent to {user.email}')
        return f'Welcome email sent to {user.email}'

    except User.DoesNotExist:
        logger.error(f'User with id {user_id} does not exist')
        return f'User with id {user_id} does not exist'
    except Exception as e:
        logger.error(f'Error sending email to user {user_id}: {str(e)}')
        return f'Error sending email: {str(e)}'


@shared_task
def update_leaderboard_async(user_id: int, score: int) -> str:
    """
    Update a user's score on the global leaderboard asynchronously.

    This task is triggered after a user completes a game to update the Redis
    leaderboard without blocking the game finish API response.

    Args:
        user_id: The unique identifier of the user.
        score: The user's total cumulative score.

    Returns:
        Success message with the updated rank, or error message if failed.

    Example:
        >>> update_leaderboard_async.delay(user_id=42, score=1500)
        <AsyncResult: task_id>
    """
    from apis.services import LeaderboardService

    try:
        leaderboard = LeaderboardService()

        success = leaderboard.add_score(user_id, score)

        if not success:
            logger.error(f'Failed to update leaderboard for user {user_id}')
            return f'Failed to update leaderboard for user {user_id}'

        user_rank = leaderboard.get_user_rank(user_id)

        if user_rank:
            logger.info(f'Leaderboard updated: User {user_id} now has score {score}, rank #{user_rank["rank"]}')
            return f'Leaderboard updated: User {user_id} now has score {score}, rank #{user_rank["rank"]}'
        else:
            return f'Leaderboard updated: User {user_id} score {score} (rank unavailable)'
    except Exception as e:
        logger.error(f'Error updating leaderboard for user {user_id}: {str(e)}')
        return f'Error updating leaderboard: {str(e)}'


@shared_task
def calculate_user_statistics(user_id: int) -> str:
    """
    Calculate and cache comprehensive statistics for a user.

    This task aggregates data from all completed game sessions to compute:
    - Total games played
    - Average score
    - Best score
    - Total score
    - Total questions answered
    - Accuracy percentage

    Results are cached in Redis for 1 hour to reduce database load.

    Args:
        user_id: The unique identifier of the user.

    Returns:
        Success message with calculated statistics, or error message if failed.

    Example:
        >>> calculate_user_statistics.delay(user_id=42)
        <AsyncResult: task_id>
    """
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

        logger.info(f'Statistics calculated for user {user_id}: {stats_data}')
        return f'Statistics calculated for user {user_id}: {stats_data}'

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f'Error calculating statistics for user {user_id}: {str(e)}\n{error_details}')
        return f'Error calculating statistics: {str(e)}\n{error_details}'


@shared_task
def calculate_daily_stats() -> str:
    """
    Scheduled task to recalculate statistics for all recently active users.

    This task runs daily at 3:00 AM (configured in settings.CELERY_BEAT_SCHEDULE).
    It identifies users who have played in the last 7 days and queues individual
    statistics calculation tasks for each user.

    Returns:
        Success message with the number of users queued, or error message if failed.

    Note:
        This is a Celery Beat scheduled task. Do not call directly.
    """
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

        logger.info(f'Daily stats calculation queued for {len(active_users)} active users')
        return f'Daily stats calculation queued for {len(active_users)} active users'

    except Exception as e:
        logger.error(f'Error in daily stats calculation: {str(e)}')
        return f'Error in daily stats calculation: {str(e)}'


@shared_task
def cleanup_old_sessions() -> str:
    """
    Scheduled task to delete incomplete game sessions older than 24 hours.

    This maintenance task runs every 6 hours (configured in settings.CELERY_BEAT_SCHEDULE)
    to clean up abandoned game sessions that were never completed.

    Returns:
        Success message with the number of sessions deleted, or error message if failed.

    Note:
        This is a Celery Beat scheduled task. Do not call directly.
    """
    from apis.models import GameSession
    from datetime import timedelta
    from django.utils import timezone

    try:
        cutoff_time = timezone.now() - timedelta(hours=24)
        deleted_count, _ = GameSession.objects.filter(
            is_completed=False,
            started_at__lt=cutoff_time
        ).delete()

        logger.info(f'Cleanup completed: {deleted_count} old incomplete sessions deleted')
        return f'Cleanup completed: {deleted_count} old incomplete sessions deleted'

    except Exception as e:
        logger.error(f'Error in cleanup: {str(e)}')
        return f'Error in cleanup: {str(e)}'


@shared_task
def generate_leaderboard_snapshot() -> str:
    """
    Scheduled task to create a daily snapshot of the global leaderboard.

    This task runs daily at 11:59 PM (configured in settings.CELERY_BEAT_SCHEDULE).
    It captures the top 100 players and stores the snapshot in Django cache for 7 days.
    Snapshots can be used for historical leaderboard analysis.

    Returns:
        Success message with the number of players in the snapshot, or error message if failed.

    Note:
        This is a Celery Beat scheduled task. Do not call directly.
    """
    from apis.services import LeaderboardService
    import json
    from django.core.cache import cache
    from datetime import datetime

    try:
        leaderboard_service = LeaderboardService()
        top_players = leaderboard_service.get_top_players(limit=100)

        snapshot_key = f'leaderboard_snapshot_{datetime.now().strftime("%Y%m%d")}'
        cache.set(snapshot_key, top_players, timeout=86400 * 7)

        logger.info(f'Leaderboard snapshot saved: {len(top_players)} players')
        return f'Leaderboard snapshot saved: {len(top_players)} players'

    except Exception as e:
        logger.error(f'Error generating snapshot: {str(e)}')
        return f'Error generating snapshot: {str(e)}'
