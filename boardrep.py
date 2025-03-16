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
        """Set initial positions of pieces on the chess board"""
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
    #TODO: REFACTOR THIS, WE GOT WAY TOO MANY OCCURRENCES OF "own_pieces" AND "occupied_squares", WE CAN'T
    #JUST PUT IT IN INIT BECAUSE IT HAS TO BE UPDATED AFTER EVERY MOVE AND THE IDEA IS CALLING
    #ONE OF THE FUNCTIONS DEPENDING ON WHAT PIECE WE CLICK ON
    def __init__(self,boardrep: BoardRep):
        self.board= {"white":boardrep.bitboard_white,"black":boardrep.bitboard_black}
        self.notHFile=~sum(1 << (7 + 8 * i) for i in range(8))&0xFFFFFFFFFFFFFFFF
        self.notGHFile= (self.notHFile & (~sum(1<< (6+8*i) for i in range(8))))&0xFFFFFFFFFFFFFFFF
        self.notAFile=~sum(1 << (8 * i) for i in range(8))&0xFFFFFFFFFFFFFFFF
        self.notABFile= (self.notAFile & (~sum(1<< (1+8*i) for i in range(8))))&0xFFFFFFFFFFFFFFFF

    def knight_attacks(self,index:int,color:str="white")-> int:
        own_pieces = sum(self.board[color].values()) 
        piece_square = 1<<index
        knight_attacks = ((piece_square >> 15) & self.notAFile) | ((piece_square << 15) & self.notHFile) | \
                ((piece_square << 10) & self.notABFile) | ((piece_square >> 10) & self.notGHFile) | \
                  ((piece_square << 17) & self.notHFile) | ((piece_square >> 17) & self.notAFile) | \
                  ((piece_square << 6)  & self.notGHFile) | ((piece_square >> 6)  & self.notABFile)
        knight_attacks &= ~own_pieces
        return knight_attacks
    
    def king_attacks(self,index:int,color:str="white")->int:
        piece_square = 1<<index
        king_attacks = ((piece_square >> 1) & self.notHFile) | ((piece_square << 1) & self.notAFile) |  \
               ((piece_square >> 7) & self.notAFile) | ((piece_square >> 9) & self.notHFile) |  \
               ((piece_square << 7) & self.notHFile) | ((piece_square << 9) & self.notAFile) |  \
               (piece_square >> 8) | (piece_square << 8)
        #TODO: king_attacks &= ~(knight_attacks(index,color = "opposite color")|...)
        return king_attacks

    def pawn_attacks(self,index:int,color:str="white")->int:
        own_pieces = sum(self.board[color].values()) 
        occupied_squares = sum(self.board["white"].values())|sum(self.board["black"].values())
        piece_square = 1<<index
        if color == "white":
            enemy_pieces = sum(self.board["black"].values()) 
            attacks = ((piece_square << 9) & self.notAFile) | ((piece_square << 7) & self.notHFile)
            attacks &=enemy_pieces
            moves = (piece_square<<8) &~ occupied_squares
            return attacks|moves
        elif color=="black":  # Black pawns attack downward
            enemy_pieces = sum(self.board["white"].values()) 
            attacks = ((piece_square >> 9) & self.notAFile) | ((piece_square >> 7) & self.notHFile)
            attacks &=enemy_pieces
            moves = (piece_square>>8) &~ occupied_squares
            return attacks|moves

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

    def bishop_attacks(self,index:int,color:str = "white")->int:
        own_pieces = sum(self.board[color].values())
        right_mask = constants.BISHOP_45DIAG[index]
        left_mask = constants.BISHOP_135DIAG[index]
        bishopAttacks = self.hyperbola_quint(index,right_mask,color) | self.hyperbola_quint(index,left_mask,color)
        bishopAttacks&= ~own_pieces
        return bishopAttacks
    def queen_attacks(self,index:int,color:str = "white")->int:
        return self.rook_attacks(index,color)|self.bishop_attacks(index,color)
