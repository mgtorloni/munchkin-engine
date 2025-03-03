class BoardRep:
    """Turns board into a bitboards"""
    def __init__(self):
        self.bitboards = { 
            "white_pawns": 0,
            "black_pawns": 0,
            "white_knights": 0,
            "black_knights": 0,
            "white_bishops": 0,
            "black_bishops": 0,
            "white_queen": 0, 
            "black_queen": 0,
            "white_rooks": 0,
            "black_rooks": 0,
            "white_king": 0,
            "black_king": 0
        }

    def square_to_index(self, square: str) -> int:
        """Returns index given algebraic notation of a square"""
        file = square[0].lower()
        rank = int(square[1])
        file_index = ord(file) - ord('a')  # convert file into a decimal 0-7
        rank_index = rank - 1  # converting rank to 0-indexed 
        return rank_index * 8 + file_index

    def squares_from_rep(self, bitboard: int) -> list:
        """Returns a list of the square(s) of the bitboard of a piece in algebraic notation""" 
        squares = []
        for index in range(64):
            if (bitboard >> index) & 1:
                rank_index = index // 8
                file_index = index % 8 
                square = chr(ord('a') + file_index) + str(rank_index + 1)
                squares.append(square)
        return squares
    def set_bit(self, square: str, piece: str) -> int:
        """Change the position of a piece"""
        index = self.square_to_index(square)
        self.bitboards[piece] |= 1 << index
        return self.bitboards
    
    def full_bitboard(self):
        """Returns the where all of the pieces are"""
        full_bitboard = 0
        for bitboard in self.bitboards.values():
            full_bitboard |= bitboard 
        return full_bitboard

    def initial_position(self)->dict:
        """Set initial positions on the chess board"""
        for file in 'abcdefgh':
            self.bitboards["white_pawns"] |= 1 << self.square_to_index(file + "2")
            self.bitboards["black_pawns"] |= 1 << self.square_to_index(file + "7")
        for file in 'ah':
            self.bitboards["white_rooks"] |= 1 << self.square_to_index(file + "1")
            self.bitboards["black_rooks"] |= 1 << self.square_to_index(file + "8")
        for file in 'bg':
            self.bitboards["white_knights"] |= 1 << self.square_to_index(file + "1")
            self.bitboards["black_knights"] |= 1 << self.square_to_index(file + "8")
        for file in 'cf':
            self.bitboards["white_bishops"] |= 1 << self.square_to_index(file + "1")
            self.bitboards["black_bishops"] |= 1 << self.square_to_index(file + "8")
        self.bitboards["white_king"] |= 1 << self.square_to_index("e1")
        self.bitboards["white_queen"] |= 1 << self.square_to_index("d1")
        self.bitboards["black_king"] |= 1 << self.square_to_index("e8")
        self.bitboards["black_queen"] |= 1 << self.square_to_index("d8")
        return self.bitboards
class ValidMoves(BoardRep):
    def __init__(self,boardrep):
        self.pieces_pos = boardrep.bitboards
    def knight(self)-> int:
        knight = self.pieces_pos["white_knights"] 
        knight_attacks = 0
        notHFile=~sum(1 << (7 + 8 * i) for i in range(8))&0xFFFFFFFFFFFFFFFF
        notGHFile= (notHFile & (~sum(1<< (6+8*i) for i in range(8))))&0xFFFFFFFFFFFFFFFF
        notAFile=~sum(1 << (8 * i) for i in range(8))&0xFFFFFFFFFFFFFFFF
        notABFile= (notAFile & (~sum(1<< (1+8*i) for i in range(8))))&0xFFFFFFFFFFFFFFFF
        knight_attacks |= (knight>>15) & notAFile|(knight<<15) & notHFile|(knight<<10) & notABFile|(knight>>10)&notGHFile|(knight<<17) & notAFile|(knight>>17)&notHFile |(knight<<6)&notGHFile|(knight>>6)&notABFile
        return knight_attacks

