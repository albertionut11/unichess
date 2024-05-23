from .Board import Board


class Play:
    def __init__(self, state):
        if state is None:
            self.board = Board()
            self.board.new_table()
        else:
            self.board = Board()
            self.board.load_table(state)


