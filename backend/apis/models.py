from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=2, unique=True)
    flag_emoji = models.CharField(max_length=10)
    flag_image = models.ImageField(upload_to='flags/', null=True, blank=True)
    aliases = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class GameSession(models.Model):
    GAME_MODE_CHOICES = [
        ('quiz', 'Quiz Mode'),
        ('flashcard', 'Flashcard Mode'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Game mode
    game_mode = models.CharField(max_length=20, choices=GAME_MODE_CHOICES, default='quiz')
    
    # Questions (for quiz mode - pre-selected IDs)
    questions = models.JSONField(default=list)
    
    # Viewed countries (for flashcard mode - track what user saw)
    viewed_countries = models.JSONField(default=list)
    
    # Progress tracking
    total_questions = models.IntegerField(default=10)
    current_question = models.IntegerField(default=0)
    
    # Scoring
    score = models.IntegerField(default=0)
    flags_viewed = models.IntegerField(default=0)  # NEW: for flashcard mode
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_elapsed_seconds = models.IntegerField(default=0)  # NEW: track duration
    
    # Status
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.username} - {self.game_mode} - {self.started_at}"
    


class UserFlagProgress(models.Model):
    """
    Tracks user's learning progress for each flag using Leitner System (Box Method)
    Box 1 = Need to learn (review in 1 day)
    Box 2 = Learning (review in 3 days)
    Box 3 = Good (review in 7 days)
    Box 4 = Very Good (review in 14 days)
    Box 5 = Mastered (review in 30 days)
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='flag_progress'
    )
    
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    
    box_number = models.IntegerField(
        default=1,
        choices=[(1, 'Box 1'), (2, 'Box 2'), (3, 'Box 3'), (4, 'Box 4'), (5, 'Box 5')],
        help_text="Leitner box number (1=new, 5=mastered)"
    )
    
    next_review_date = models.DateTimeField(
        default=timezone.now,
        help_text="When this flag should be reviewed next"
    )
    
    total_reviews = models.IntegerField(
        default=0,
        help_text="Total number of times reviewed"
    )
    
    correct_reviews = models.IntegerField(
        default=0,
        help_text="Number of correct reviews"
    )
    
    last_reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this flag was reviewed"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'country')
        ordering = ['next_review_date']
        indexes = [
            models.Index(fields=['user', 'next_review_date']),
            models.Index(fields=['user', 'box_number']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.country.name} (Box {self.box_number})"
    
    @property
    def is_due(self):
        """Check if this flag is due for review"""
        return self.next_review_date <= timezone.now()
    
    @property
    def accuracy_rate(self):
        """Calculate accuracy percentage"""
        if self.total_reviews == 0:
            return 0
        return round((self.correct_reviews / self.total_reviews) * 100, 1)