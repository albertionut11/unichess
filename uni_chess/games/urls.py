from django.urls import path

from . import views

urlpatterns = [
    path('games', views.get_games, name='games'),
    path('games/<int:id>', views.game_info, name='game_info'),
    path('games/create', views.create, name='game_create'),
    path('games/update/<int:id>', views.update, name='game_update'),
    path('games/delete/<int:id>', views.delete, name='game_delete'),
    path('games/play/<int:game_id>', views.PlayView.as_view(), name='game_play'),
    path('move_piece/<int:game_id>', views.move_piece, name='move_piece'),
    path('tournaments', views.get_tournaments, name='tournaments'),
    path('tournaments/<int:id>', views.tournament_info, name='tournament_info')]
