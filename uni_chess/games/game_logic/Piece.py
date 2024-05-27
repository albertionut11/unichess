class Piece:
    def __init__(self, color):
        self.color = color

    def getAvailableMoves(self, board, from_row, from_col):
        raise NotImplementedError("This method should be overridden by subclasses")

    def __str__(self):
        raise NotImplementedError("This method should be overridden by subclasses")

    def get_color(self):
        return self.color

    @staticmethod
    def outOfBounds(row, col):
        row = int(row)
        if row < 1 or 8 < row:
            return True

        # out of bounds col
        if col < 'a' or 'h' < col:
            return True

        return False

    @staticmethod
    def getPiece(board, row, col):
        piece = board.get_piece(row, col)
        return piece

    def getSafeMoves(self, board, from_row, from_col):
        all_moves, enPassantPos = self.getAvailableMoves(board, from_row, from_col)
        safe_moves = []
        for move in all_moves:
            to_row, to_col = move[0], move[1]
            if board.is_valid_move(from_row, from_col, to_row, to_col):
                safe_moves.append(move)
        return safe_moves, enPassantPos


class King(Piece):
    def getAvailableMoves(self, board, from_row, from_col):
        directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        moves = []
        for direction in directions:
            to_row = str(int(from_row) + direction[0])
            to_col = chr(ord(from_col) + direction[1])
            if not self.outOfBounds(to_row, to_col):
                piece = board.get_piece(to_row, to_col)
                if not piece or piece.get_color() != self.color:
                    moves.append(to_row + to_col)
        return moves, None

    def __str__(self):
        return f'{self.color[0]}K'


class Queen(Piece):
    def getAvailableMoves(self, board, from_row, from_col):
        moves = []
        rook = Rook(Piece)
        bishop = Bishop(Piece)
        RookMoves = rook.getAvailableMoves(board, from_row, from_col)
        BishopMoves = bishop.getAvailableMoves(board, from_row, from_col)

        moves = RookMoves[0] + BishopMoves[0]

        return moves, None

    def __str__(self):
        return f'{self.color[0]}Q'


class Rook(Piece):

    def __str__(self):
        return f'{self.color[0]}R'

    def getAvailableMoves(self, board, from_row, from_col):
        moves = []

        # up
        up_row = str(int(from_row) + 1)
        while up_row <= '8':
            piece = self.getPiece(board, up_row, from_col)
            if piece:
                if piece.get_color() != self.color:
                    moves.append(up_row + from_col)
                break
            else:
                moves.append(up_row + from_col)
                up_row = str(int(up_row) + 1)

        # down
        down_row = str(int(from_row) - 1)
        while down_row >= '1':
            piece = self.getPiece(board, down_row, from_col)
            if piece:
                if piece.get_color() != self.color:
                    moves.append(down_row + from_col)
                break
            else:
                moves.append(down_row + from_col)
                down_row = str(int(down_row) - 1)

        # left
        left_col = chr(ord(from_col) - 1)
        while left_col >= 'a':
            piece = self.getPiece(board, from_row, left_col)
            if piece:
                if piece.get_color() != self.color:
                    moves.append(from_row + left_col)
                break
            else:
                moves.append(from_row + left_col)
                left_col = chr(ord(left_col) - 1)

        # right
        right_col = chr(ord(from_col) + 1)
        while right_col <= 'h':
            piece = self.getPiece(board, from_row, right_col)
            if piece:
                if piece.get_color() != self.color:
                    moves.append(from_row + right_col)
                break
            else:
                moves.append(from_row + right_col)
                right_col = chr(ord(right_col) + 1)

        return moves, None


class Knight(Piece):

    def __str__(self):
        return f'{self.color[0]}N'

    def getAvailableMoves(self, board, from_row, from_col):
        moves = []
        # breakpoint()
        # 2 up 1 left-right
        up_row = str(int(from_row) + 2)
        left_col = chr(ord(from_col) - 1)
        right_col = chr(ord(from_col) + 1)

        if not self.outOfBounds(up_row, left_col) and self.isValidKnightMove(board, up_row, left_col):
            moves.append(up_row + left_col)

        if not self.outOfBounds(up_row, right_col) and self.isValidKnightMove(board, up_row, right_col):
            moves.append(up_row + right_col)

        # 2 down 1 left-right
        down_row = str(int(from_row) - 2)

        if not self.outOfBounds(down_row, left_col) and self.isValidKnightMove(board, down_row, left_col):
            moves.append(down_row + left_col)

        if not self.outOfBounds(down_row, right_col) and self.isValidKnightMove(board, down_row, right_col):
            moves.append(down_row + right_col)

        # 2 left 1 up-down
        left_col = chr(ord(from_col) - 2)
        up_row = str(int(from_row) + 1)
        down_row = str(int(from_row) - 1)

        if not self.outOfBounds(up_row, left_col) and self.isValidKnightMove(board, up_row, left_col):
            moves.append(up_row + left_col)

        if not self.outOfBounds(down_row, left_col) and self.isValidKnightMove(board, down_row, left_col):
            moves.append(down_row + left_col)

        # 2 right 1 up-down
        right_col = chr(ord(from_col) + 2)

        if not self.outOfBounds(up_row, right_col) and self.isValidKnightMove(board, up_row, right_col):
            moves.append(up_row + right_col)

        if not self.outOfBounds(down_row, right_col) and self.isValidKnightMove(board, down_row, right_col):
            moves.append(down_row + right_col)

        return moves, None

    def isValidKnightMove(self, board, row, col):
        piece = self.getPiece(board, row, col)
        if piece:
            if piece.get_color() == self.color:
                return False

        return True

class Bishop(Piece):

    def __str__(self):
        return f'{self.color[0]}B'

    def getAvailableMoves(self, board, from_row, from_col):
        moves = []
        # breakpoint()
        # down left
        row = str(int(from_row) - 1)
        col = chr(ord(from_col) - 1)

        while row >= '1' and col >= 'a':
            piece = self.getPiece(board, row, col)
            if piece:
                if piece.get_color() != self.color:
                    moves.append(row + col)
                break
            else:
                moves.append(row + col)
                row = str(int(row) - 1)
                col = chr(ord(col) - 1)

        # up left
        row = str(int(from_row) + 1)
        col = chr(ord(from_col) - 1)

        while row <= '8' and col >= 'a':
            piece = self.getPiece(board, row, col)
            if piece:
                if piece.get_color() != self.color:
                    moves.append(row + col)
                break
            else:
                moves.append(row + col)
                row = str(int(row) + 1)
                col = chr(ord(col) - 1)

        # down right
        row = str(int(from_row) - 1)
        col = chr(ord(from_col) + 1)

        while row >= '1' and col <= 'h':
            piece = self.getPiece(board, row, col)
            if piece:
                if piece.get_color() != self.color:
                    moves.append(row + col)
                break
            else:
                moves.append(row + col)
                row = str(int(row) - 1)
                col = chr(ord(col) + 1)

        # up right
        row = str(int(from_row) + 1)
        col = chr(ord(from_col) + 1)

        while row <= '8' and col <= 'h':
            piece = self.getPiece(board, row, col)
            if piece:
                if piece.get_color() != self.color:
                    moves.append(row + col)
                break
            else:
                moves.append(row + col)
                row = str(int(row) + 1)
                col = chr(ord(col) + 1)

        return moves, None


class Pawn(Piece):

    def __str__(self):
        return f'{self.color[0]}P'

    def getAvailableMoves(self, board, from_row, from_col):
        # breakpoint()
        moves = []
        side = self.get_color()
        direction = 1 if side == 'white' else -1

        # starting moves -> pawn can move two squares at the beginning of the game
        next_row_1 = str(int(from_row) + direction * 1)
        if self.isValidMove(board, next_row_1, from_col, True):
            move_1 = next_row_1 + from_col
            moves.append(move_1)

            # second square
            if (side == 'white' and from_row == '2') or (side == 'black' and from_row == '7'):
                next_row_2 = str(int(from_row) + direction * 2)
                if self.isValidMove(board, next_row_2, from_col, True):
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

        return moves, enPassantPos

    def isValidMove(self, board, from_row, from_col, forwardMove=False):
        # breakpoint()
        # out of bounds check
        if self.outOfBounds(from_row, from_col):
            return False

        # check for piece in following square, if we have piece but forward move -> False, if now forward move -> True
        piece = board.get_piece(from_row, from_col)
        if forwardMove:
            if piece:
                return False

        return True

    def opponentDiagonalPositions(self, board, from_row, from_col, side):
        direction = 1 if side == 'white' else -1
        diagRow_1, diagCol_1 = str(int(from_row) + direction * 1), chr(ord(from_col) + 1)
        diagRow_2, diagCol_2 = str(int(from_row) + direction * 1), chr(ord(from_col) - 1)
        # breakpoint()
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
