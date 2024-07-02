from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse

from games.models import Game


def welcome(request):
    if request.user.is_authenticated:
        context = {}
        games = list(Game.objects.filter(white=request.user, started=True, isActive=True) | Game.objects.filter(black=request.user, started=True, isActive=True))
        context['active_game'] = len(games) > 0
    else:
        context = {}
    print(context)
    return render(request, "website/welcome.html", context)


def date(request):
    return HttpResponse("This page was served at " + str(datetime.now()))


def about(request):
    return HttpResponse("This page is about the project:\n" +
                        "This project is developed for my bachelor degree.\n" +
                        "Good luck coding!")
