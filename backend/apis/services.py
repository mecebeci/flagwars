import redis
from django.conf import settings
from typing import List, Dict, Optional
from datetime import timedelta
from django.utils import timezone
from .models import UserFlagProgress, Country

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
        


class LeitnerService:
    # Box review intervals (in days)
    BOX_INTERVALS = {
        1: 1,    # Review tomorrow
        2: 3,    # Review in 3 days
        3: 7,    # Review in 1 week
        4: 14,   # Review in 2 weeks
        5: 30,   # Review in 1 month
    }
    
    @staticmethod
    def get_due_flags(user, limit=10):
        """
        Get flags that are due for review (next_review_date <= now)
        Returns queryset of UserFlagProgress objects
        """
        return UserFlagProgress.objects.filter(
            user=user,
            next_review_date__lte=timezone.now()
        ).select_related('country').order_by('next_review_date')[:limit]
    
    @staticmethod
    def get_or_create_progress(user, country_id):
        """
        Get existing progress or create new one for a country
        """
        try:
            country = Country.objects.get(id=country_id)
        except Country.DoesNotExist:
            raise ValueError(f"Country with id {country_id} does not exist")
        
        progress, created = UserFlagProgress.objects.get_or_create(
            user=user,
            country=country,
            defaults={
                'box_number': 1,
                'next_review_date': timezone.now(),
                'total_reviews': 0,
                'correct_reviews': 0,
            }
        )
        
        return progress
    
    @staticmethod
    def process_review(user, country_id, is_correct):
        """
        Process a review answer and update progress
        
        Args:
            user: User object
            country_id: ID of the country being reviewed
            is_correct: Boolean indicating if answer was correct
            
        Returns:
            Updated UserFlagProgress object
        """
        # Get or create progress record
        progress = LeitnerService.get_or_create_progress(user, country_id)
        
        # Update review statistics
        progress.total_reviews += 1
        progress.last_reviewed_at = timezone.now()
        
        if is_correct:
            # Correct answer: move to next box (cap at 5)
            progress.correct_reviews += 1
            progress.box_number = min(progress.box_number + 1, 5)
        else:
            # Incorrect answer: reset to box 1
            progress.box_number = 1
        
        # Calculate next review date based on box number
        interval_days = LeitnerService.BOX_INTERVALS[progress.box_number]
        progress.next_review_date = timezone.now() + timedelta(days=interval_days)
        
        progress.save()
        
        return progress
    
    @staticmethod
    def get_learning_stats(user):
        """
        Get overall learning statistics for a user
        """
        total_flags = UserFlagProgress.objects.filter(user=user).count()
        due_flags = UserFlagProgress.objects.filter(
            user=user,
            next_review_date__lte=timezone.now()
        ).count()
        
        # Count flags in each box
        box_distribution = {}
        for box_num in range(1, 6):
            box_distribution[f'box_{box_num}'] = UserFlagProgress.objects.filter(
                user=user,
                box_number=box_num
            ).count()
        
        # Calculate average accuracy
        progress_records = UserFlagProgress.objects.filter(
            user=user,
            total_reviews__gt=0
        )
        
        if progress_records.exists():
            total_correct = sum(p.correct_reviews for p in progress_records)
            total_attempts = sum(p.total_reviews for p in progress_records)
            average_accuracy = round((total_correct / total_attempts) * 100, 1) if total_attempts > 0 else 0
        else:
            average_accuracy = 0
        
        return {
            'total_flags': total_flags,
            'due_flags': due_flags,
            'box_distribution': box_distribution,
            'average_accuracy': average_accuracy,
        }
    
    @staticmethod
    def add_new_flags_to_learn(user, limit=10):
        """
        Add new flags (not yet in learning system) to Box 1
        Returns list of newly added UserFlagProgress objects
        """
        # Get countries user hasn't started learning yet
        learned_country_ids = UserFlagProgress.objects.filter(
            user=user
        ).values_list('country_id', flat=True)
        
        new_countries = Country.objects.exclude(
            id__in=learned_country_ids
        ).order_by('?')[:limit]
        
        new_progress = []
        for country in new_countries:
            progress = UserFlagProgress.objects.create(
                user=user,
                country=country,
                box_number=1,
                next_review_date=timezone.now(),
            )
            new_progress.append(progress)
        
        return new_progress