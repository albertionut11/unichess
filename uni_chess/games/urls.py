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
    path('get_moves/<int:game_id>', views.get_moves, name='get_moves'),
    path('tournaments', views.get_tournaments, name='tournaments'),
    path('tournaments/<int:id>', views.tournament_info, name='tournament_info'),
    path('create_tournament', views.create_tournament, name='create_tournament'),
    path('join_tournament/<int:tournament_id>', views.join_tournament, name='join_tournament'),
    path('tournaments/<int:tournament_id>/add_players/', views.add_players, name='add_players'),
    path('tournament/<int:tournament_id>/remove_player/', views.remove_player, name='remove_player'),
    path('tournament/<int:tournament_id>/start/', views.start_tournament, name='start_tournament'),
    path('save_time/<int:game_id>/', views.save_time, name='save_time'),
    path('get_timer_state/<int:game_id>/', views.get_timer_state, name='get_timer_state'),
    path('resign/<int:game_id>', views.resign, name='resign'),
    path('offer_draw/<int:game_id>', views.offer_draw, name='offer_draw'),
    path('cancel_draw/<int:game_id>', views.cancel_draw, name='cancel_draw'),
    path('accept_draw/<int:game_id>', views.accept_draw, name='accept_draw'),
    path('auth/register', views.register, name='register'),
]
