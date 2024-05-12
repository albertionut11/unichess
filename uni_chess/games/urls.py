from django.urls import path

from . import views

urlpatterns = [
    path('games', views.get_games, name='games'),
    path('games/<int:id>', views.game_info, name='game_info'),
    path('tournaments', views.get_tournaments, name='tournaments'),
    path('tournaments/<int:id>', views.tournament_info, name='tournament_info')]
