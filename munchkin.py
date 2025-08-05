from boardrep import BoardRep
import random

def munchkin_move(board_rep:BoardRep,legal_moves:list, colour = "black"):
    print(f"Legal moves: {legal_moves}")
    move = random.choice(legal_moves)
    source_square,target_square = move
    current_board = board_rep.bitboard_black if colour == "black" else board_rep.bitboard_white
    piece_at_source = None
    for piece_name, bitboard in current_board.items():
        if bitboard & source_square:
            piece_at_source = piece_name
            break

    print(f"AI moving {piece_at_source} from {source_square} to {target_square}")

    board_rep.make_move(move = move,colour = colour,en_passant_square = board_rep.en_passant_square)
    return True

