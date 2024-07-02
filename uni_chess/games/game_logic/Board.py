from django.template import loader
from .Piece import King, Queen, Bishop, Knight, Rook, Pawn, Piece


class Board:
    def __init__(self):
        print('Board.__init__')
        self.table = dict()
        self.data = None
        self.template_name = 'games/table.html'
        self.light_color = 'F5DEB3'
        self.dark_color = 'a1764b'
        self.turn = 'white'
        self.kings_moved = {'white': False, 'black': False}
        self.rooks_moved = {'1a': False, '1h': False, '8a': False, '8h': False}

    def load_table(self, data, ind=None):
        self.new_table()
        self.data = data
        # breakpoint()

        moves = data.split(' ')[:-1] if self.data[-1] == ' ' else data.split(' ')

        self.turn = 'white' if len(moves) % 2 == 0 else 'black'

        i = 0
        for move in moves:
            if ind is not None and i == ind:
                break

            i += 1

            if move[0] == 'E':
                # En passant move
                from_pos = move[1] + move[2]
                to_pos = move[3] + move[4]

                self.table[to_pos[0]][to_pos[1]] = self.table[from_pos[0]][from_pos[1]]
                self.table[from_pos[0]][from_pos[1]] = None
                self.table[from_pos[0]][to_pos[1]] = None  # remove the capture pawn in En Passant move

            elif move[0] == 'P':
                # breakpoint()
                # Pawn Promotion move
                from_row, from_col = move[1], move[2]
                to_row, to_col = move[3], move[4]
                self.make_move(from_row, from_col, to_row, to_col, move[-1])

            elif move[0] == 'C':
                from_row, from_col = move[1], move[2]
                to_row, to_col = move[3], move[4]
                castling = None
                if to_col == 'g':
                    castling = 'K'
                elif to_col == 'c':
                    castling = 'Q'
                self.make_move(from_row, from_col, to_row, to_col, castling=castling)

            else:
                # Regular move
                from_pos = move[0] + move[1]
                to_pos = move[2] + move[3]

                self.table[to_pos[0]][to_pos[1]] = self.table[from_pos[0]][from_pos[1]]
                self.table[from_pos[0]][from_pos[1]] = None

    def new_table(self):
        self.turn = 'white'

        self.table = {
            '8': {'a': Rook('black'), 'b': Knight('black'), 'c': Bishop('black'), 'd': Queen('black'), 'e': King('black'), 'f': Bishop('black'), 'g': Knight('black'), 'h': Rook('black')},
            '7': {'a': Pawn('black'), 'b': Pawn('black'), 'c': Pawn('black'), 'd': Pawn('black'), 'e': Pawn('black'), 'f': Pawn('black'), 'g': Pawn('black'), 'h': Pawn('black')},
            '6': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '5': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '4': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '3': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '2': {'a': Pawn('white'), 'b': Pawn('white'), 'c': Pawn('white'), 'd': Pawn('white'), 'e': Pawn('white'), 'f': Pawn('white'), 'g': Pawn('white'), 'h': Pawn('white')},
            '1': {'a': Rook('white'), 'b': Knight('white'), 'c': Bishop('white'), 'd': Queen('white'), 'e': King('white'), 'f': Bishop('white'), 'g': Knight('white'), 'h': Rook('white')},
        }

        # self.pp_table()

    def pp_table(self):
        self.table = {
            '8': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '7': {'a': Pawn('white'), 'b': Pawn('white'), 'c': Pawn('white'), 'd': Pawn('white'), 'e': Pawn('white'),
                  'f': Pawn('white'), 'g': Pawn('white'), 'h': Pawn('white')},
            '6': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '5': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '4': {'a': None, 'b': King('white'), 'c': None, 'd': None, 'e': None, 'f': King('black'), 'g': None, 'h': None},
            '3': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '2': {'a': Pawn('black'), 'b': Pawn('black'), 'c': Pawn('black'), 'd': Pawn('black'), 'e': Pawn('black'),
                  'f': Pawn('black'), 'g': Pawn('black'), 'h': Pawn('black')},
            '1': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
        }

    def cc_table(self):
        self.table = {
            '8': {'a': Rook('black'), 'b': None, 'c': None, 'd': None, 'e': King('black'), 'f': None, 'g': None, 'h': Rook('black')},
            '7': {'a': Pawn('black'), 'b': Pawn('black'), 'c': Pawn('black'), 'd': Pawn('black'), 'e': Pawn('black'), 'f': Pawn('black'), 'g': Pawn('black'), 'h': Pawn('black')},
            '6': {'a': Knight('black'), 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '5': {'a': Queen('black'), 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '4': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '3': {'a': Queen('white'), 'b': Knight('white'), 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '2': {'a': Pawn('white'), 'b': Pawn('white'), 'c': Pawn('white'), 'd': Pawn('white'), 'e': Pawn('white'), 'f': Pawn('white'), 'g': Pawn('white'), 'h': Pawn('white')},
            '1': {'a': Rook('white'), 'b': None, 'c': None, 'd': None, 'e': King('white'), 'f': None, 'g': None, 'h': Rook('white')},
        }

    def stalemate_table(self):
        self.table = {
            '8': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '7': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '6': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '5': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '4': {'a': None, 'b': King('white'), 'c': None, 'd': None, 'e': None, 'f': King('black'), 'g': None,
                  'h': None},
            '3': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '2': {'a': Pawn('black'), 'b': Pawn('black'), 'c': Pawn('black'), 'd': Pawn('black'),
                  'e': Pawn('black'),
                  'f': Pawn('black'), 'g': Pawn('black'), 'h': Pawn('black')},
            '1': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
        }

    def get_json_table(self):
        json_table = {
            '8': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '7': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '6': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '5': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '4': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '3': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '2': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
            '1': {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None},
        }
        # breakpoint()
        for row_key in self.table.keys():
            for col_key in self.table[row_key].keys():
                json_table[row_key][col_key] = self.table[row_key][col_key].__str__()

        return json_table

    def render(self, context):
        template = loader.get_template(self.template_name)
        context['board'] = self
        html_table = template.render(context)
        return html_table

    def get_piece(self, row, col):
        return self.table[row][col]

    def __str__(self):
        return str(self.table)

    def is_king_in_check(self, king_color):
        king_position = self.find_king(king_color)
        if not king_position:
            return False

        king_row, king_col = king_position[0], king_position[1]
        opponent_color = 'white' if king_color == 'black' else 'black'

        directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),  # rook-like moves
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # bishop-like moves
        ]

        # check for attacks from Rook, Bishop, and Queen
        for direction in directions:
            row_offset, col_offset = direction
            row, col = int(king_row), king_col

            while True:
                row += row_offset
                col = chr(ord(col) + col_offset)

                if Piece.outOfBounds(str(row), col):
                    break

                piece = self.get_piece(str(row), col)

                if piece:
                    if piece.get_color() == opponent_color and (
                            (abs(row_offset) == abs(col_offset) and isinstance(piece, (Bishop, Queen))) or
                            ((row_offset == 0 or col_offset == 0) and isinstance(piece, (Rook, Queen)))
                    ):
                        return True
                    break

        # check for attacks from Knight
        knight_moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]

        for move in knight_moves:
            row = str(int(king_row) + move[0])
            col = chr(ord(king_col) + move[1])

            if not Piece.outOfBounds(str(row), col):
                piece = self.get_piece(row, col)
                if piece and piece.get_color() == opponent_color and isinstance(piece, Knight):
                    return True

        # check for attacks from Pawn
        pawn_direction = -1 if king_color == 'black' else 1
        for col_offset in [-1, 1]:
            row = str(int(king_row) + pawn_direction)
            col = chr(ord(king_col) + col_offset)

            if not Piece.outOfBounds(row, col):
                piece = self.get_piece(row, col)
                if piece and piece.get_color() == opponent_color and isinstance(piece, Pawn):
                    return True

        return False

    def find_king(self, color):
        for row in self.table:
            for col in self.table[row]:
                piece = self.get_piece(row, col)
                if piece and piece.__str__() == f'{color[0]}K':
                    return row + col

        return None

    def promote_pawn(self, row, col, promotion_choice):
        color = self.table[row][col].get_color()
        if promotion_choice == 'Q':
            self.table[row][col] = Queen(color)
        elif promotion_choice == 'R':
            self.table[row][col] = Rook(color)
        elif promotion_choice == 'B':
            self.table[row][col] = Bishop(color)
        elif promotion_choice == 'N':
            self.table[row][col] = Knight(color)
        else:
            raise ValueError("Invalid promotion choice")


    def make_move(self, from_row, from_col, to_row, to_col, promotion=None, castling=None):
        # breakpoint()
        if not castling:
            piece = self.table[from_row][from_col]
            captured_piece = self.table[to_row][to_col]
            self.table[to_row][to_col] = piece
            self.table[from_row][from_col] = None

            # handle and validate pawn promotion
            if isinstance(piece, Pawn):
                promotion_row = '8' if piece.get_color() == 'white' else '1'
                if to_row == promotion_row:
                    if promotion:
                        self.promote_pawn(to_row, to_col, promotion)

            return piece, captured_piece
        else:
            # breakpoint()
            king_piece = self.table[from_row][from_col]
            if isinstance(king_piece, King):
                rook = None
                if castling == 'K':
                    rook = self.table[from_row]['h']
                    self.table[from_row]['h'] = None
                    self.table[from_row][from_col] = None
                    self.table[from_row]['f'] = rook
                    self.table[from_row]['g'] = king_piece
                    self.kings_moved[king_piece.get_color()] = True
                    self.rooks_moved[from_row + from_col] = True

                elif castling == 'Q':
                    rook = self.table[from_row]['a']
                    self.table[from_row]['a'] = None
                    self.table[from_row][from_col] = None
                    self.table[from_row]['d'] = rook
                    self.table[from_row]['c'] = king_piece
                    self.kings_moved[king_piece.get_color()] = True
                    self.rooks_moved[from_row + from_col] = True

                return king_piece, rook
            else:
                print("You have tried to castle but not with the king")

    def undo_move(self, from_row, from_col, to_row, to_col, captured_piece):
        piece = self.table[to_row][to_col]
        self.table[from_row][from_col] = piece
        self.table[to_row][to_col] = captured_piece

    def is_valid_move(self, from_row, from_col, to_row, to_col):
        piece, captured_piece = self.make_move(from_row, from_col, to_row, to_col)
        king_in_check = self.is_king_in_check(piece.get_color())
        self.undo_move(from_row, from_col, to_row, to_col, captured_piece)
        return not king_in_check

    def can_castle_kingside(self, color):
        row = '1' if color == 'white' else '8'
        rook_pos = row + 'h'

        if self.kings_moved[color] or self.rooks_moved[rook_pos] or self.table[row]['f'] or self.table[row]['g']:
            return False

        # Check if squares are under attack
        if self.is_under_attack(row, 'e', color) or self.is_under_attack(row, 'f', color) or self.is_under_attack(row, 'g', color):
            return False
        return True

    def can_castle_queenside(self, color):
        row = '1' if color == 'white' else '8'
        rook_pos = row + 'a'

        if self.kings_moved[color] or self.rooks_moved[rook_pos] or self.table[row]['b'] or self.table[row]['c'] or self.table[row]['d']:
            return False

        # Check if squares are under attack
        if self.is_under_attack(row, 'e', color) or self.is_under_attack(row, 'd', color) or self.is_under_attack(row, 'c', color):
            return False
        return True

    def is_under_attack(self, row, col, color):
        king_position = self.find_king(color)
        if king_position == row + col:
            if self.is_king_in_check(color):
                return True
        else:
            # make temporary move
            self.table[row][col] = self.table[king_position[0]][king_position[1]]
            self.table[king_position[0]][king_position[1]] = None
            if self.is_king_in_check(color):
                # undo move
                self.table[king_position[0]][king_position[1]] = self.table[row][col]
                self.table[row][col] = None
                return True
            # undo move
            self.table[king_position[0]][king_position[1]] = self.table[row][col]
            self.table[row][col] = None
