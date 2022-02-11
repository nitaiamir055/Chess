"""
this class is responsible for storing the data on the game state , and also it will determine
    whether the moves valid or not.
"""
import re
from Chess.ErrorHandel import *


class GameState:
    def __init__(self):
        # the board game is 8*8 2 lists,
        # the first letter of each piece is the color "w" - white "b" - black ,
        # the second is the piece type (Rook, Knight, Bishop, Queen, King, Pawn)
        # blank place represent as "--"
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.piecesValidation = {"R": self.validRookMoves, "N": self.validKnightMoves,
                                 "P": self.validPawnMoves, "B": self.validBishopMoves,
                                 "Q": self.validQueenMoves, "K": self.validKingMoves}

        self.isWhiteMove = True  # for know who's turn
        self.gameOver = False  # checkmate flag
        self.move_log = []  # for moves history

        self.black_king_place = [0, 4]
        self.white_king_place = [7, 4]

        self.protectors = []
        self.threats = []

    def makeMove(self, move):
        # castling is the only move where the moved and the capture are the same color
        if move.piece_moved[0] == move.piece_capture[0]:
            if move.piece_moved[1] == 'K':
                self.makeCastlingMove(move)
        # en passant is the only move where the pawn move diagonal to empty square
        elif move.piece_moved[1] == 'P' and not move.end_col == move.start_col and move.piece_capture == "--":
            self.makeEnPassantMove(move)
        else:
            self.board[move.start_row][move.start_col] = "--"
            self.board[move.end_row][move.end_col] = move.piece_moved

        # king position:
        for i in range(0, 8):
            for j in range(0, 8):
                if self.board[i][j] == "wK":
                    self.white_king_place = (i, j)
                elif self.board[i][j] == "bK":
                    self.black_king_place = (i, j)

        self.move_log.append(move)  # add to history
        self.isWhiteMove = not self.isWhiteMove  # changing players

    def makeCastlingMove(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = "--"
        # left castling
        if move.end_col == 0:
            self.board[move.start_row][move.start_col - 2] = move.piece_moved
            self.board[move.start_row][move.start_col - 1] = move.piece_capture
        # right castling
        else:
            self.board[move.start_row][move.start_col + 2] = move.piece_moved
            self.board[move.start_row][move.start_col + 1] = move.piece_capture

    def makeEnPassantMove(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        if self.isWhiteMove:
            self.board[move.end_row + 1][move.end_col] = "--"
        else:
            self.board[move.end_row - 1][move.end_col] = "--"

    def undoMove(self):
        if len(self.move_log) != 0:
            last = self.move_log.pop()
            # castling undo
            if last.piece_moved[0] == last.piece_capture[0]:
                if last.end_col > last.start_col:
                    for i in range(last.start_col, last.end_col):
                        self.board[last.end_row][i] = "--"
                else:
                    for i in range(last.end_col, last.start_col):
                        self.board[last.end_row][i] = "--"

                self.board[last.end_row][last.end_col] = last.piece_capture
                self.board[last.start_row][last.start_col] = last.piece_moved

            # en-passant undo
            elif last.piece_moved[1] == 'P' and last.piece_capture[1] == '-' and abs(last.start_col - last.end_col) == 1:
                self.board[last.start_row][last.start_col] = last.piece_moved
                self.board[last.end_row][last.end_col] = "--"
                if self.isWhiteMove:  # if it eaten a white pawn , than the forward is row down
                    self.board[last.end_row - 1][last.end_col] = "wP"
                else:  # if it eaten a black pawn , than the forward is row up
                    self.board[last.end_row + 1][last.end_col] = "bP"

            # non-special move undo
            else:
                self.board[last.end_row][last.end_col] = last.piece_capture
                self.board[last.start_row][last.start_col] = last.piece_moved

            self.gameOver = False
            self.isWhiteMove = not self.isWhiteMove
        else:
            raise NoUndo("No move to undo.")

    def matchTurnPiece(self, move):
        if move.piece_moved[0] == 'b' and not self.isWhiteMove:
            return True
        elif move.piece_moved[0] == 'w' and self.isWhiteMove:
            return True
        return False

    def getValidMoves(self):
        if self.isWhiteMove:
            k_r, k_c = self.white_king_place
        else:
            k_r, k_c = self.black_king_place
        self.threats, self.protectors = self.lookForCheck(k_r, k_c)
        pieces_moves = self.getAllPossibleMoves()

        if len(self.threats) == 1:  # or blocking by another piece or move the king.
            square_valid = []
            d = self.threats[0][1]
            threat_pos = self.threats[0][0]
            for i in range(1, 8):
                row = k_r + d[0] * i
                col = k_c + d[1] * i
                square_valid.append((row, col))
                if (row, col) == threat_pos:
                    break

            for i in range(len(pieces_moves)-1, -1, -1):
                move = pieces_moves[i]
                move_pos = (move.end_row, move.end_col)
                if not((move_pos in square_valid) or (move.piece_moved[1] == 'K')):
                    pieces_moves.pop(i)

        elif len(self.threats) == 2:  # only the king can move
            for i in range(len(pieces_moves)-1, -1, -1):
                move = pieces_moves[i]
                if move.piece_moved[1] != 'K':
                    pieces_moves.remove(move)
        else:
            special_moves = self.specialMoves()
            pieces_moves.extend(special_moves)

        if len(pieces_moves) == 0:
            self.gameOver = True
        return pieces_moves

    def lookForCheck(self, k_r, k_c):
        """
        this method will search for threats on the king and protectors,
         - if there is a threat and it has a protector - save the protector loc and direction of threat ,
          but don't announce check.
         - if there is a threat without any protector , save the threat loc and direction of threat,
        :return: protector - [[loc of piece],[direction of threat]]
        """
        # declare the variables protector and threats
        protectors = []
        threats = []
        # first define enemy:
        if self.isWhiteMove:
            enemy = 'b'
            ally = 'w'
        else:
            enemy = 'w'
            ally = 'b'

        # create the king direction , and check threats and allies:
        king_d = [(0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, -1), (-1, 1)]

        for j, d in enumerate(king_d):
            temp_protector = []
            for i in range(1, 8):
                row = k_r + d[0] * i
                col = k_c + d[1] * i
                if 0 <= row <= 7 and 0 <= col <= 7:
                    piece = self.board[row][col][1]
                    color = self.board[row][col][0]

                    if color == ally:
                        temp_protector.append([(row, col), d])
                    elif color == enemy:
                        if (piece == 'P' and i == 1 and (
                                (ally == 'w' and 6 <= j <= 7) or (ally == 'b' and 4 <= j <= 5))) or \
                                (piece == 'B' and 4 <= j <= 7) or \
                                (piece == 'R' and 0 <= j <= 3) or \
                                (piece == 'Q'):
                            if len(temp_protector) == 0:
                                threats.append([(row, col), d])
                            elif len(temp_protector) == 1:
                                protectors.append(temp_protector[0])
                            else:  # more than two protectors
                                break
                        break  # an enemy piece that doesn't threats' me
                else:  # off board
                    break
        knight_moves = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (-2, 1), (2, -1), (-2, -1)]
        for m in knight_moves:
            row = k_r + m[0]
            col = k_c + m[1]
            if 0 <= row <= 7 and 0 <= col <= 7:
                color = self.board[row][col][0]
                piece = self.board[row][col][1]
                if piece == 'N' and color == enemy:
                    threats.append([(row, col), m])

        return threats, protectors

    # get all possible moves of the player, without consider check.
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                pieceColor = self.board[r][c][0]
                if (pieceColor == 'w' and self.isWhiteMove) or (pieceColor == 'b' and not self.isWhiteMove):
                    piece = self.board[r][c][1]
                    temp = self.piecesValidation[piece](r, c)
                    if temp:
                        moves.extend(temp)
        return moves

    def specialMoves(self):
        moves = []
        # castling
        moves.extend(self.castling())
        # en passant
        moves.extend(self.enPassant())

        return moves

    def castling(self):
        """
        castling move is a special move.
        the rook and the king move together. This move is valid with 4 conditions:
        the king not in chek, the swap will not make the king be in chek,
        the rook and the king didn't make a move from the beginning
        and the squares between the king and rook are empty.
        :return: list of valid castling moves list(Move)
        """
        moves = []

        king_place = [(7, 4), (0, 4)]
        rook_place = [[(7, 0), (7, 7)], [(0, 0), (0, 7)]]
        king_swap = [[(7, 2), (7, 6)], [(0, 2), (0, 6)]]
        castlingLeft = True
        castlingRight = True

        if self.isWhiteMove:
            king_place = king_place[0]
            rook_place = rook_place[0]
            king_swap = king_swap[0]
            color = 'w'
        else:
            king_place = king_place[1]
            rook_place = rook_place[1]
            king_swap = king_swap[1]
            color = 'b'

        # check if the squares between the king and the rooks are empty:
        for i in range(1, king_place[1]):
            if not self.board[king_place[0]][i] == "--":
                castlingLeft = False
                break
        for i in range(king_place[1] + 1, 7):
            if not self.board[king_place[0]][i] == "--":
                castlingRight = False
                break

        # if the king in chek the castling func will not been called,
        # now we check if the if the swap will make a chek
        threats, temp = self.lookForCheck(king_swap[0][0], king_swap[0][1])
        if len(threats) > 0:
            castlingLeft = False
        threats, temp = self.lookForCheck(king_swap[1][0], king_swap[1][1])
        if len(threats) > 0:
            castlingRight = False

        # check if the king of the rooks moved:
        for move in self.move_log:
            if move.piece_moved == color + "R":
                if rook_place[0] == (move.start_row, move.start_col):
                    castlingLeft = False
                if rook_place[1] == (move.start_row, move.start_col):
                    castlingLeft = False
                break
            if move.piece_moved == color + "K":
                castlingLeft = castlingRight = False

        if castlingLeft:
            moves.append(Move(king_place, rook_place[0], self.board))
        if castlingRight:
            moves.append(Move(king_place, rook_place[1], self.board))

        return moves

    def enPassant(self):
        """
        enPassant is move that valid in 4 condition:
        between two pawns
        the opponent pawn do 2 step in one move (first move)
        this move happened just after the move in the first cond
        your pawn was in the fifth row (with the opponent pawn)
        :return: move
        """
        moves = []
        my_pawn_place = [(1, 1), (1, -1)]
        enemy = 'w'
        if self.isWhiteMove:
            enemy = 'b'
            my_pawn_place = [(p[0] * -1, p[1] * -1) for p in my_pawn_place]

        # en-passant can't be done in less than three moves:
        if len(self.move_log) > 3:
            last_move = self.move_log[-1]
            c = last_move.end_col
            r = last_move.end_row
            # *last* move of the opponent , two steps
            if last_move.piece_moved == enemy + 'P' and abs(last_move.start_row - last_move.end_row) == 2:
                # check if there is my pawn in the row next to the opponent
                for p in my_pawn_place:
                    if 0 <= c + p[1] < 8 and 0 <= r + p[0] < 8:
                        my_piece = self.board[r][c + p[1]]
                        if (not my_piece[0] == enemy) and (my_piece[1] == 'P'):
                            moves.append(Move((r, c + p[1]), (r + p[0], c), self.board))
        return moves

    def validKingMoves(self, r, c):
        """

        :param r: row of square of te pawn : int
        :param c: column of square of the pawn : int
        :return all valid moves for the pawn : list(Move)
            Illustration for the places that the king can move:
                R - row, C - column, P - plus(forward), M-minus(backward)

            RP-CM  RP   RP-CP     (1, -1),  (1, 0),  (1, 1)
            CM    King  CP    ->  (0, -1),  (0, 0),  (0, 1)
            RM-CM  RM   RM-CP     (-1, -1), (-1, 0), (-1, 1)

        """
        moves = []

        # all directions that the king can move:
        king_directions = [(1, -1), (1, 0), (1, 1), (0, -1), (0, 1), (-1, -1), (-1, 0), (-1, 1)]
        enemy = 'w'
        k_r = self.black_king_place[0]
        k_c = self.black_king_place[1]

        if self.isWhiteMove:
            enemy = 'b'
            k_r = self.white_king_place[0]
            k_c = self.white_king_place[1]

        """
        In this section we will look for threats on the king if the is a threat remove this direction , 'cause
         king cant move there. 
        """
        if len(self.threats) >= 1:
            for threat in self.threats:
                d = threat[1]
                pos = threat[0]
                if self.board[pos[0]][pos[1]] != enemy + "N" and d in king_directions:  # if it's a knight the is no threat direction!
                    if (k_r + d[0], k_c + d[1]) != pos:  # the king doesn't eat the threat, remove that direction as valid
                        king_directions.remove(d)

        for d in king_directions:
            row = r + d[0]  # the place of the row king + step
            col = c + d[1]  # the place of the col king + step
            # validation in row and col in board:
            if 0 <= row < 8 and 0 <= col < 8:
                # the place is empty or enemy color:
                if self.board[row][col][0] == enemy or self.board[row][col] == "--":
                    """
                    check if the king move will make him been threats
                    """
                    threats = self.lookForCheck(row, col)[0]
                    if len(threats) == 0:  # the new king move will not make another check:
                        moves.append(Move((r, c), (row, col), self.board))
        return moves

    def validQueenMoves(self, r, c):
        """

        :param r: row of square of te queen : int
        :param c: column of square of the queen : int
        :return all valid moves for the queen : list(Move)
        The queen move are the moves of the rook and the bishop together.
        """
        return self.validRookMoves(r, c) + self.validBishopMoves(r, c)

    def validPawnMoves(self, r, c):
        """

        :param r: row of square of te pawn : int
        :param c: column of square of the pawn : int
        :return all valid moves for the pawn : list(Move)
        the valid moves for a pawn are 1 or 2 steps forward on the first move, 1 step forward if the is no
        other piece ahead , and he eat diagonal (only forward)
        """
        moves = []
        pawn_moves = [(1, -1), (1, 1), (1, 0), (2, 0)]
        one_step_flag = False  # for two steps
        enemy = "w"
        # white move from the last row -> down , so his directions are opposite
        if self.isWhiteMove:
            pawn_moves = [(d[0] * -1, d[1] * -1) for d in pawn_moves]
            enemy = "b"

        # eat move for pawn:
        for d in pawn_moves[0:2]:
            row = r + d[0]
            col = c + d[1]
            if 0 <= row < 8 and 0 <= col < 8:
                # the place is enemy color:
                if self.board[row][col][0] == enemy:
                    moves.append(Move((r, c), (row, col), self.board))

        for d in pawn_moves[2:4]:
            row = r + d[0]
            col = c + d[1]
            if 0 < row < 8 and (not one_step_flag):
                # the place is empty:
                if self.board[row][col][0] == "-":
                    moves.append(Move((r, c), (row, col), self.board))
                    one_step_flag = True
                else:
                    break  # cant make one step , can't make two
            # the condition for two steps:
            if ((self.isWhiteMove and r == 6) or (not self.isWhiteMove and r == 1)) and abs(
                    r - row) == 2 and one_step_flag:
                if self.board[row][col][0] == "-":
                    moves.append(Move((r, c), (row, col), self.board))

        # if the pawn is protector, if he eat the threat this is valid move else, he cant move
        if len(self.protectors) == 1:
            p = self.protectors[0]
            if (r, c) == p[0] and p[1] in pawn_moves[:2]:
                if self.board[r+p[1][0]][c+p[1][1]][0] == enemy:
                    return [Move((r, c), (r+p[1][0], c+p[1][1]), self.board)]
                else:
                    return []

        return moves

    def validBishopMoves(self, r, c):
        """

        :param r: row of square of te bishop : int
        :param c: column of square of the bishop : int
        :return all valid moves for the bishop : list(Move)
        the bishop moves diagonal, it moves in four diagonal way until another piece,
        -- XX     ++
        XX bishop XX
        -+ XX     +-
        """

        moves = []
        enemy = 'w'
        bishop_directions = [(-1, -1), (1, 1), (-1, 1), (1, -1)]

        # if the bishop is protector, if he move in the direction of the threat this is valid move else, he cant move
        if len(self.protectors) == 1:
            p = self.protectors[0]
            if (r, c) == p[0]:
                bishop_directions = [p[1], (-p[1][0], -p[1][1])]
        if self.isWhiteMove:
            enemy = 'b'
        for d in bishop_directions:
            for i in range(1, 8):
                row = r + (d[0] * i)
                col = c + (d[1] * i)
                # validation in row and col in board:
                if 0 <= row < 8 and 0 <= col < 8:
                    # the place is empty or enemy color:
                    if self.board[row][col] == "--":
                        moves.append(Move((r, c), (row, col), self.board))
                    elif self.board[row][col][0] == enemy:
                        moves.append(Move((r, c), (row, col), self.board))
                        break  # meet enemy
                    else:
                        break  # meet friendly piece
                else:
                    break  # out of board

        return moves

    def validKnightMoves(self, r, c):
        """

         :param r: row of square of te knight : int
        :param c: column of square of the knight : int
        :return all valid moves for the knight : list(Move)
        the knight eat and move 1 step and the 2 more in 90 degrees.
        in another words all the possible moves: (r,c)- the (row,column) of the knight
            (r+1 c+2) (r+1 c-2) (r-1 c+2) (r-1 c-2) (r+2 c+1) (r+2 c-1) (r-2 c+1) (r-2 c-1)
        """
        moves = []
        enemy = 'w'
        knight_moves = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (-2, 1), (2, -1), (-2, -1)]

        # if the knight is protector, he can't move
        if len(self.protectors) == 1:
            p = self.protectors[0]
            if (r, c) == p[0]:
                return []

        if self.isWhiteMove:
            enemy = 'b'

        for m in knight_moves:
            row = r + m[0]
            col = c + m[1]
            # validation in row and col in board:
            if 0 <= row < 8 and 0 <= col < 8:
                # the place is empty or enemy color:
                if self.board[row][col] == "--" or self.board[row][col][0] == enemy:
                    moves.append(Move((r, c), (row, col), self.board))

        return moves

    def validRookMoves(self, r, c):
        """

        :param r: row of square of te rook : int
        :param c: column of square of the rook : int
        :return all valid moves for the rook : list(Move)
        The Rook valid moves are like plus sign to any distance that we want unless there is a piece in his way.
        If it's the opponent piece he can eat him if not he can't skip it.
        """
        moves = []
        enemy = 'w'
        rook_directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

        # if the rook is protector, if he move in the direction of the threat this is valid move else, he cant move
        if len(self.protectors) == 1:
            p = self.protectors[0]
            if (r, c) == p[0]:
                rook_directions = [p[1], (-p[1][0], -p[1][1])]

        if self.isWhiteMove:
            enemy = 'b'
        for d in rook_directions:
            for i in range(1, 8):
                row = r + (d[0] * i)
                col = c + (d[1] * i)
                # validation in row and col in board:
                if 0 <= row < 8 and 0 <= col < 8:
                    # the place is empty or enemy color:
                    if self.board[row][col] == "--":
                        moves.append(Move((r, c), (row, col), self.board))
                    elif self.board[row][col][0] == enemy:
                        moves.append(Move((r, c), (row, col), self.board))
                        break  # meet enemy
                    else:
                        break  # meet friendly piece
                else:
                    break  # out of board

        return moves


class Move:
    # In real chess board each place is indexed from the bottom right corner ,
    # the row are numbered from 1-8 , and the cols are indexed from A-H
    # we created dictionaries from how our board stored as table to indexed board and the opposite:
    rankToRow = {"1": 7, "2": 6, "3": 5, "4": 4,
                 "5": 3, "6": 2, "7": 1, "8": 0}
    rowToRank = {v: k for k, v in rankToRow.items()}
    letterToCol = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colToLetter = {v: k for k, v in letterToCol.items()}

    def __init__(self, start_sq, end_sq, board):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_capture = board[self.end_row][self.end_col]
        self.moveID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col  # unique ID to
        # each instance

    # overriding the equal method to compere between to different instances with the same moveID,
    # (which it means that it's a different instances to the same move)
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    # get the place of the move as indexed board.
    def getPlaceNotation(self):
        return self.getRankLetter(self.start_row, self.start_col) + \
               self.getRankLetter(self.end_row, self.end_col)

    # table to indexed
    def getRankLetter(self, r, c):
        return self.colToLetter[c] + self.rowToRank[r]

    # indexed to table
    def getRowCol(self, r, l):
        return self.rankToRow[r] + self.letterToCol[l]
