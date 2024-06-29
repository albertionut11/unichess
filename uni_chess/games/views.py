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
from .models import Game, Tournament, Round, Profile
from .forms import GameForm, SignUpForm, TournamentForm, AddPlayerForm, RemovePlayerForm

import chess
import chess.engine


@login_required
def create(request):
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            game = form.save(commit=False)
            game.white_time_remaining = game.duration * 60
            game.black_time_remaining = game.duration * 60
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
        context['white_username'] = game.white
        context['black_username'] = game.black
        context['is_active'] = game.isActive
        context['started'] = game.started

        context['time'], context['white_time'], context['black_time'] = formatTime(game.white_time_remaining, game.black_time_remaining)

        if play.checkmate:
            context['checkmate'] = play.checkmate
            game.isActive = False
        # breakpoint()
        if not game.isActive:
            # breakpoint()
            winner = "White" if game.result == 1 else "Black"
            loser = "Black" if game.result == 1 else "White"
            if game.endgame == 'draw':
                context['endgame_message'] = "Game drawn!"
            elif game.endgame == 'checkmate':
                context['endgame_message'] = f"Checkmate! {winner} wins!"
            elif game.endgame == 'resign':
                context['endgame_message'] = f"{loser} resigns! {winner} wins!"
            elif game.endgame == 'stalemate':
                context['endgame_message'] = "Stalemate!"
            elif game.endgame == 'time_expired':
                context['endgame_message'] = f"{winner} wins! {loser} ran out of time."

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
    # breakpoint()
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

        if checkmate != 'false' and checkmate != '':

            game.isActive = False
            if checkmate == 'true':
                game.endgame = 'checkmate'
                game.result = 1 if turn == 'white' else 2
            else:
                game.endgame = checkmate
            game.save()
            update_stats(game)
            return JsonResponse({"status": "ok", "winner": turn})

        return JsonResponse({"status": "ok", "new_turn": new_turn, "enPassant": EP, "castling": C, 'white_time_remaining': game.white_time_remaining, 'black_time_remaining': game.black_time_remaining})
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
    update_stats(game)

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
        update_stats(game)

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


def join_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if request.method == 'POST':
        if len(tournament.players) < tournament.maximum_players:
            tournament.players.append(request.user.username)
            tournament.save()
            return redirect('tournament_info', tournament.id)
        else:
            return render(request, 'tournaments/info_tournaments.html', {'tournament': tournament, 'error': 'Maximum number of players reached'})
    return redirect('tournament_info', tournament.id)


def leave_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if request.method == 'POST':
        if request.user.username in tournament.players:
            tournament.players.remove(request.user.username)
            tournament.save()
            return redirect('tournament_info', tournament.id)
        else:
            return render(request, 'tournaments/info_tournaments.html', {'tournament': tournament, 'error': 'You are not part of the tournament'})
    return redirect('tournament_info', tournament.id)


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
def start_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if request.user == tournament.owner and not tournament.is_active:
        players = [User.objects.get(username=player) for player in tournament.players]
        generated_rounds = RoundRobinGeneration(players)
        round_counter = 1
        for matches in generated_rounds:
            round_obj = Round.objects.create(tournament=tournament, round_number=round_counter)
            for white, black in matches:
                Game.objects.create(
                    white=white,
                    black=black,
                    duration=tournament.duration,
                    increment=tournament.increment,
                    white_time_remaining=tournament.duration*60,
                    black_time_remaining=tournament.duration*60,
                    round=round_obj,
                    tournament=tournament
                )
            round_counter += 1
        tournament.is_active = True
        tournament.save()
    return redirect('tournament_info', tournament.id)


def RoundRobinGeneration(players):
    n = len(players)
    rounds = []
    if n % 2 == 1:
        n += 1
        players.append(None)
    for round_num in range(n - 1):
        round_matches = []
        for i in range(n // 2):
            player1 = players[i]
            player2 = players[n - i - 1]
            if player1 is not None and player2 is not None:
                round_matches.append((player1, player2))
        players.insert(1, players.pop())
        rounds.append(round_matches)
    return rounds


@login_required
def tournament_info(request, id):
    tournament = get_object_or_404(Tournament, id=id)
    if tournament.is_active:
        rounds = Game.objects.filter(tournament=tournament)
        rankings = get_tournament_rankings(tournament)
        return render(request, 'tournaments/active_tournament.html', {'tournament': tournament, 'rounds': rounds, 'rankings': rankings})
    else:
        leave = False
        if request.user.username in tournament.players:
            leave = True
        return render(request, 'tournaments/info_tournaments.html', {'tournament': tournament, 'leave': leave})


def get_tournament_rankings(tournament):
    # breakpoint()
    players = tournament.players
    rankings = dict()

    for player in players:
        user = get_object_or_404(User, username=player)
        player_user_name = f'{user.first_name} {user.last_name}'
        rankings[player_user_name] = 0

    games = Game.objects.filter(tournament=tournament, isActive=False)
    for game in games:
        user = get_object_or_404(User, username=game.white.username)
        white_user_name = f'{user.first_name} {user.last_name}'
        user = get_object_or_404(User, username=game.black.username)
        black_user_name = f'{user.first_name} {user.last_name}'
        if game.result == 1:
            rankings[white_user_name] += 1
        elif game.result == 2:
            rankings[black_user_name] += 1
        elif game.result == 0:
            rankings[white_user_name] += 0.5
            rankings[black_user_name] += 0.5

    sorted_rankings = sorted(rankings.items(), key=lambda item: item[1], reverse=True)
    ranked_rankings = [(index + 1, player, points) for index, (player, points) in enumerate(sorted_rankings)]

    return ranked_rankings


@login_required
def profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)
    games = list(Game.objects.filter(white=request.user) | Game.objects.filter(black=request.user))[-10:]
    games.reverse()
    context = {
        'profile': profile,
        'games': games
    }
    return render(request, 'user/profile.html', context)


def leaderboard(request):
    users = User.objects.select_related('profile').order_by('-profile__elo')
    rankings = [(index + 1, f'{user.first_name} {user.last_name}', user.profile.elo) for index, user in enumerate(users)]
    return render(request, 'user/leaderboard.html', {'rankings': rankings})


def update_stats(game):
    white_profile = get_object_or_404(Profile, user=game.white)
    black_profile = get_object_or_404(Profile, user=game.black)

    # Update games played
    white_profile.games += 1
    black_profile.games += 1

    white_profile.games_white += 1
    black_profile.games_black += 1

    # Update wins, losses, draws
    if game.result == 1:
        white_profile.wins_white += 1
        black_profile.losses_black += 1
    elif game.result == 2:
        black_profile.wins_black += 1
        white_profile.losses_white += 1
    elif game.result == 0:
        white_profile.draws_white += 1
        black_profile.draws_black += 1

    # Update ELO
    white_elo = white_profile.elo
    black_elo = black_profile.elo

    # Simple ELO adjustment calculation
    k = 30  # K-factor
    expected_white = 1 / (1 + 10 ** ((black_elo - white_elo) / 400))
    expected_black = 1 / (1 + 10 ** ((white_elo - black_elo) / 400))

    if game.result == 1:
        white_profile.elo += k * (1 - expected_white)
        black_profile.elo += k * (0 - expected_black)
    elif game.result == 2:
        white_profile.elo += k * (0 - expected_white)
        black_profile.elo += k * (1 - expected_black)
    elif game.result == 0:
        white_profile.elo += k * (0.5 - expected_white)
        black_profile.elo += k * (0.5 - expected_black)

    white_profile.save()
    black_profile.save()


def analyse_game(request, game_id):
    # breakpoint()
    context = dict()
    game = get_object_or_404(Game, id=game_id)
    moves = game.data.split(' ')

    parsed_moves = parse_moves(moves)

    play = Play('')
    html_table = play.board.render(context)

    context = {
        'context': game,
        'evaluation': 0,
        'suggestions': [('e2e4', 0.2), ('d2d4', 0.1), ('c2c4', 0.1), ('g1g3', 0), ('c1c3', 0)],
        'parsed_moves': parsed_moves,
        'moves': json.dumps(moves),
        'html_table': html_table,
        'game_id': game_id,
    }

    return render(request, 'analyse/analyse_game.html', context)


@csrf_exempt
@login_required
def analyse_game_move(request, game_id):
    # breakpoint()
    game = get_object_or_404(Game, pk=game_id)

    if request.method == "POST":
        # breakpoint()
        data = json.loads(request.body)
        indice = data.get("indice")
        play = Play(game.data, ind=indice)
        turn = 'white' if indice % 2 == 0 else 'black'
        json_table = json.dumps(play.board.get_json_table())
        # breakpoint()
        moves = game.data.split(' ')[:indice]
        evaluation, suggestions = get_evaluation(moves, turn)

        return JsonResponse({"status": "ok", "json_table": json_table, "evaluation": evaluation, "suggestions": suggestions})
    return JsonResponse({"status": "fail"})


def get_evaluation(moves, turn):
    STOCKFISH_PATH = 'C:/Users/alber/Desktop/UniChessRepo/unichess/uni_chess/stockfish/stockfish-windows-x86-64-avx2.exe'
    board = chess.Board()
    for move in moves:
        uci_move = convert_to_uci(move)
        board.push_uci(uci_move)

    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
        # breakpoint()
        info = engine.analyse(board, chess.engine.Limit(time=1), multipv=7)
        scores = []
        for i in range(min(7, len(info))):
            if info[i]['score'].is_mate():
                if info[i].get('pv'):
                    score = 'Mate in ' + str(abs(info[i]['score'].relative.mate()))
                else:
                    score = 'Checkmate'
            else:
                relative_score = info[i]['score'].relative.score() / 100

                if turn == 'black':
                    relative_score = -relative_score
                score = str(relative_score)
            scores.append(score)
        # breakpoint()
        if scores[0] == 'Checkmate':
            suggestions = []
        else:
            suggestions = [(info[i]['pv'][0].uci(), scores[i]) for i in range(min(7, len(info)))]

        engine.quit()
    return scores[0], suggestions


def convert_to_uci(move):

    move = show_move(move)

    # Parse simple moves
    if len(move) == 4:
        return move

    # Parse EnPassant
    if move[0] == 'E':
        return move[1:]

    # Parse Promotion
    if move[0] == 'P':
        return move[1:5] + move[5].lower()

    # Parse Castling
    if move[0] == 'C':
        if move[-1] == 'K':
            return 'e1g1' if move[1:3] == 'e1' else 'e8g8'
        elif move[-1] == 'Q':
            return 'e1c1' if move[1:3] == 'e1' else 'e8c8'

    raise ValueError(f"Invalid move format: {move}")


def parse_moves(moves):
    if moves[-1] == '':
        moves = moves[:-1]

    n = len(moves)
    parsed_moves = []

    if n % 2 == 0:
        for i in range(0, n, 2):
            pair = {'white': show_move(moves[i]), 'black': show_move(moves[i + 1])}
            parsed_moves.append(pair)
    else:
        for i in range(0, n-1, 2):
            pair = {'white': show_move(moves[i]), 'black': show_move(moves[i + 1])}
            parsed_moves.append(pair)
        parsed_moves.append({'white': show_move(moves[-1]), 'black': 'N/A'})

    return parsed_moves


def show_move(move):
    n = len(move)
    if n == 4:
        return move[1] + move[0] + move[3] + move[2]
    elif n == 5:
        return move[0] + move[2] + move[1] + move[4] + move[3]
    else:
        return move[0] + move[2] + move[1] + move[4] + move[3] + move[5]


@login_required
def get_games(request):
    games = list(Game.objects.filter(started=True))[-10:]
    games.reverse()
    return render(request, 'games/games_list.html', {'games': games})


@csrf_exempt
@login_required
def start_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    if request.user != game.white:
        return JsonResponse({"status": "fail", "message": "Only the white player can start the game."})

    game.started = True
    game.save()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'game_{game_id}',
        {
            'type': 'start_game'
        }
    )

    return JsonResponse({"status": "ok"})


@csrf_exempt
def expire_game(request, game_id):
    # breakpoint()
    if request.method == "POST":
        game = get_object_or_404(Game, pk=game_id)
        data = json.loads(request.body)
        game.isActive = False
        game.endgame = "time_expired"
        game.result = 2 if data.get('white_time_remaining') == 0 else 1
        game.white_time_remaining = data.get('white_time_remaining')
        game.black_time_remaining = data.get('black_time_remaining')
        game.save()
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "fail"}, status=400)


@login_required
def game_info(request, id):
    game = get_object_or_404(Game, pk=id)
    return render(request, "games/info.html", {"game": game})


@login_required
def get_tournaments(request):
    tournaments = list(Tournament.objects.all())[-10:]
    tournaments.reverse()
    return render(request, 'tournaments/tournaments.html', {'tournaments': tournaments})


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


def formatTime(white, black):
    white_min, white_sec, black_min, black_sec = white // 60, white % 60, black // 60, black % 60

    l = [white_min, white_sec, black_min, black_sec]

    for i in range(0, len(l)):
        if l[i] < 10:
            l[i] = "0" + str(l[i])
        else:
            l[i] = str(l[i])

    return ({
        "white_min": l[0],
        "white_sec": l[1],
        "black_min": l[2],
        "black_sec": l[3]
    },
        white_min * 60 + white_sec,
        black_min * 60 + black_sec)
