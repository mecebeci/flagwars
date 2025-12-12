from django.urls import path
from . import views

urlpatterns = [
    path('game/start/', views.start_game, name='start_game'),
    path('game/question/', views.get_question, name='get_question'),
    path('game/answer/', views.submit_answer, name='submit_answer'),
    path('game/finish/', views.finish_game, name='finish_game'),
    path('game/history/', views.game_history, name='game_history'),
    path('leaderboard/global/', views.global_leaderboard, name='global_leaderboard'),
    path('leaderboard/me/', views.my_leaderboard_rank, name='my_leaderboard_rank'),
    path('game/random-country/', views.random_country, name='random_country'),
    path('learn/due/', views.get_due_flags, name='get_due_flags'),
    path('learn/review/', views.submit_review, name='submit_review'),
    path('learn/stats/', views.get_learning_stats, name='get_learning_stats'),
    path('learn/add-new/', views.add_new_flags, name='add_new_flags'),
]
