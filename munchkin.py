from boardrep import BoardRep,ValidMoves
import random
import numpy as np
from dataclasses import dataclass
import conversions

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

    best_move = find_best_move(board_rep,legal_moves,4,colour)

    source_square, target_square = best_move
    current_player_board = board_rep.bitboard_white if colour == "white" else board_rep.bitboard_black

    moved_piece = next((p for p, bb in current_player_board.items() if bb & source_square), None)
    board_rep.make_move(move = best_move,moved_piece = moved_piece, colour = colour)

    return True

def get_move_priority(move, board_rep, colour, piece_order):
    source, target = move
    current_board = board_rep.bitboard_white if colour == "white" else board_rep.bitboard_black
    moved_piece = next((p for p, bb in current_board.items() if bb & source), None)
    if not moved_piece:
        return 0
    opponent_board = board_rep.bitboard_black if colour == "white" else board_rep.bitboard_white
    opponent_occupied = sum(opponent_board.values())
    captured_piece = next((p for p, bb in opponent_board.items() if bb & target), None)
    if captured_piece:
        victim_val = piece_order[captured_piece]
        attacker_val = piece_order[moved_piece]
        return victim_val * 10 - attacker_val  # MVV-LVA score; all positive for captures
    elif moved_piece == "pawn" and target == board_rep.en_passant_square:
        victim_val = piece_order["pawn"]
        attacker_val = piece_order["pawn"]
        return victim_val * 10 - attacker_val
    return 0  # Quiet moves

def minimax(board_rep,values,tables,depth,colour,alpha,beta):
    if depth == 0:
        return evaluate_board(board_rep.bitboard_white,board_rep.bitboard_black,values,tables)
    validator = ValidMoves(board_rep)
    legal_moves = validator.generate_all_legal_moves(colour)
    if not legal_moves:
        king_pos = board_rep.bitboard_white["king"] if colour == "white" else board_rep.bitboard_black["king"]
        if validator.is_square_attacked(king_pos,colour):
            sign = -1 if colour == "white" else 1
            return sign*np.inf

    current_player_board = board_rep.bitboard_white if colour == "white" else board_rep.bitboard_black
    opponent_colour = "black" if colour == "white" else "white"

    if colour == "white":
        value = -np.inf
        legal_moves.sort(key=lambda m: get_move_priority(m, board_rep, colour, piece_order), reverse=True)
        for move in legal_moves:
            source_square,_ = move
            moved_piece = next((p for p, bb in current_player_board.items() if bb & source_square),None)

            if not moved_piece:
                continue
            unmake_info = board_rep.make_move(move,moved_piece,colour)
            value = max(value,minimax(board_rep,values,tables,depth-1,opponent_colour,alpha,beta))
            board_rep.unmake_move(unmake_info)
            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return value

    else:
        value = np.inf
        legal_moves.sort(key=lambda m: get_move_priority(m, board_rep, colour, piece_order), reverse=False)
        for move in legal_moves:
            source_square,_ = move
            moved_piece = next((p for p, bb in current_player_board.items() if bb & source_square),None)

            if not moved_piece:
                continue
            unmake_info = board_rep.make_move(move,moved_piece,colour)
            value = min(value,minimax(board_rep,values,tables,depth-1,opponent_colour,alpha,beta))
            board_rep.unmake_move(unmake_info)
            beta = min(beta, value)
            if beta <= alpha:
                break

        return value

def find_best_move(board_rep, legal_moves, depth, colour):
    values = PieceValue()
    tables = PieceTable()

    alpha = -np.inf
    beta = np.inf

    best_move = None
    best_score = -np.inf if colour == "white" else np.inf

    legal_moves.sort(key=lambda m: get_move_priority(m, board_rep, colour, piece_order), reverse=True)
    for move in legal_moves:
        source_square, target_square = move
        current_player_board = board_rep.bitboard_white if colour == "white" else board_rep.bitboard_black
        moved_piece = next((p for p, bb in current_player_board.items() if bb & source_square), None)
        if not moved_piece:
            continue

        unmake_info = board_rep.make_move(move, moved_piece, colour)

        opponent_colour = "black" if colour == "white" else "white"
        score = minimax(board_rep, values, tables, depth-1, opponent_colour,alpha,beta)
        print(f"Move: {conversions.square_to_algebraic(source_square)}, {conversions.square_to_algebraic(target_square)} ({moved_piece}), Score: {score}")
        board_rep.unmake_move(unmake_info)

        if colour == "white":
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha,score)

        else:
            if score < best_score:
                best_score = score
                best_move = move
            beta = min(beta,score)

    print(f"Munchkin found best move: {best_move[0]},{best_move[1]} with score: {best_score}")
    return best_move


def evaluate_board(board_white,board_black,values,tables):
    white_score = 0
    black_score = 0

    for piece, bitboard in board_white.items():
        piece_value = getattr(values, piece)
        piece_table = getattr(tables, piece)
        bb_copy = bitboard
        while bb_copy > 0:
            lsb = bb_copy & -bb_copy
            square_index = lsb.bit_length() - 1
            white_score += piece_value
            white_score += piece_table[7 - (square_index // 8)][square_index % 8]
            bb_copy &= (bb_copy - 1)

    for piece, bitboard in board_black.items():
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

