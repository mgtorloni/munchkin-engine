import conversions
class BoardRep:
    """Turns board into a bitboards"""
    def __init__(self):
        self.bitboard_black={
            "black_pawns": 0,
            "black_knights": 0,
            "black_bishops": 0,
            "black_queen": 0,
            "black_rooks": 0,
            "black_king": 0
        }
        self.bitboard_white = { 
            "white_pawns": 0,
            "white_knights": 0,
            "white_bishops": 0,
            "white_queen": 0, 
            "white_rooks": 0,
            "white_king": 0,
        }
   

    def set_bit(self,square: str, piece: str,color = "white") -> int:
        """Change the position of a piece"""
        index = conversions.square_to_index(square)
        if color.lower() == "white":
            self.bitboard_white[piece] |= 1 << index
            return self.bitboard_white
        elif color.lower() == "black":
            bitboard_black[piece] |= 1 << index
            return self.bitboard_black
        else:
            raise ValueError("Color must be either 'white' or 'black'")


    def full_bitboard(self):
        """Returns where all of the pieces are"""
        full_bitboard = 0
        for bitboard in self.bitboards.values():
            full_bitboard |= bitboard 
        return full_bitboard

    def initial_position(self)->tuple[dict,dict]:
        """Set initial positions on the chess board"""
        for file in 'abcdefgh':
            self.bitboard_white["white_pawns"] |= 1 << conversions.square_to_index(file + "2")
            self.bitboard_black["black_pawns"] |= 1 << conversions.square_to_index(file + "7")
        for file in 'ah':
            self.bitboard_white["white_rooks"] |= 1 << conversions.square_to_index(file + "1")
            self.bitboard_black["black_rooks"] |= 1 << conversions.square_to_index(file + "8")
        for file in 'bg':
            self.bitboard_white["white_knights"] |= 1 << conversions.square_to_index(file + "1")
            self.bitboard_black["black_knights"] |= 1 << conversions.square_to_index(file + "8")
        for file in 'cf':
            self.bitboard_white["white_bishops"] |= 1 << conversions.square_to_index(file + "1")
            self.bitboard_black["black_bishops"] |= 1 << conversions.square_to_index(file + "8")
        self.bitboard_white["white_king"] |= 1 << conversions.square_to_index("e1")
        self.bitboard_white["white_queen"] |= 1 << conversions.square_to_index("d1")
        self.bitboard_black["black_king"] |= 1 << conversions.square_to_index("e8")
        self.bitboard_black["black_queen"] |= 1 << conversions.square_to_index("d8")
        return (self.bitboard_white,self.bitboard_black)

class ValidMoves(BoardRep):
    def __init__(self,boardrep):
        self.board= {"white":boardrep.bitboard_white,"black":boardrep.bitboard_black}
        self.notHFile=~sum(1 << (7 + 8 * i) for i in range(8))&0xFFFFFFFFFFFFFFFF
        self.notGHFile= (self.notHFile & (~sum(1<< (6+8*i) for i in range(8))))&0xFFFFFFFFFFFFFFFF
        self.notAFile=~sum(1 << (8 * i) for i in range(8))&0xFFFFFFFFFFFFFFFF
        self.notABFile= (self.notAFile & (~sum(1<< (1+8*i) for i in range(8))))&0xFFFFFFFFFFFFFFFF

    def knight_attacks(self,color)-> int:
        knight = self.board[color+"_knight"] 
        knight_attacks = 0
        knight_attacks |= ((knight >> 15) & self.notAFile) | ((knight << 15) & self.notHFile) | \
                  ((knight << 10) & self.notABFile) | ((knight >> 10) & self.notGHFile) | \
                  ((knight << 17) & self.notHFile) | ((knight >> 17) & self.notAFile) | \
                  ((knight << 6)  & self.notGHFile) | ((knight >> 6)  & self.notABFile)
        own_pieces = sum(self.board[color].values()) 
        knight_attacks &= ~own_pieces
        return knight_attacks
    
    def king_attacks(self,color)->int:
        king = self.board[color][color+"_king"]
        king_attacks = 0 
        king_attacks |= ((king >> 1) & self.notHFile) | ((king << 1) & self.notAFile) |  \
               ((king >> 7) & self.notAFile) | ((king >> 9) & self.notHFile) |  \
               ((king << 7) & self.notHFile) | ((king << 9) & self.notAFile) |  \
               (king >> 8) | (king << 8)
        return king_attacks

    def pawns_attacks(self,color)->int:
        pawns = self.board[color][color+"_pawns"] 
        pawns_attacks = 0
        pawns_attacks |= ((pawns<<9) & self.notAFile)|((pawns<<7) & self.notHFile)
        return pawns_attacks
    #TODO: PAWN MOVES AND ATTACKS ARE INDEED DIFFERENT
    
    def rook_attacks(self)->int:
        ...    
