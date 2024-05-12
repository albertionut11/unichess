from django.shortcuts import render, get_object_or_404

from .models import Game, Tournament


def get_games(request):
    games = Game.objects.all()
    return render(request, 'games/games.html', {'games': games})

def game_info(request, id):
    game = get_object_or_404(Game, pk=id)
    return render(request, "games/info_games.html", {"game": game})


def get_tournaments(request):
    tournaments = Tournament.objects.all()
    return render(request, 'tournaments/tournaments.html', {'tournaments': tournaments})


def tournament_info(request, id):
    tournament = get_object_or_404(Tournament, pk=id)
    return render(request, 'tournaments/info_tournaments.html', {'tournament': tournament})