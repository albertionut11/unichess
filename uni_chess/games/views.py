import base64
import json
import uuid

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView, FormView

from games.game_logic.Board import Board
from games.game_logic.Play import Play
from .models import Game, Tournament
from .forms import GameForm


class PlayView(LoginRequiredMixin, TemplateView):
    template_name = 'games/play.html'

    def get_context_data(self, **kwargs):
        context = super(PlayView, self).get_context_data(**kwargs)

        game_id = self.kwargs.get('game_id')

        game = get_object_or_404(Game, pk=game_id)
        play = Play(game.data)

        html_table = play.board.render(context)
        context['html_table'] = html_table
        context['game_id'] = game_id
        return {'context': context}


@login_required
def create(request):
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            game = form.save()
            print('Here')
            print(game.id)
            return redirect("game_play", game_id=game.id)
    else:
        form = GameForm()
    return render(request, 'games/create.html', {"form": form})


@csrf_exempt
def move_piece(request, game_id):

    if request.method == "POST":
        data = json.loads(request.body)
        from_pos = data.get("from")
        to_pos = data.get("to")

        print(from_pos)
        print(to_pos)

        game = get_object_or_404(Game, pk=game_id)

        data = game.data
        data += from_pos + to_pos + ' '
        game.data = data

        game.save()

        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "fail"})


@login_required
def get_games(request):
    games = Game.objects.all()
    return render(request, 'games/games_list.html', {'games': games})


@login_required
def game_info(request, id):
    game = get_object_or_404(Game, pk=id)
    return render(request, "games/info.html", {"game": game})


@login_required
def get_tournaments(request):
    tournaments = Tournament.objects.all()
    return render(request, 'tournaments/tournaments.html', {'tournaments': tournaments})


@login_required
def tournament_info(request, id):
    tournament = get_object_or_404(Tournament, pk=id)
    return render(request, 'tournaments/info_tournaments.html', {'tournament': tournament})


@login_required
def update(request, id):
    game = get_object_or_404(Game, pk=id)
    if request.method == "POST":
        form = GameForm(request.POST, instance=game)
        if form.is_valid():
            form.save()
            return redirect("game_info", id)
    else:
        form = GameForm(instance=game)
    return render(request, "games/update.html", {"form": form})


@login_required
def delete(request, id):
    game = get_object_or_404(Game, pk=id)
    if request.method == "POST":
        game.delete()
        return redirect("games")
    else:
        return render(request, "games/delete.html", {"game": game})

