import redis
import logging
from django.conf import settings
from typing import List, Dict, Optional
from datetime import timedelta
from django.utils import timezone
from .models import Country

logger = logging.getLogger(__name__)


class LeaderboardService:
    """
    Service class for managing the global leaderboard using Redis sorted sets.

    This service provides high-performance leaderboard operations by leveraging
    Redis's ZADD, ZREVRANGE, and ZREVRANK commands. User scores are stored in
    a sorted set for O(log N) insertions and O(1) rank lookups.

    Attributes:
        LEADERBOARD_KEY: Redis key for the global leaderboard sorted set.
        redis_client: Redis connection instance with decoded responses.
    """

    LEADERBOARD_KEY = 'flagwars:leaderboard'

    def __init__(self) -> None:
        """
        Initialize the LeaderboardService with a Redis client connection.

        Raises:
            redis.ConnectionError: If unable to connect to Redis server.
        """
        self.redis_client = redis.Redis(
            host='redis',
            port=6379,
            password=getattr(settings, 'REDIS_PASSWORD', None),
            decode_responses=True
        )

    def add_score(self, user_id: int, score: int) -> bool:
        """
        Add or update a user's score on the leaderboard.

        If the user already exists in the leaderboard, their score will be updated.
        Redis sorted sets automatically maintain sorted order by score.

        Args:
            user_id: The unique identifier of the user.
            score: The total score to set for this user.

        Returns:
            True if the score was successfully added/updated, False on error.

        Example:
            >>> leaderboard = LeaderboardService()
            >>> leaderboard.add_score(user_id=42, score=1500)
            True
        """
        try:
            self.redis_client.zadd(self.LEADERBOARD_KEY, {str(user_id): score})
            return True
        except redis.RedisError as e:
            logger.error(f"Redis error adding score for user {user_id}: {e}")
            return False

    def get_top_players(self, limit: int = 100) -> List[Dict]:
        """
        Retrieve the top N players from the leaderboard.

        Players are returned in descending order by score. Each entry includes
        the player's rank (1-indexed), user ID, and total score.

        Args:
            limit: Maximum number of players to return (default: 100).

        Returns:
            List of dictionaries containing rank, user_id, and score.
            Returns empty list on error.

        Example:
            >>> leaderboard = LeaderboardService()
            >>> top_players = leaderboard.get_top_players(limit=10)
            >>> print(top_players[0])
            {'rank': 1, 'user_id': 42, 'score': 5420}
        """
        try:
            results = self.redis_client.zrevrange(
                self.LEADERBOARD_KEY,
                0,
                limit - 1,
                withscores=True
            )
            leaderboard = []
            for rank, (user_id, score) in enumerate(results, start=1):
                leaderboard.append({
                    'rank': rank,
                    'user_id': int(user_id),
                    'score': int(score)
                })
            return leaderboard

        except redis.RedisError as e:
            logger.error(f"Redis error getting top players: {e}")
            return []

    def get_user_rank(self, user_id: int) -> Optional[Dict]:
        """
        Get a specific user's rank and score on the leaderboard.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            Dictionary with rank (1-indexed), user_id, and score.
            Returns None if user not found or on error.

        Example:
            >>> leaderboard = LeaderboardService()
            >>> user_rank = leaderboard.get_user_rank(user_id=42)
            >>> print(user_rank)
            {'rank': 5, 'user_id': 42, 'score': 3200}
        """
        try:
            rank = self.redis_client.zrevrank(self.LEADERBOARD_KEY, str(user_id))

            if rank is None:
                return None

            score = self.redis_client.zscore(self.LEADERBOARD_KEY, str(user_id))
            return {
                'rank': rank + 1,  # Convert to 1-indexed
                'user_id': user_id,
                'score': int(score) if score else 0
            }

        except redis.RedisError as e:
            logger.error(f"Redis error getting user rank for user {user_id}: {e}")
            return None

    def get_user_score(self, user_id: int) -> Optional[int]:
        """
        Retrieve a user's total score from the leaderboard.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            The user's total score as an integer, or None if not found or on error.

        Example:
            >>> leaderboard = LeaderboardService()
            >>> score = leaderboard.get_user_score(user_id=42)
            >>> print(score)
            3200
        """
        try:
            score = self.redis_client.zscore(self.LEADERBOARD_KEY, str(user_id))
            return int(score) if score else None
        except redis.RedisError as e:
            logger.error(f"Redis error getting user score for user {user_id}: {e}")
            return None
