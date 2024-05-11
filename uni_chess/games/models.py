from datetime import time

from django.db import models


# Create your models here.
class Tournament(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    start_time = models.TimeField(default=time(9))
    prize = models.IntegerField(default=0)

    def __str__(self):
        return f"Tournament {self.name} with prize of {self.prize}$ at {self.start_time} on {self.date}"

class Game(models.Model):
    title = models.CharField(max_length=200)
    white = models.CharField(max_length=200)
    black = models.CharField(max_length=200)
    result = models.IntegerField()
    date = models.DateField()
    start_time = models.TimeField(default=time(9))
    duration = models.IntegerField(default=0)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} between White: {self.white} and Black: {self.black} at {self.start_time} on {self.date}"
