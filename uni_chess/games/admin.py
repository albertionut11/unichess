from django.contrib import admin

from .models import Game, Tournament, Round, Profile

admin.site.register(Game)
admin.site.register(Tournament)
admin.site.register(Round)
admin.site.register(Profile)

