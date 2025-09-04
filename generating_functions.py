"""
THIS FILE CONTAINS THE FUNCTIONS THAT GENERATE THE VALUES IN constants.py
"""
from typing import List

def bitboard_to_string(bitboard: int, piece_bb:int = 0) -> str:
    board_str = ""
    for rank in range(7, -1, -1):
        board_str += f"{rank + 1} | "
        for file in range(8):
            square_index = rank * 8 + file
            square_bit = 1<<square_index
            if piece_bb & square_bit:
                board_str += "P "
            elif bitboard & square_bit:
                board_str += "X "
            else:
                board_str += ". "
        board_str += "\n"
    board_str += "  +-----------------\n"
    board_str += "    A B C D E F G H\n"
    return board_str

def generate_rook_mask_hyperbola(square: int) -> int:
    """
    In reality this function was broken up in two functions, creating horizontal masks and vertical masks for the rooks
    separately, this is important when passing it through the hyperbola quintessential formula
    """
    rank = square // 8
    file = square % 8
    mask = 0

    #Horizontal (Rank)
    for f in range(8):
        if f != file:
            mask|= 1 << (rank * 8 + f)
    # Vertical (File)
    for r in range(8):
        if r != rank:
            mask|= 1 << (r * 8 + file)
    return mask

#ROOK_MASKS = [generate_rook_mask_hyperbola(s) for s in range(64)]
#print(ROOK_MASKS)


def generate_bishop_mask(square: int) -> int:
    rank = square // 8
    file = square % 8
    mask = 0

    # Up-right diagonal
    r, f = rank, file
    while r < 7 and f < 7:
        r += 1
        f += 1
        mask |= 1 << (r * 8 + f)
    # Down-left diagonal
    r, f = rank, file
    while r > 0 and f > 0:
        r -= 1
        f -= 1
        mask |= 1 << (r * 8 + f)

    # Down-right diagonal
    r, f = rank, file
    while r > 0 and f < 7:
        r -= 1
        f += 1
        mask |= 1 << (r * 8 + f)

    # Up-left diagonal
    r, f = rank, file
    while r < 7 and f > 0:
        r += 1
        f -= 1
        mask |= 1 << (r * 8 + f)
    """
    
    In reality this function was broken up in two functions, creating right diagonal masks (45 degrees) and left diagonal masks (135 degrees) for the bishops 
    separately, this is important when passing it through the hyperbola quintessential formula

    """

    return mask

# Build a list of bishop masks for all 64 squares
#BISHOP_MASKS = [generate_bishop_mask_hyperbola(s) for s in range(64)]
#print(BISHOP_MASKS)

def generate_initial_positions(bitboard_white,bitboard_black):
    import conversions
    for file in 'abcdefgh':
        bitboard_white["pawns"] |= 1 << conversions.square_to_index(file + "2")
        
        bitboard_black["pawns"] |= 1 << conversions.square_to_index(file + "7")
       
    for file in 'ah':
        bitboard_white["rooks"] |= 1 << conversions.square_to_index(file + "1")
        bitboard_black["rooks"] |= 1 << conversions.square_to_index(file + "8")
    for file in 'bg':
        bitboard_white["knights"] |= 1 << conversions.square_to_index(file + "1")
        bitboard_black["knights"] |= 1 << conversions.square_to_index(file + "8")
    for file in 'cf':
        bitboard_white["bishop"] |= 1 << conversions.square_to_index(file + "1")
        bitboard_black["bishop"] |= 1 << conversions.square_to_index(file + "8")
    bitboard_white["king"] |= 1 << conversions.square_to_index("e1")
    bitboard_white["queen"] |= 1 << conversions.square_to_index("d1")
    bitboard_black["king"] |= 1 << conversions.square_to_index("e8")
    bitboard_black["queen"] |= 1 << conversions.square_to_index("d8")
    return (bitboard_white,bitboard_black)
