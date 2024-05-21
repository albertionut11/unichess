from .Board import Board


class Chess:
    def __init__(self):
        self.board = Board()
        self.board.load_table()



