from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=2, unique=True)
    flag_image = models.ImageField(upload_to='flags/', null=True, blank=True)
    aliases = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class GameSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='game_sessions'
    )
    
    # New fields for endless mode:
    current_country_id = models.IntegerField(null=True, blank=True)  # Current flag showing
    viewed_countries = models.JSONField(default=list)  # Countries already shown
    score = models.IntegerField(default=0)  # Correct answers only
    skips_remaining = models.IntegerField(default=3)  # Skip counter
    skips_used = models.IntegerField(default=0)  # Track skips used
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_elapsed_seconds = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - Score: {self.score} - {'Active' if not self.is_completed else 'Completed'}"
    

