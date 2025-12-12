from django.db import models
from django.contrib.auth import get_user_model

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_sessions')
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=10)
    current_question = models.IntegerField(default=0)
    questions = models.JSONField(default=list)
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Game #{self.id} - {self.user.username} ({self.score}/{self.total_questions})"