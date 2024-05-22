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

    def load_table(self):
        self.new_table()

    def new_table(self):
        whites = Player('white')
        self.players['white'] = whites
        blacks = Player('black')
        self.players['black'] = blacks

        self.table = {
            '8': {'a': '.', 'b': '.', 'c': '.', 'd': '.', 'e': '.', 'f': '.', 'g': '.', 'h': '.'},
            '7': {'a': '.', 'b': '.', 'c': '.', 'd': '.', 'e': '.', 'f': '.', 'g': '.', 'h': '.'},
            '6': {'a': '.', 'b': '.', 'c': '.', 'd': '.', 'e': '.', 'f': '.', 'g': '.', 'h': '.'},
            '5': {'a': '.', 'b': '.', 'c': '.', 'd': '.', 'e': '.', 'f': '.', 'g': '.', 'h': '.'},
            '4': {'a': '.', 'b': '.', 'c': '.', 'd': '.', 'e': '.', 'f': '.', 'g': '.', 'h': '.'},
            '3': {'a': '.', 'b': '.', 'c': '.', 'd': '.', 'e': '.', 'f': '.', 'g': '.', 'h': '.'},
            '2': {'a': '.', 'b': '.', 'c': '.', 'd': '.', 'e': '.', 'f': '.', 'g': '.', 'h': '.'},
            '1': {'a': '.', 'b': '.', 'c': '.', 'd': '.', 'e': '.', 'f': '.', 'g': '.', 'h': '.'},
        }

    def render(self, context):
        template = loader.get_template(self.template_name)
        context['board'] = self
        print('Board context:', context)
        print('Template:', template, self.template_name)
        html_table = template.render(context)
        return html_table
