import redis
from django.conf import settings
from typing import List, Dict, Optional
from datetime import timedelta
from django.utils import timezone
from .models import Country

class LeaderboardService:
    LEADERBOARD_KEY = 'flagwars:leaderboard'

    def __init__(self):
        self.redis_client = redis.Redis(
            host='redis',
            port=6379,
            password=getattr(settings, 'REDIS_PASSWORD', None),
            decode_responses=True
        )

    def add_score(self, user_id : int, score: int) -> bool:
        try:
            self.redis_client.zadd(self.LEADERBOARD_KEY, {str(user_id): score})
            return True
        except redis.RedisError as e:
            print(f"Redis error adding score: {e}")
            return False
        
    def get_top_players(self, limit: int = 100) -> List[Dict]:
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
                    'rank' : rank,
                    'user_id' : int(user_id),
                    'score' : int(score)
                })
            return leaderboard
        
        except redis.RedisError as e:
            print(f"Redis error getting top players: {e}")
            return []
        
    def get_user_rank(self, user_id : int) -> Optional[Dict]:
        try:
            rank = self.redis_client.zrevrank(self.LEADERBOARD_KEY, str(user_id))

            if rank is None:
                return None
            
            score = self.redis_client.zscore(self.LEADERBOARD_KEY, str(user_id))
            return {
                'rank' : rank + 1,
                'user_id' : user_id,
                'score' : int(score) if score else 0
            }
        
        except redis.RedisError as e:
            print(f"Redis error getting user rank: {e}")
            return None
        
    def get_user_score(self, user_id: int) -> Optional[int]:
        try:
            score = self.redis_client.zscore(self.LEADERBOARD_KEY, str(user_id))
            return int(score) if score else None
        except redis.RedisError as e:
            print(f"Redis error getting user score: {e}")
            return None
        