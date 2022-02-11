"""
In this file we will make a AI-computer player , It will learn the board,
and make decisions. Using few algorithms, min-max tree decision ,alpha-beta pruning

"""
from Chess import ChessEngine
import random
from math import inf
import gym
import gym_chess

PAWN_PLACE_EVALUATION = [[0, 0, 0, 0, 0, 0, 0, 0],
                         [50, 50, 50, 50, 50, 50, 50, 50],
                         [10, 10, 20, 30, 30, 20, 10, 10],
                         [5, 5, 10, 25, 25, 10, 5, 5],
                         [0, 0, 0, 20, 20, 0, 0, 0],
                         [5, -5, -10, 0, 0, -10, -5, 5],
                         [5, 10, 10, -20, -20, 10, 10, 5],
                         [0, 0, 0, 0, 0, 0, 0, 0]]
KNIGHT_PLACE_EVALUATION = [[-50, -40, -30, -30, -30, -30, -40, -50],
                           [-40, -20, 0, 0, 0, 0, -20, -40],
                           [-30, 0, 10, 15, 15, 10, 0, -30],
                           [-30, 5, 15, 20, 20, 5, 15, -30],
                           [-30, 0, 15, 20, 20, 15, 0, -30],
                           [-30, 5, 10, 15, 15, 10, 5, -30],
                           [-40, -20, 0, 5, 5, 0, -20, -40],
                           [-50, -40, -30, -30, -30, -30, -40, -50]]
BISHOP_PLACE_EVALUATION = [[-20, -10, -10, -10, -10, -10, -10, -20],
                           [-10, 0, 0, 0, 0, 0, 0, -10],
                           [-10, 0, 5, 10, 10, 5, 0, -10],
                           [-10, 5, 5, 10, 10, 5, 5, -10],
                           [-10, 0, 10, 10, 10, 10, 0, -10],
                           [-10, 10, 10, 10, 10, 10, 10, -10],
                           [-10, 5, 0, 0, 0, 0, 5, -10],
                           [-20, -10, -10, -10, -10, -10, -10, -20]]
ROOK_PLACE_EVALUATION = [[0, 0, 0, 0, 0, 0, 0, 0],
                         [5, 10, 10, 10, 10, 10, 10, 5],
                         [-5, 0, 0, 0, 0, 0, 0, -5],
                         [-5, 0, 0, 0, 0, 0, 0, -5],
                         [-5, 0, 0, 0, 0, 0, 0, -5],
                         [-5, 0, 0, 0, 0, 0, 0, -5],
                         [-5, 0, 0, 0, 0, 0, 0, -5],
                         [0, 0, 0, 5, 5, 0, 0, 0]]
QUEEN_PLACE_EVALUATION = [[-20, -10, -10, -5, -5, -10, -10, -20],
                          [-10, 0, 0, 0, 0, 0, 0, -10],
                          [-10, 0, 5, 5, 5, 5, 0, -10],
                          [-5, 0, 5, 5, 5, 5, 0, -5],
                          [0, 0, 5, 5, 5, 5, 0, -5],
                          [-10, 5, 5, 5, 5, 5, 0, -10],
                          [-10, 0, 5, 0, 0, 0, 0, -10],
                          [-20, -10, -10, -5, -5, -10, -10, -20]]
KING_PLACE_EVALUATION_STR = [[-30, -40, -40, -50, -50, -40, -40, -30],
                             [-30, -40, -40, -50, -50, -40, -40, -30],
                             [-30, -40, -40, -50, -50, -40, -40, -30],
                             [-30, -40, -40, -50, -50, -40, -40, -30],
                             [-20, -30, -30, -40, -40, -30, -30, -20],
                             [-10, -20, -20, -20, -20, -20, -20, -10],
                             [20, 20, 0, 0, 0, 0, 20, 20],
                             [20, 30, 10, 0, 0, 10, 30, 20]]
KING_PLACE_EVALUATION_END = [[-50, -40, -30, -20, -20, -30, -40, -50],
                             [-30, -20, -10, 0, 0, -10, -20, -30],
                             [-30, -10, 20, 30, 30, 20, -10, -30],
                             [-30, -10, 30, 40, 40, 30, -10, -30],
                             [-30, -10, 30, 40, 40, 30, -10, -30],
                             [-30, -10, 20, 30, 30, 20, -10, -30],
                             [-30, -30, 0, 0, 0, 0, -30, -30],
                             [-50, -30, -30, -30, -30, -30, -30, -50]]


def get_king_pos_evaluation(board):
    count = 0
    for i in range(8):
        for j in range(8):
            if board[i][j] != "--":
                count += 1
    if count > 15:
        return KING_PLACE_EVALUATION_STR
    return KING_PLACE_EVALUATION_END


class AIPlayer:
    def __init__(self, colorIsWhite, gs):
        self.game_state = gs
        self.position_evaluation = {'P': (100, PAWN_PLACE_EVALUATION), 'N': (320, KNIGHT_PLACE_EVALUATION),
                                    'B': (330, BISHOP_PLACE_EVALUATION), 'R': (500, ROOK_PLACE_EVALUATION),
                                    'Q': (900, QUEEN_PLACE_EVALUATION),
                                    'K': (20000, get_king_pos_evaluation(self.game_state.board))}

        self.colorIsWhite = colorIsWhite
        self.board_evaluation = self.makeEvaluation(gs.board)

    def makeEvaluation(self, board):
        evaluation = 0
        for i in range(8):
            for j in range(8):
                if (self.colorIsWhite and board[i][j][0] == 'w') or (
                        not self.colorIsWhite and board[i][j][0] == 'b'):  # computer piece
                    color = board[i][j][0]
                    piece = board[i][j][1]
                    if color == 'w':
                        evaluation += self.position_evaluation[piece][0] + self.position_evaluation[piece][1][i][j]
                    else:
                        evaluation += self.position_evaluation[piece][0] - self.position_evaluation[piece][1][i][j]

                elif board[i][j][0] == "-":  # empty square
                    evaluation += 0
                else:  # an enemy piece
                    color = board[i][j][0]
                    piece = board[i][j][1]
                    if color == 'w':
                        evaluation += -self.position_evaluation[piece][0] + self.position_evaluation[piece][1][i][j]
                    else:
                        evaluation += -self.position_evaluation[piece][0] - self.position_evaluation[piece][1][i][j]
        return evaluation

    def getBestMove(self):
        best_move, value = self.MiniMax(3, -inf, inf, True)
        print("The best value is: {}".format(value))
        return best_move

    def MiniMax(self, depth, alpha, beta, MinMaxplayer):
        """
        minimax algorithm is recursive decision tree , that find the best move for player in two players game to certain
        depth.
        alpha-beta pruning
        :return: best value and move for the node.
        """
        moves = self.game_state.getValidMoves()  # get all moves for the current node

        # first condition: if we are in terminal node or we reach to check,
        # the best value is not known yet ,
        # and the value is the evaluation of the current node
        if depth == 0 or self.game_state.gameOver:
            value = self.makeEvaluation(self.game_state.board)
            return None, value

        best_move = random.choice(moves)  # choose randomly a move as best move ,
        # if the evaluation of other move will be better the best move will change

        if MinMaxplayer:  # computer turn (or parent node turn)
            value = - inf
            for move in moves:  # for each move in all valid moves make a move , and send them to the method again.
                self.game_state.makeMove(move)
                new_val = self.MiniMax(depth - 1, alpha, beta, False)[1]
                self.game_state.undoMove()  # undo the move (back up in tree)

                if new_val > value:  # get the maximum score you can get
                    value = new_val
                    best_move = move  # if the score is bigger then the last value , the is a new best move

                alpha = max(alpha, new_val)
                if beta <= alpha:
                    break
            print("MAX: best value is: {}".format(value))
            return best_move, value
        else:
            value = inf
            for move in moves:
                self.game_state.makeMove(move)
                new_val = self.MiniMax(depth - 1, alpha, beta, True)[1]
                self.game_state.undoMove()

                if new_val < value:
                    value = new_val
                    best_move = move

                beta = min(beta, new_val)
                if beta <= alpha:
                    break

            print("MIN: best value is: {}".format(value))
            return best_move, value


import pandas as pd
import tensorflow as tf
import gym
import gym_chess


class DP_player:
    def __init__(self):
        self.env = gym.make('Chess-v0')
        self.train()

    def train(self):
        for i_episode in range(20):
            observation = self.env.reset()
            for t in range(100):
                self.env.render()
                print(observation)
                action = self.env.get_possible_actions()
                observation, reward, done, info = self.env.step(action)
                if done:
                    print("Episode finished after {} timesteps".format(t + 1))
                    break
        self.env.close()