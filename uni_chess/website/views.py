from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse


def welcome(request):
    return HttpResponse("Welcome to the UniChess page")


def date(request):
    return HttpResponse("This page was served at " + str(datetime.now()))


def about(request):
    return HttpResponse("This page is about the project:\n" +
                        "This project is developed for my bachelor degree.\n" +
                        "Good luck coding!")