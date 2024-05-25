from .Board import Board


class Play:
    def __init__(self, data):
        self.board = Board()
        self.data = data

        if self.data == '':
            self.board.new_table()
        else:
            self.board.load_table(self.data)

    def getAvailableMoves(self, from_row, from_col):
        moves = []
        for row in self.board.table.keys():
            for col in self.board.table[row].keys():
                pos = row + col
                moves.append(pos)

        print(moves)
        return moves
