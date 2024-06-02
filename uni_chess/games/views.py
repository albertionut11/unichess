import base64
import json
import uuid
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView, FormView
from django.utils import timezone

from .game_logic.Play import Play
from .models import Game, Tournament
from .forms import GameForm


@login_required
def create(request):
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            game = form.save(commit=False)
            game.white_time_remaining = game.duration * 60  # Initialize time in seconds
            game.black_time_remaining = game.duration * 60  # Initialize time in seconds
            game.save()
            return redirect("game_play", game_id=game.id)
    else:
        form = GameForm()
    return render(request, 'games/create.html', {"form": form})


class PlayView(LoginRequiredMixin, TemplateView):
    template_name = 'games/play.html'

    def get_context_data(self, **kwargs):
        context = super(PlayView, self).get_context_data(**kwargs)

        game_id = self.kwargs.get('game_id')
        game = get_object_or_404(Game, pk=game_id)
        play = Play(game.data)

        context['user_role'] = self.get_user_role(game)
        html_table = play.board.render(context)
        context['html_table'] = html_table
        context['game_id'] = game_id
        context['turn'] = game.turn
        context['duration'] = game.duration
        context['increment'] = game.increment
        context['white_time_remaining'] = game.white_time_remaining
        context['black_time_remaining'] = game.black_time_remaining

        if play.checkmate:
            context['checkmate'] = play.checkmate

        return {'context': context}

    def get_user_role(self, game):
        user = self.request.user
        if user.username == game.white.username:
            return 'white'
        elif user.username == game.black.username:
            return 'black'
        return 'spectator'


@csrf_exempt
@login_required
def move_piece(request, game_id):
    game = get_object_or_404(Game, pk=game_id)

    if request.user.username != game.white.username and request.user.username != game.black.username:
        return JsonResponse({"status": "fail"})

    if request.method == "POST":
        data = json.loads(request.body)
        from_pos = data.get("from")
        to_pos = data.get("to")
        turn = data.get("turn")
        promotion = data.get("promotion")

        if (request.user.username == game.white.username and turn != 'white') or \
                (request.user.username == game.black.username and turn != 'black'):
            return JsonResponse({"status": "fail"})

        # validate move
        play = Play(game.data)
        moves, enPassantPos, castling = play.getMoves(from_pos[0], from_pos[1])

        ok, EP, C = False, False, None
        if to_pos == enPassantPos:
            ok = True
            EP = True
        elif castling and to_pos in castling:
            ok = True
            C = 'K' if to_pos[1] == 'g' else 'Q'
        elif to_pos in moves:
            ok = True
        if not ok:
            return JsonResponse({"status": "fail"})

        game_data = game.data

        if not EP and not promotion and not C:
            game_data += from_pos + to_pos + ' '
        elif EP:
            game_data += 'E' + from_pos + to_pos + ' '
        elif promotion:
            game_data += 'P' + from_pos + to_pos + promotion + ' '
        elif C:
            game_data += 'C' + from_pos + to_pos + C + ' '
        else:
            print("We should never be here in game_data stuff in move_piece")

        game.data = game_data

        new_turn = 'black' if turn == 'white' else 'white'
        game.turn = new_turn

        # Update the time for the player who just made the move
        if turn == 'white':
            game.white_time_remaining = data.get("white_time_remaining")
            game.black_time_remaining += game.increment  # Add increment to the other player's time
        else:
            game.black_time_remaining = data.get("black_time_remaining")
            game.white_time_remaining += game.increment  # Add increment to the other player's time

        game.save()

        # perform move on the table to be able to correctly check for checkmate
        play.board.make_move(from_pos[0], from_pos[1], to_pos[0], to_pos[1], promotion, C)
        checkmate = False
        if play.board.is_king_in_check(new_turn):
            if play.is_checkmate(new_turn):
                checkmate = True

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'game_{game_id}',
            {
                'type': 'game_move',
                'from': from_pos,
                'to': to_pos,
                'turn': new_turn,
                'enPassant': EP,
                'checkmate': checkmate,
                'promotion': promotion,
                'castling': C,
                'white_time_remaining': game.white_time_remaining,
                'black_time_remaining': game.black_time_remaining
            }
        )

        if checkmate:
            return JsonResponse({"status": "ok", "winner": turn})

        return JsonResponse({"status": "ok", "new_turn": new_turn, "enPassant": EP, "castling": C})
    return JsonResponse({"status": "fail"})


@login_required
@csrf_exempt
def get_moves(request, game_id):
    game = get_object_or_404(Game, pk=game_id)

    if request.user.username != game.white.username and request.user.username != game.black.username:
        return JsonResponse({"status": "fail"})
    if request.method == "GET":
        turn = request.GET.get("turn")
        pos = request.GET.get("from")
        from_row, from_col = pos[0], pos[1]

        if (request.user.username == game.white.username and turn != 'white') or \
                (request.user.username == game.black.username and turn != 'black'):
            return JsonResponse({"status": "fail"})

        play = Play(game.data)
        # breakpoint()
        moves, EP, castling = play.getMoves(from_row, from_col)
        # moves, EP, castling = play.getAllMoves(from_row, from_col)

        if castling:
            moves += castling
        return JsonResponse({"status": "ok", "moves": moves})

@login_required
@csrf_exempt
def save_time(request, game_id):
    game = get_object_or_404(Game, pk=game_id)

    if request.user.username != game.white.username and request.user.username != game.black.username:
        return JsonResponse({"status": "fail"})

    if request.method == "POST":
        data = json.loads(request.body)
        game.white_time_remaining = data.get('white_time_remaining', game.white_time_remaining)
        game.black_time_remaining = data.get('black_time_remaining', game.black_time_remaining)
        game.save()

        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "fail"})

@login_required
def get_timer_state(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    return JsonResponse({
        'white_time_remaining': game.white_time_remaining,
        'black_time_remaining': game.black_time_remaining
    })


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
