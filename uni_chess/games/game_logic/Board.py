from django.template import loader
from .Piece import King, Queen, Bishop, Knight, Rook, Pawn

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
        moves = data.split(' ')[:-1]

        self.turn = 'white' if len(moves) % 2 == 0 else 'black'

        for move in moves:
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

    def render(self, context):
        template = loader.get_template(self.template_name)
        context['board'] = self
        html_table = template.render(context)
        return html_table

    def get_piece(self, row, col):
        return self.table[row][col]

    def __str__(self):
        return self.table

