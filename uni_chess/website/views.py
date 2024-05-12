from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse

from games.models import Game


def welcome(request):
    return render(request, "website/welcome.html",
                  {"message": "Chess is a beautiful sport.",
                           "games": Game.objects.all})


def date(request):
    return HttpResponse("This page was served at " + str(datetime.now()))


def about(request):
    return HttpResponse("This page is about the project:\n" +
                        "This project is developed for my bachelor degree.\n" +
                        "Good luck coding!")
