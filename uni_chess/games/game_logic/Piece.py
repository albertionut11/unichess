class Piece:
    def __init__(self, color):
        self.color = color

    def getAvailableMoves(self, board, from_row, from_col):
        raise NotImplementedError("This method should be overridden by subclasses")

    def __str__(self):
        raise NotImplementedError("This method should be overridden by subclasses")

    def get_color(self):
        return self.color


class King(Piece):
    def getAvailableMoves(self, board, from_row, from_col):
        # Implement the logic to get available moves for the King
        pass

    def __str__(self):
        return f'{self.color[0]}K'


class Queen(Piece):
    def getAvailableMoves(self, board, from_row, from_col):
        # Implement the logic to get available moves for the Queen
        pass

    def __str__(self):
        return f'{self.color[0]}Q'


class Bishop(Piece):
    def getAvailableMoves(self, board, from_row, from_col):
        # Implement the logic to get available moves for the Bishop
        pass

    def __str__(self):
        return f'{self.color[0]}B'


class Knight(Piece):
    def getAvailableMoves(self, board, from_row, from_col):
        # Implement the logic to get available moves for the Knight
        pass

    def __str__(self):
        return f'{self.color[0]}N'


class Rook(Piece):
    def getAvailableMoves(self, board, from_row, from_col):
        # Implement the logic to get available moves for the Rook
        pass

    def __str__(self):
        return f'{self.color[0]}R'


class Pawn(Piece):
    def getAvailableMoves(self, board, from_row, from_col):
        # Implement the logic to get available moves for the Pawn
        pass

    def __str__(self):
        return f'{self.color[0]}P'
