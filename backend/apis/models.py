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
    

