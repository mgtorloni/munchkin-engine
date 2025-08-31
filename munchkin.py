from boardrep import BoardRep,ValidMoves,MoveHandler
import random
import numpy as np
from dataclasses import dataclass
import conversions
import copy
import multiprocessing
from operator import itemgetter
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

piece_order = {
    "pawn": 1,
    "knight": 3,
    "bishop": 3,
    "rook": 5,
    "queen": 9,
    "king": 0  # Kings aren't captured, but include for completeness
}
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

    king = np.array([
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [20, 20,  0,  0,  0,  0, 20, 20],
    [20, 30, 10,  0,  0, 10, 30, 20]
    ])

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

def munchkin_move(board_rep:BoardRep,legal_moves:list, colour = "black"):
    move_handler = MoveHandler(board_rep)

    values= PieceValue()
    tables= PieceTable()

    #print(f"Legal moves: {legal_moves}")

    best_move = find_best_move(board_rep, legal_moves,5,colour)

    source_square, target_square = best_move
    current_player_board = board_rep.bitboard_white if colour == "white" else board_rep.bitboard_black

    move_handler.make_move(move = best_move, colour = colour)

    return True


def minimax(board_rep, move_handler, alpha, beta, depth, values, tables, colour):
    if depth == 0:
        return evaluate_board(board_rep.bitboard_white, board_rep.bitboard_black, values, tables)

    validator = ValidMoves(board_rep)
    pseudo_legal_moves = validator.generate_pseudo_legal_moves(colour)
    
    legal_moves_found = 0
    opponent_colour = "black" if colour == "white" else "white"

    if colour == "white":
        value = -np.inf
        for move in pseudo_legal_moves:
            unmake_info = move_handler.make_move(move, colour)

            king_bb = board_rep.bitboard_white["king"]
            if validator.is_square_attacked(king_bb, colour):
                move_handler.unmake_move(unmake_info)  # Illegal move, undo and skip
                continue
            
            legal_moves_found += 1
            value = max(value, minimax(board_rep, move_handler, alpha, beta, depth - 1, values, tables, opponent_colour))
            move_handler.unmake_move(unmake_info)
            
            if value >= beta:
                break
            alpha = max(alpha, value)
        
        # If no legal moves were found, it's checkmate or stalemate
        if legal_moves_found == 0:
            king_bb = board_rep.bitboard_white["king"]
            if validator.is_square_attacked(king_bb, colour):
                return -values.king+depth # Checkmate
            else:
                return 0 # Stalemate
        return value

    else:  # Black's turn
        value = np.inf
        for move in pseudo_legal_moves:
            unmake_info = move_handler.make_move(move, colour)

            king_bb = board_rep.bitboard_black["king"]
            if validator.is_square_attacked(king_bb, colour):
                move_handler.unmake_move(unmake_info)  # Illegal move, undo and skip
                continue
            
            legal_moves_found += 1
            value = min(value, minimax(board_rep, move_handler, alpha, beta, depth - 1, values, tables, opponent_colour))
            move_handler.unmake_move(unmake_info)
            
            if value <= alpha:
                break
            beta = min(beta, value)
        
        # If no legal moves were found, it's checkmate or stalemate
        if legal_moves_found == 0:
            king_bb = board_rep.bitboard_black["king"]
            if validator.is_square_attacked(king_bb, colour):
                return values.king-depth # Checkmate (good for white)
            else:
                return 0 # Stalemate
        return value

def score_move(fen_string: str, moves_to_check: list, depth: int, colour: str):
    board_rep = BoardRep()
    board_rep.from_fen(fen_string)
    move_handler = MoveHandler(board_rep)

    values = PieceValue()
    tables = PieceTable()
    alpha = -np.inf
    beta = np.inf
    
    best_move_local = None
    best_score_local = -np.inf if colour == "white" else np.inf
    opponent_colour = "black" if colour == "white" else "white"

    for move in moves_to_check:
        unmake_info = move_handler.make_move(move, colour)
        score = minimax(board_rep, move_handler, alpha, beta, depth - 1, values, tables, opponent_colour)
        move_handler.unmake_move(unmake_info)
        print(f"Move: {conversions.square_to_algebraic(move[0])}, {conversions.square_to_algebraic(move[1])}, Score: {score}")
        
        if colour == "white":
            if score > best_score_local:
                best_score_local = score
                best_move_local = move
            alpha = max(alpha, score)
        else: # Black
            if score < best_score_local:
                best_score_local = score
                best_move_local = move
            beta = min(beta, score)
            
    return best_score_local, best_move_local

def partition_lst(lst, n):
    length = len(lst)
    return [lst[i * length // n: (i + 1) * length // n]
            for i in range(n)]

def find_best_move(board_rep, legal_moves, depth, colour):
    num_threads = multiprocessing.cpu_count()
    print(num_threads)
    
    fen = board_rep.to_fen(colour)

    partitioned_list = partition_lst(legal_moves, num_threads)
    results = []

    with ProcessPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(score_move, fen, partition, depth, colour) 
            for partition in partitioned_list 
        ]

        for future in futures:
            result = future.result()
            if result[1] is not None:
                results.append(result)

    if colour == "white":
        best_score, best_move = max(results, key=itemgetter(0))
    else:
        best_score, best_move = min(results, key=itemgetter(0))

    print(f"Munchkin found best move: {conversions.square_to_algebraic(best_move[0])}{conversions.square_to_algebraic(best_move[1])} with score: {best_score}")
    return best_move

def is_endgame(board_white, board_black):
    white_has_queen = board_white["queen"] != 0
    black_has_queen = board_black["queen"] != 0

    if not white_has_queen and not black_has_queen:
        return True

    white_satisfies_condition = True
    if white_has_queen:
        num_white_rooks = bin(board_white["rook"]).count('1')
        num_white_knights = bin(board_white["knight"]).count('1')
        num_white_bishops = bin(board_white["bishop"]).count('1')
        
        if num_white_rooks > 0 or (num_white_knights + num_white_bishops) > 1:
            white_satisfies_condition = False

    black_satisfies_condition = True
    if black_has_queen:
        num_black_rooks = bin(board_black["rook"]).count('1')
        num_black_knights = bin(board_black["knight"]).count('1')
        num_black_bishops = bin(board_black["bishop"]).count('1')
        
        if num_black_rooks > 0 or (num_black_knights + num_black_bishops) > 1:
            black_satisfies_condition = False
            
    return white_satisfies_condition and black_satisfies_condition

def evaluate_board(board_white,board_black,values,tables):
    total_score = 0
    endgame = is_endgame(board_white,board_black)
    for piece, bitboard in board_white.items():

        piece_value = getattr(values, piece)
        piece_table = getattr(tables, piece)

        if piece == "king" and endgame:
            piece_table = getattr(tables,f"king_end")    
        bb_copy = bitboard
        while bb_copy > 0:
            lsb = bb_copy & -bb_copy
            square_index = lsb.bit_length() - 1
            total_score += piece_value
            total_score += piece_table[7-(square_index // 8)][square_index % 8]
            bb_copy &= (bb_copy - 1)

    for piece, bitboard in board_black.items():
        piece_value = getattr(values, piece)
        piece_table = getattr(tables, piece)
        bb_copy = bitboard
        
        while bb_copy > 0:
            lsb = bb_copy & -bb_copy
            square_index = lsb.bit_length() - 1
            total_score -= piece_value
            total_score -= piece_table[square_index // 8][square_index % 8]
            bb_copy &= (bb_copy - 1)
    
    return total_score 

