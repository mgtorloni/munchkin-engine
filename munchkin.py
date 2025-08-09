from boardrep import BoardRep
import random
import numpy as np
from dataclasses import dataclass

@dataclass
class PieceValue:
    pawn = 100
    knight = 320
    bishop = 330
    rook = 500
    queen = 900
    king = 20000

@dataclass
class PieceTable:
    #Piece square tables, from whites perspective
    #I can use -np.fliup(piece) to get whites perpective
    pawn = np.array([
    [0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5,  5, 10, 25, 25, 10,  5,  5],
    [0,  0,  0, 20, 20,  0,  0,  0],
    [5, -5,-10,  0,  0,-10, -5,  5],
    [5, 10, 10,-20,-20, 10, 10,  5],
    [0,  0,  0,  0,  0,  0,  0,  0]
     ])

    knight = np.array([
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
    ])

    bishop = np.array([
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0, 10, 10, 10, 10,  0,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
    ])

    rook = np.array([
    [0,  0,  0,  0,  0,  0,  0,  0],
    [5, 10, 10, 10, 10, 10, 10,  5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [0,  0,  0,  5,  5,  0,  0,  0]
    ])
    
    queen = np.array([
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [-5,  0,  5,  5,  5,  5,  0, -5],
    [0,  0,  5,  5,  5,  5,  0, -5],
    [-10,  5,  5,  5,  5,  5,  0,-10],
    [-10,  0,  5,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20]
    ])

    king= np.array([
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [20, 20,  0,  0,  0,  0, 20, 20],
    [20, 30, 10,  0,  0, 10, 30, 20]
    ])
    """
    king_end = np.array([
    [-50,-40,-30,-20,-20,-30,-40,-50],
    [-30,-20,-10,  0,  0,-10,-20,-30],
    [-30,-10, 20, 30, 30, 20,-10,-30],
    [-30,-10, 30, 40, 40, 30,-10,-30],
    [-30,-10, 30, 40, 40, 30,-10,-30],
    [-30,-10, 20, 30, 30, 20,-10,-30],
    [-30,-30,  0,  0,  0,  0,-30,-30],
    [-50,-30,-30,-30,-30,-30,-30,-50]
    ])
    """

    

def munchkin_move(board_rep:BoardRep,legal_moves:list, colour = "black"):

    values= PieceValue()
    tables= PieceTable()

    #print(f"Legal moves: {legal_moves}")

    move = random.choice(legal_moves)
    #source_square,target_square = move

    board = board_rep.bitboard_black if colour == "black" else board_rep.bitboard_white
    opponent_board = board_rep.bitboard_white if colour == "black" else board_rep.bitboard_black
    evaluation = evaluate_board(board_rep, values, tables)
    print(evaluation)

    board_rep.make_move(move = move,colour = colour,en_passant_square = board_rep.en_passant_square)

    return True


def evaluate_board(board_rep,values,tables):
    white_score = 0
    black_score = 0

    for piece, bitboard in board_rep.bitboard_white.items():
        piece_value = getattr(values, piece)
        piece_table = getattr(tables, piece)
        bb_copy = bitboard
        while bb_copy > 0:
            lsb = bb_copy & -bb_copy
            square_index = lsb.bit_length() - 1
            # Add material value
            white_score += piece_value
            # Add positional value using your original indexing for White
            white_score += piece_table[7 - (square_index // 8)][square_index % 8]
            bb_copy &= (bb_copy - 1)

    for piece, bitboard in board_rep.bitboard_black.items():
        piece_value = getattr(values, piece)
        piece_table = getattr(tables, piece)
        bb_copy = bitboard
        while bb_copy > 0:
            lsb = bb_copy & -bb_copy
            square_index = lsb.bit_length() - 1
            black_score += piece_value
            black_score += piece_table[square_index // 8][square_index % 8]
            bb_copy &= (bb_copy - 1)
    
    return white_score - black_score

