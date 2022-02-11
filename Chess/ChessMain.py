"""
This is the main file, where we are going to handle with the game interface and user input.
"""
import pygame as pg
from Chess import ChessEngine, AI_player
from Chess.ErrorHandel import *

# global variables:
WIDTH = HEIGHT = 512
DIM = 8
SQ_SIZE = HEIGHT // DIM
MAX_FPS = 15  # for animation.
IMAGES = {}


# In this function we are going to load (once) , the images of the pieces to the IMAGES list.
def load_images():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
    for piece in pieces:
        # we are loading the images and fitting it to the size of a square on the board
        IMAGES[piece] = pg.transform.scale(
            pg.image.load(r"C:\Users\nitai\PycharmProjects\Chess\Chess\chess_images/" + piece + ".png"),
            (SQ_SIZE, SQ_SIZE))


# This is th main function, here we will handle with the user interface and the gamestate.
def main():
    pg.init()
    load_images()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    screen.fill(pg.Color("white"))
    gs = ChessEngine.GameState()

    play_against_computer = True
    computer_player = AI_player.AIPlayer(False, gs)

    validMoves = gs.getValidMoves()  # list of all valid moves for the player
    moveMade = False  # a flag to control the call for gs.getValidMoves() function

    running = True
    mouse_selected = ()  # the location of the square that pressed by user (tuple: (x,y))
    sq_selected = []  # list of the the to last two clicks of the user (first for picking the second is where to move)

    while running:
        try:
            for e in pg.event.get():
                # close event:
                if e.type == pg.QUIT:
                    running = False
                # mouse handler:
                elif e.type == pg.MOUSEBUTTONDOWN:
                    location = pg.mouse.get_pos()
                    row = location[1] // SQ_SIZE  # y
                    col = location[0] // SQ_SIZE  # x
                    if (row, col) == mouse_selected:  # it mean the user double clicked the same place
                        # -> cancel the move
                        mouse_selected = ()
                        sq_selected = []
                    else:
                        mouse_selected = (row, col)
                        sq_selected.append(mouse_selected)
                        if len(sq_selected) == 2:
                            # make a move.
                            move = ChessEngine.Move(sq_selected[0], sq_selected[1], gs.board)
                            if move.piece_moved == "--":
                                raise IllegalMove("there is no piece picked!")
                            elif not gs.matchTurnPiece(move):
                                if gs.isWhiteMove:
                                    raise NotYourTurn("You cant move this piece you are white!")
                                if not gs.isWhiteMove:
                                    raise NotYourTurn("You cant move this piece you are black!")
                            elif move in validMoves:  # check if the move is in the valid move that the player can do!
                                gs.makeMove(move)
                                moveMade = True  # recalculate the possible moves after a move done
                            else:
                                raise IllegalMove("Illegal move")
                            # after the move clear the variables for the next move
                            mouse_selected = ()
                            sq_selected = []
                # Key handler:
                elif e.type == pg.KEYDOWN:
                    if e.key == pg.K_DELETE:
                        gs.undoMove()
                        if play_against_computer:  # need to undo twice - to overcome the same computer move
                            gs.undoMove()
                        moveMade = True  # recalculate the possible moves after a move undo
            if moveMade:
                if gs.gameOver:
                    raise EndGame(gs.isWhiteMove)
                if play_against_computer:  # computer_play_turn
                    if (computer_player.colorIsWhite and gs.isWhiteMove) or \
                            (not computer_player.colorIsWhite and not gs.isWhiteMove):
                        gs.makeMove(computer_player.getBestMove())
                validMoves = gs.getValidMoves()
                moveMade = False
            drawGameState(screen, gs)
            if len(sq_selected) == 1:
                lightMoves(validMoves, sq_selected[0], screen)
            clock.tick(MAX_FPS)
            pg.display.flip()

        except NotYourTurn as ex:
            ex.showMessage()
            mouse_selected = ()
            sq_selected = []
        except NoUndo as ex:
            print(ex)
            pass
        except IllegalMove as ex:
            ex.showMessage()
            mouse_selected = ()
            sq_selected = []
        except EndGame as ex:
            ex.showMessage()
            running = False

# this function responsible for the graphics for a current game state
def drawGameState(screen, gs):
    drawGameBoard(screen)
    drawGamePieces(screen, gs.board)


# this function will display on the screen the board game.
def drawGameBoard(screen):
    colors = [pg.Color("light gray"), pg.Color("dark gray")]
    for r in range(DIM):
        for c in range(DIM):
            color = colors[((r + c) % 2)]  # first right square is white, so the row + column % 2 is
            # whether it even or odd ,white - even black - odd
            pg.draw.rect(screen, color, pg.Rect(r * SQ_SIZE, c * SQ_SIZE, SQ_SIZE, SQ_SIZE))  # r*sq and c*sq are the
            # coordinates where to start draw the rect, sq and sq are the size of the rect


# this function will display on the screen the pieces of the current state.
def drawGamePieces(screen, board):
    for r in range(DIM):
        for c in range(DIM):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece],
                            pg.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))  # switch between r and c
                # to put the pieces in the the right place.


def lightMoves(validMoves, mouse_selected, screen):
    # highlighting the selected square:
    pg.draw.rect(screen,
                 "orange",
                 pg.Rect(mouse_selected[1] * SQ_SIZE,
                         mouse_selected[0] * SQ_SIZE,
                         SQ_SIZE, SQ_SIZE), 2)

    # highlighting the valid squares that the piece can go to
    for move in validMoves:
        if (move.start_row, move.start_col) == mouse_selected:
            pg.draw.rect(screen,
                         "yellow",
                         pg.Rect(move.end_col * SQ_SIZE,
                                 move.end_row * SQ_SIZE,
                                 SQ_SIZE, SQ_SIZE), 2)


if __name__ == "__main__":
    main()
