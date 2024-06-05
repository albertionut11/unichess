import json
from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from .game_logic.Play import Play
from .models import Game, Tournament
from .forms import GameForm, SignUpForm, TournamentForm, AddPlayerForm, RemovePlayerForm


@login_required
def create(request):
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            game = form.save(commit=False)
            game.white_time_remaining = game.duration * 60  # Initialize time in seconds
            game.black_time_remaining = game.duration * 60  # Initialize time in seconds
            game.isActive = 1
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
        context['white_username'] = game.white
        context['black_username'] = game.black
        context['is_active'] = game.isActive

        if play.checkmate:
            context['checkmate'] = play.checkmate

        if not game.isActive:
            winner = "Black" if game.turn == "white" else "Black"
            loser = "White" if game.turn == "white" else "White"
            if game.endgame == 'draw':
                context['endgame_message'] = "Game drawn!"
            elif game.endgame == 'checkmate':
                context['endgame_message'] = f"Checkmate! {winner} wins!"
            elif game.endgame == 'resign':
                context['endgame_message'] = f"{loser} resigns! {winner} wins!"
            elif game.endgame == 'stalemate':
                context['endgame_message'] = "Stalemate!"

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
        else:
            game.black_time_remaining = data.get("black_time_remaining")

        game.save()
        # perform move on the table to be able to correctly check for checkmate
        play.board.make_move(from_pos[0], from_pos[1], to_pos[0], to_pos[1], promotion, C)
        checkmate = ''
        if play.board.is_king_in_check(new_turn):
            checkmate = play.is_checkmate(new_turn)

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

        if checkmate != 'false':
            if checkmate == 'true':
                game.endgame = 'checkmate'
            else:
                game.endgame = checkmate
            game.save()
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
@csrf_exempt
def resign(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    if request.user == game.white:
        winner = "Black"
        loser = "White"
        game.result = 2
    elif request.user == game.black:
        winner = "White"
        loser = "Black"
        game.result = 1
    else:
        return JsonResponse({"status": "fail"})

    game.isActive = False
    game.endgame = "resign"
    game.save()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'game_{game_id}',
        {
            'type': 'end_game',
            'winner': winner,
            'loser': loser,
            'message': f'{loser} resigns! {winner} wins!'
        }
    )

    print(winner, loser)
    return JsonResponse({"status": "ok", "winner": winner, "loser": loser})

@csrf_exempt
def offer_draw(request, game_id):
    data = json.loads(request.body)
    turn = data['turn']

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'game_{game_id}',
        {
            'type': 'offer_draw',
            'turn': turn
        }
    )

    return JsonResponse({"status": "ok"})


@csrf_exempt
def cancel_draw(request, game_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'game_{game_id}',
        {
            'type': 'cancel_draw',
        }
    )

    return JsonResponse({"status": "ok"})


@csrf_exempt
def accept_draw(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    if game.isActive:
        game.result = 0
        game.endgame = 'draw'
        game.isActive = False
        game.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'game_{game.id}',
            {
                'type': 'accept_draw'
            }
        )

        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "fail"})


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def create_tournament(request):
    if request.method == 'POST':
        form = TournamentForm(request.POST)
        if form.is_valid():
            tournament = form.save(commit=False)
            tournament.owner = request.user
            tournament.date = timezone.now()
            tournament.start_date = tournament.date + timedelta(minutes=tournament.start_minutes)
            tournament.save()
            return redirect('tournaments')
    else:
        form = TournamentForm()
    return render(request, 'tournaments/create_tournament.html', {'form': form})


@login_required
def join_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if request.user.username not in tournament.players:
        tournament.players.append(request.user.username)
        tournament.save()
    return redirect('tournament_info', tournament_id)


@login_required
def add_players(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if request.user != tournament.owner:
        return redirect('tournaments')

    if request.method == 'POST':
        form = AddPlayerForm(request.POST, tournament=tournament)
        if form.is_valid():
            user = form.cleaned_data['user']
            if user.username not in tournament.players:
                tournament.players.append(user.username)
                tournament.save()
                return redirect('tournament_info', tournament.id)
    else:
        form = AddPlayerForm(tournament=tournament)

    return render(request, 'tournaments/add_players.html', {'form': form, 'tournament': tournament})


@login_required
def remove_player(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if request.user != tournament.owner:
        return redirect('tournament_info', tournament_id=tournament_id)

    if request.method == 'POST':
        form = RemovePlayerForm(request.POST, tournament=tournament)
        if form.is_valid():
            user = form.cleaned_data['user']
            tournament.players.remove(user.username)
            tournament.save()
            return redirect('tournament_info', tournament_id)
    else:
        form = RemovePlayerForm(tournament=tournament)

    return render(request, 'tournaments/remove_players.html', {'form': form, 'tournament': tournament})


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
