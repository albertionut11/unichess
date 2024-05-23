from django.template import loader


class Player:
    def __init__(self, name):
        self.name = name
        self.pieces = list()


class Board:
    def __init__(self):
        print('Board.__init__')
        self.table = dict()
        self.data = None
        self.players = dict()
        self.players['white'] = Player('white')
        self.players['black'] = Player('black')
        self.template_name = 'games/table.html'
        self.light_color = 'F5DEB3'
        self.dark_color = 'a1764b'

    def load_table(self, data):
        self.new_table()
        moves = data.split(' ')[:-1]

        for move in moves:
            from_pos = move[0] + move[1]
            to_pos = move[2] + move[3]

            self.table[to_pos[0]][to_pos[1]] = self.table[from_pos[0]][from_pos[1]]
            self.table[from_pos[0]][from_pos[1]] = '.'


    def new_table(self):
        whites = Player('white')
        self.players['white'] = whites
        blacks = Player('black')
        self.players['black'] = blacks

        self.table = {
            '8': {'a': 'bR', 'b': 'bN', 'c': 'bB', 'd': 'bQ', 'e': 'bK', 'f': 'bB', 'g': 'bN', 'h': 'bR'},
            '7': {'a': 'bP', 'b': 'bP', 'c': 'bP', 'd': 'bP', 'e': 'bP', 'f': 'bP', 'g': 'bP', 'h': 'bP'},
            '6': {'a': '.', 'b': '.', 'c': '.', 'd': '.', 'e': '.', 'f': '.', 'g': '.', 'h': '.'},
            '5': {'a': '.', 'b': '.', 'c': '.', 'd': '.', 'e': '.', 'f': '.', 'g': '.', 'h': '.'},
            '4': {'a': '.', 'b': '.', 'c': '.', 'd': '.', 'e': '.', 'f': '.', 'g': '.', 'h': '.'},
            '3': {'a': '.', 'b': '.', 'c': '.', 'd': '.', 'e': '.', 'f': '.', 'g': '.', 'h': '.'},
            '2': {'a': 'wP', 'b': 'wP', 'c': 'wP', 'd': 'wP', 'e': 'wP', 'f': 'wP', 'g': 'wP', 'h': 'wP'},
            '1': {'a': 'wR', 'b': 'wN', 'c': 'wB', 'd': 'wQ', 'e': 'wK', 'f': 'wB', 'g': 'wN', 'h': 'wR'},
        }

    def render(self, context):
        template = loader.get_template(self.template_name)
        context['board'] = self
        print('Board context:', context)
        print('Template:', template, self.template_name)
        html_table = template.render(context)
        return html_table
