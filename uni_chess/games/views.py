import base64
import json
import uuid

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
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

        context['msg'] = 'Chess is beautiful'

        play_id = self.kwargs.get('play_id')

        cache_key = f'game_{play_id}'
        state = cache.get(cache_key)
        play = Play(state)

        html_table = play.board.render(context)
        context['html_table'] = html_table
        context['play_id'] = play_id
        return {'context': context}


@login_required
def create_play(request):
    play = Play(None)

    play_id = base64.urlsafe_b64encode(uuid.uuid4().bytes).rstrip(b'=').decode('ascii')

    cache_key = f'game_{play_id}'
    cache.set(cache_key, play.board.table)
    return redirect('game_play', play_id=play_id)


@csrf_exempt
def move_piece(request, play_id):

    cache_key = f'game_{play_id}'

    if request.method == "POST":
        data = json.loads(request.body)
        from_pos = data.get("from")
        to_pos = data.get("to")

        print(from_pos)
        print(to_pos)

        state = cache.get(cache_key)
        from_row, from_col = from_pos[0], from_pos[1]
        to_row, to_col = to_pos[0], to_pos[1]

        # Move piece
        state[to_row][to_col] = state[from_row][from_col]
        state[from_row][from_col] = '.'

        cache.set(cache_key, state)

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
def create(request):
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("games")
    else:
        form = GameForm()
    return render(request, 'games/create.html', {"form": form})


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

