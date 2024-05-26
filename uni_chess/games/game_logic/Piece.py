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

    def __str__(self):
        return f'{self.color[0]}P'

    def getAvailableMoves(self, board, from_row, from_col):

        moves = []
        side = self.get_color()
        direction = 1 if side == 'white' else -1

        # starting moves -> pawn can move two squares at the beginning of the game
        next_row_1 = str(int(from_row) + direction * 1)
        if self.isValidMove(board, next_row_1, from_col):
            move_1 = next_row_1 + from_col
            moves.append(move_1)

            # second square
            if (side == 'white' and from_row == '2') or (side == 'black' and from_col == '7'):
                next_row_2 = str(int(from_row) + direction * 2)
                if self.isValidMove(board, next_row_2, from_col):
                    move_2 = next_row_2 + from_col
                    moves.append(move_2)

        # capture moves -> pawn can move diagonally if he can capture a piece
        diagPositions = self.opponentDiagonalPositions(board, from_row, from_col, side)
        if len(diagPositions) > 0:
            for pos in diagPositions:
                moves.append(pos)

        # en passant -> pawn can also da en passant for some reason
        enPassantPos = self.checkEnPassant(board, from_row, from_col, side)
        if enPassantPos:
            moves.append(enPassantPos)

        return moves


    @staticmethod
    def isValidMove(board, from_row, from_col):
        # piece ahead of us
        piece = board.get_piece(from_row, from_col)
        if piece:
            return False

        # out of bounds row
        if '1' > from_row > '8':
            return False

        # out of bounds col
        if 'a' > from_col > 'h':
            return False

        return True

    def opponentDiagonalPositions(self, board, from_row, from_col, side):
        direction = 1 if side == 'white' else -1
        diagRow_1, diagCol_1 = str(int(from_row) + direction * 1), chr(ord(from_col) + 1)
        diagRow_2, diagCol_2 = str(int(from_row) + direction * 1), chr(ord(from_col) - 1)

        positions = []

        if self.isValidMove(board, diagRow_1, diagCol_1):
            diagPiece_1 = board.get_piece(diagRow_1, diagCol_1)

            if diagPiece_1:
                if side != diagPiece_1.get_color():
                    pos = diagRow_1 + diagCol_1
                    positions.append(pos)

        if self.isValidMove(board, diagRow_2, diagCol_2):
            diagPiece_2 = board.get_piece(diagRow_2, diagCol_2)

            if diagPiece_2:
                if side != diagPiece_2.get_color():
                    pos = diagRow_2 + diagCol_2
                    positions.append(pos)

        return positions

    @staticmethod
    def checkEnPassant(board, from_row, from_col, side):
        if (side == 'white' and from_row == '5') or (side == 'black' and from_row == '4'):
            vecinCol_1 = chr(ord(from_col) + 1) if chr(ord(from_col) + 1) <= 'h' else None
            vecinCol_2 = chr(ord(from_col) - 1) if chr(ord(from_col) - 1) >= 'a' else None
            lastMove = board.data.split(' ')[-2]

            if vecinCol_1:
                piece = board.get_piece(from_row, vecinCol_1)
                if side == 'white' and piece.__str__() == 'bP':
                    expMove = f'7{vecinCol_1}5{vecinCol_1}'
                    if lastMove == expMove:
                        return str(int(from_row) + 1) + vecinCol_1

                elif side == 'black' and piece.__str__() == 'wP':
                    expMove = f'2{vecinCol_1}4{vecinCol_1}'
                    if lastMove == expMove:
                        return str(int(from_row) - 1) + vecinCol_1

            if vecinCol_2:
                piece = board.get_piece(from_row, vecinCol_2)
                if side == 'white' and piece.__str__() == 'bP':
                    expMove = f'7{vecinCol_2}5{vecinCol_2}'
                    if lastMove == expMove:
                        return str(int(from_row) + 1) + vecinCol_2

                elif side == 'black' and piece.__str__() == 'wP':
                    expMove = f'2{vecinCol_2}4{vecinCol_2}'
                    if lastMove == expMove:
                        return str(int(from_row - 1)) + vecinCol_2

        return None
