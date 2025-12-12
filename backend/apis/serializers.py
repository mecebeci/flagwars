from rest_framework import serializers
from .models import Country, GameSession

class QuestionSerializer(serializers.ModelSerializer):
    flag_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Country
        fields = ['id', 'code', 'flag_emoji', 'flag_image_url']
    
    def get_flag_image_url(self, obj):
        if obj.flag_image:
            return obj.flag_image.url
        return None

class AnswerSerializer(serializers.Serializer):
    answer = serializers.CharField(max_length=100, trim_whitespace=True)

class StartGameSerializer(serializers.Serializer):
    game_mode = serializers.ChoiceField(
        choices=['quiz', 'flashcard'],
        default='quiz',
        help_text="Game mode: 'quiz' for traditional quiz mode, 'flashcard' for learning mode"
    )
    
    class Meta:
        fields = ['game_mode']

class GameSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = [
            'id',
            'user',
            'game_mode', 
            'questions',
            'viewed_countries',  
            'total_questions',
            'current_question',
            'score',
            'flags_viewed',  
            'started_at',
            'completed_at',
            'time_elapsed_seconds', 
            'is_completed'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at']
