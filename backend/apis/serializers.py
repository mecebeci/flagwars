from rest_framework import serializers
from .models import Country, GameSession

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country # ← This tells DRF: "Get fields from Country model"
        fields = ['id', 'flag_emoji']

class AnswerSerializer(serializers.Serializer):
    answer = serializers.CharField(max_length=100, trim_whitespace=True)


class GameSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = ['id', 'score', 'total_questions', 'current_question', 'is_completed', 'started_at', 'completed_at']
        read_only_fields = ['id', 'started_at', 'completed_at']