from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apis.models import GameSession

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, label='Confirm Password')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'email' : {'required': True}
        }
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email

        return token
    

class UserStatsSerializer(serializers.Serializer):
    """User statistics summary"""
    total_games = serializers.IntegerField()
    completed_games = serializers.IntegerField()
    best_score = serializers.IntegerField()
    best_time = serializers.IntegerField()
    average_score = serializers.FloatField()
    total_correct_answers = serializers.IntegerField()
    total_flags_viewed = serializers.IntegerField()
    member_since = serializers.DateTimeField()

class RecentGameSerializer(serializers.ModelSerializer):
    """Serializer for recent game history"""
    completion_percentage = serializers.SerializerMethodField()
    countries_viewed = serializers.SerializerMethodField()  # Changed
    
    class Meta:
        model = GameSession
        fields = [
            'id',
            'score',
            'time_elapsed_seconds',
            'completed_at',
            'countries_viewed',
            'completion_percentage',
            'is_completed'
        ]
        read_only_fields = fields
    
    def get_countries_viewed(self, obj):
        return len(obj.viewed_countries)  # Get length of JSONField list
    
    def get_completion_percentage(self, obj):
        total_countries = 192
        countries_count = len(obj.viewed_countries)
        return round((countries_count / total_countries) * 100)