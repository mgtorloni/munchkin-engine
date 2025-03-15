import conversions
import constants
class BoardRep:
    """Turns board into a bitboards"""
    def __init__(self):
        self.bitboard_black={
            "pawns": 0,
            "knights": 0,
            "bishops": 0,
            "queen": 0,
            "rooks": 0,
            "king": 0
        }
        self.bitboard_white = { 
            "pawns": 0,
            "knights": 0,
            "bishops": 0,
            "queen": 0, 
            "rooks": 0,
            "king": 0,
        }
   

    def set_bit(self,square: str, piece: str,color = "white") -> int:
        """Change the position of a piece"""
        index = conversions.square_to_index(square)
        if color.lower() == "white":
            self.bitboard_white[piece] |= 1 << index
            return self.bitboard_white
        elif color.lower() == "black":
            self.bitboard_black[piece] |= 1 << index
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
            self.bitboard_white["pawns"] |= 1 << conversions.square_to_index(file + "2")
            self.bitboard_black["pawns"] |= 1 << conversions.square_to_index(file + "7")
        for file in 'ah':
            self.bitboard_white["rooks"] |= 1 << conversions.square_to_index(file + "1")
            self.bitboard_black["rooks"] |= 1 << conversions.square_to_index(file + "8")
        for file in 'bg':
            self.bitboard_white["knights"] |= 1 << conversions.square_to_index(file + "1")
            self.bitboard_black["knights"] |= 1 << conversions.square_to_index(file + "8")
        for file in 'cf':
            self.bitboard_white["bishops"] |= 1 << conversions.square_to_index(file + "1")
            self.bitboard_black["bishops"] |= 1 << conversions.square_to_index(file + "8")
        self.bitboard_white["king"] |= 1 << conversions.square_to_index("e1")
        self.bitboard_white["queen"] |= 1 << conversions.square_to_index("d1")
        self.bitboard_black["king"] |= 1 << conversions.square_to_index("e8")
        self.bitboard_black["queen"] |= 1 << conversions.square_to_index("d8")
        return (self.bitboard_white,self.bitboard_black)

class ValidMoves:
    def __init__(self,boardrep: BoardRep):
        self.board= {"white":boardrep.bitboard_white,"black":boardrep.bitboard_black}
        self.notHFile=~sum(1 << (7 + 8 * i) for i in range(8))&0xFFFFFFFFFFFFFFFF
        self.notGHFile= (self.notHFile & (~sum(1<< (6+8*i) for i in range(8))))&0xFFFFFFFFFFFFFFFF
        self.notAFile=~sum(1 << (8 * i) for i in range(8))&0xFFFFFFFFFFFFFFFF
        self.notABFile= (self.notAFile & (~sum(1<< (1+8*i) for i in range(8))))&0xFFFFFFFFFFFFFFFF

    def knight_attacks(self,index:int,color:str)-> int:
        #knight = self.board[color+"_knight"] 
        
        piece_square = 1<<index
        knight_attacks = ((piece_square >> 15) & self.notAFile) | ((piece_square << 15) & self.notHFile) | \
                ((piece_square << 10) & self.notABFile) | ((piece_square >> 10) & self.notGHFile) | \
                  ((piece_square << 17) & self.notHFile) | ((piece_square >> 17) & self.notAFile) | \
                  ((piece_square << 6)  & self.notGHFile) | ((piece_square >> 6)  & self.notABFile)
        own_pieces = sum(self.board[color].values()) 
        knight_attacks &= ~own_pieces
        return knight_attacks
    
    def king_attacks(self,square:int,color:str)->int:
        #king = self.board[color][color+"_king"]
        king_attacks = ((square >> 1) & self.notHFile) | ((square << 1) & self.notAFile) |  \
               ((square >> 7) & self.notAFile) | ((square >> 9) & self.notHFile) |  \
               ((square << 7) & self.notHFile) | ((square << 9) & self.notAFile) |  \
               (square >> 8) | (square << 8)
        return king_attacks

    def pawns_attacks(self,index:int,color:str)->int:
        #pawns = self.board[color][color+"_pawns"] 
        
        piece_square = 1<<index
        if color == "white":
            return ((piece_square << 9) & self.notAFile) | ((piece_square << 7) & self.notHFile)
        else:  # Black pawns attack downward
            return ((piece_square >> 9) & self.notHFile) | ((piece_square >> 7) & self.notAFile)
    #TODO: PAWN MOVES AND ATTACKS ARE INDEED DIFFERENT

    def hyperbola_quint(self,index:int,mask:list[int],color:str = "white")->int:
        occupied_squares = sum(self.board["white"].values())|sum(self.board["black"].values())
        slider_square = 1<<index
        #formula : ((o&m)-2s)^reverse(reverse(o&m)-2reverse(s))&m
        sliderAttacks = (((occupied_squares & mask) - (slider_square << 1)) ^
                        conversions.reverse_bitboard(conversions.reverse_bitboard(occupied_squares & mask) - (conversions.reverse_bitboard(slider_square) << 1))) & mask

        return sliderAttacks

    def rook_attacks(self,index:int,color:str = "white")->int:
        own_pieces = sum(self.board[color].values()) 
        hmask = constants.ROOK_MASK_RANK[index]
        vmask = constants.ROOK_MASK_FILE[index]
        rookAttacks = self.hyperbola_quint(index,hmask,color) | self.hyperbola_quint(index,vmask,color)
        rookAttacks &= ~own_pieces 
        return rookAttacks
    def bishop_attacks(self,index:int)->int:
        ... 
