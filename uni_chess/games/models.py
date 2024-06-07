from datetime import time, datetime

import jsonfield
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Tournament(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    players = jsonfield.JSONField(default=list)
    minimum_players = models.IntegerField(default=2)
    maximum_players = models.IntegerField(default=20)
    date = models.DateTimeField(default=timezone.now)
    start_minutes = models.IntegerField(default=10)
    start_date = models.DateTimeField(default=timezone.now)
    prize = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=False)
    duration = models.IntegerField(default=5)
    increment = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Round(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.IntegerField()

    def __str__(self):
        return f"Round {self.round_number} of {self.tournament.name}"


class Game(models.Model):
    white = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='white')
    black = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='black')
    result = models.IntegerField(default=0)
    date = models.DateTimeField(default=datetime.now)
    duration = models.IntegerField(default=5)  # Time in minutes
    increment = models.IntegerField(default=0)
    white_time_remaining = models.IntegerField(default=0)  # Time in seconds
    black_time_remaining = models.IntegerField(default=0)
    data = models.CharField(max_length=1000, default='')
    isActive = models.BooleanField(default=True)
    turn = models.CharField(max_length=10, default='white')
    endgame = models.CharField(max_length=100, default='')
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='games', null=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=True)

    def __str__(self):
        if self.isActive:
            return f"{self.white.first_name} {self.white.last_name} vs {self.black.first_name} {self.black.last_name}"
        else:
            if self.result == 0:
                return f"{self.white.first_name} {self.white.last_name}  DRAW  {self.black.first_name} {self.black.last_name}"
            elif self.result == 1:
                return f"{self.white.first_name} {self.white.last_name} 1 - 0 {self.black.first_name} {self.black.last_name}"
            elif self.result == 2:
                return f"{self.white.first_name} {self.white.last_name} 0 - 1 {self.black.first_name} {self.black.last_name}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    elo = models.IntegerField(default=1200)
    games = models.IntegerField(default=0)
    games_white = models.IntegerField(default=0)
    games_black = models.IntegerField(default=0)
    wins_white = models.IntegerField(default=0)
    wins_black = models.IntegerField(default=0)
    losses_white = models.IntegerField(default=0)
    losses_black = models.IntegerField(default=0)
    draws_white = models.IntegerField(default=0)
    draws_black = models.IntegerField(default=0)
    tournaments_participated = models.IntegerField(default=0)
    tournaments_won = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

