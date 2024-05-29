from .Board import Board


class Play:
    def __init__(self, data):
        self.board = Board()
        self.data = data
        self.checkmate = None

        if self.data == '':
            self.board.new_table()
        else:
            self.board.load_table(self.data)
            if self.is_checkmate("white"):
                self.checkmate = "Black"
            elif self.is_checkmate("black"):
                self.checkmate = "White"

    def getMoves(self, from_row, from_col):
        # breakpoint()
        piece = self.board.get_piece(from_row, from_col)
        if piece:
            return piece.getSafeMoves(self.board, from_row, from_col)
        else:
            print("We should never be here")
        return None, None, None

    def is_checkmate(self, color):
        for row in self.board.table:
            for col in self.board.table[row]:
                piece = self.board.get_piece(row, col)
                if piece and piece.get_color() == color:
                    moves, _, _ = piece.getSafeMoves(self.board, row, col)
                    if moves:
                        # print(piece.__str__, row, col, moves)
                        return False
        return True if self.board.is_king_in_check(color) else False

    def getAllMoves(self):
        moves = []
        for row in self.board.table.keys():
            for col in self.board.table[row].keys():
                pos = row + col
                moves.append(pos)

        # print(moves)
        return moves, None