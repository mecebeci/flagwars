from django.urls import path
from . import views

urlpatterns = [
    path('game/start/', views.start_game, name='start_game'),
    path('game/question/', views.get_question, name='get_question'),
    path('game/answer/', views.submit_answer, name='submit_answer'),
    path('game/skip/', views.skip_question, name='skip_question'),
    path('game/finish/', views.finish_game, name='finish_game'),
    path('game/history/', views.game_history, name='game_history'),
    path('game/random-country/', views.random_country, name='random_country'),
    path('leaderboard/', views.get_leaderboard, name='leaderboard'),
]
