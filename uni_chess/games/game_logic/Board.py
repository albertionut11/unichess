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

    def load_table(self, data):
        self.new_table()
        self.data = data
        moves = data.split(' ')[:-1]

        self.turn = 'white' if len(moves) % 2 == 0 else 'black'

        for move in moves:
            # if not En Passant move
            if move[0] != 'E':
                from_pos = move[0] + move[1]
                to_pos = move[2] + move[3]

                self.table[to_pos[0]][to_pos[1]] = self.table[from_pos[0]][from_pos[1]]
                self.table[from_pos[0]][from_pos[1]] = None
            else:
                # En passant move
                from_pos = move[1] + move[2]
                to_pos = move[3] + move[4]

                self.table[to_pos[0]][to_pos[1]] = self.table[from_pos[0]][from_pos[1]]
                self.table[from_pos[0]][from_pos[1]] = None
                self.table[from_pos[0]][to_pos[1]] = None  # remove the capture pawn in En Passant move

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

            if Piece.outOfBounds(str(row), col):
                break

            piece = self.get_piece(row, col)
            if piece and piece.get_color() == opponent_color and isinstance(piece, Knight):
                return True

        # check for attacks from Pawn
        pawn_direction = -1 if king_color == 'black' else +1 # changed here consider this in case of bugs
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

    def make_move(self, from_row, from_col, to_row, to_col):
        piece = self.table[from_row][from_col]
        captured_piece = self.table[to_row][to_col]
        self.table[to_row][to_col] = piece
        self.table[from_row][from_col] = None
        return piece, captured_piece

    def undo_move(self, from_row, from_col, to_row, to_col, captured_piece):
        piece = self.table[to_row][to_col]
        self.table[from_row][from_col] = piece
        self.table[to_row][to_col] = captured_piece

    def is_valid_move(self, from_row, from_col, to_row, to_col):
        piece, captured_piece = self.make_move(from_row, from_col, to_row, to_col)
        king_in_check = self.is_king_in_check(piece.get_color())
        self.undo_move(from_row, from_col, to_row, to_col, captured_piece)
        return not king_in_check
