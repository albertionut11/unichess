from django.shortcuts import render, get_object_or_404

from .models import Game


def info(request, id):
    game = get_object_or_404(Game, pk=id)
    return render(request, "games/info.html", {"game": game})
