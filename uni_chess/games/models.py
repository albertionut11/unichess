from datetime import time, datetime
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class Tournament(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    start_time = models.TimeField(default=time(9))
    prize = models.IntegerField(default=0)

    def __str__(self):
        return f"Tournament {self.name} with prize of {self.prize}$ at {self.start_time} on {self.date}"


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

    def __str__(self):
        return f"Game between White: {self.white} and Black: {self.black}"
