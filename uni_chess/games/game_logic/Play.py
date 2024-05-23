from django.shortcuts import get_object_or_404

from .Board import Board
from ..models import Game

class Play:
    def __init__(self, data):
        self.board = Board()
        self.data = data

        if self.data == '':
            self.board.new_table()
        else:
            self.board.load_table(self.data)


