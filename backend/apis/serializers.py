from rest_framework import serializers
from .models import Country, GameSession, UserFlagProgress

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

class UserFlagProgressSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_code = serializers.CharField(source='country.code', read_only=True)
    flag_image_url = serializers.SerializerMethodField()
    flag_emoji = serializers.CharField(source='country.flag_emoji', read_only=True)
    is_due = serializers.BooleanField(read_only=True)
    accuracy_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = UserFlagProgress
        fields = [
            'id',
            'country',
            'country_name',
            'country_code',
            'flag_image_url',
            'flag_emoji',
            'box_number',
            'next_review_date',
            'total_reviews',
            'correct_reviews',
            'accuracy_rate',
            'is_due',
            'last_reviewed_at',
        ]
        read_only_fields = ['id', 'total_reviews', 'correct_reviews', 'last_reviewed_at']
    
    def get_flag_image_url(self, obj):
        if obj.country.flag_image:
            return obj.country.flag_image.url
        return None


class ReviewAnswerSerializer(serializers.Serializer):
    country_id = serializers.IntegerField(required=True)
    is_correct = serializers.BooleanField(required=True)