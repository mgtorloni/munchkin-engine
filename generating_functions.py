"""
THIS FILE CONTAINS THE FUNCTIONS THAT GENERATE THE VALUES IN constants.py
"""
def generate_rook_mask(square: int) -> int:
    rank = square // 8
    file = square % 8
    mask = 0

    for f in range(8):
        if f != file:
            mask|= 1 << (rank * 8 + f)
    # Vertical (File)
    for r in range(8):
        if r != rank:
            mask|= 1 << (r * 8 + file)
    return mask
ROOK_MASKS = [generate_rook_mask(s) for s in range(64)]
print(ROOK_MASKS)

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
    return mask

# Build a list of bishop masks for all 64 squares
BISHOP_MASKS = [generate_bishop_mask(s) for s in range(64)]
print(BISHOP_MASKS)

def generate_initial_positions():
    import conversions
    for file in 'abcdefgh':
        self.bitboard_white["pawns"] |= 1 << conversions.square_to_index(file + "2")
        
        self.bitboard_black["pawns"] |= 1 << conversions.square_to_index(file + "7")
       
    for file in 'ah':
        self.bitboard_white["rooks"] |= 1 << conversions.square_to_index(file + "1")
        self.bitboard_black["rooks"] |= 1 << conversions.square_to_index(file + "8")
    for file in 'bg':
        self.bitboard_white["knights"] |= 1 << conversions.square_to_index(file + "1")
        self.bitboard_black["knights"] |= 1 << conversions.square_to_index(file + "8")
    for file in 'cf':
        self.bitboard_white["bishop"] |= 1 << conversions.square_to_index(file + "1")
        self.bitboard_black["bishop"] |= 1 << conversions.square_to_index(file + "8")
    self.bitboard_white["king"] |= 1 << conversions.square_to_index("e1")
    self.bitboard_white["queen"] |= 1 << conversions.square_to_index("d1")
    self.bitboard_black["king"] |= 1 << conversions.square_to_index("e8")
    self.bitboard_black["queen"] |= 1 << conversions.square_to_index("d8")
    return (self.bitboard_white,self.bitboard_black)
