from django.contrib import admin

from .models import Game, Tournament, Round

admin.site.register(Game)
admin.site.register(Tournament)
admin.site.register(Round)
