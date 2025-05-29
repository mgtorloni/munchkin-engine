import constants
import conversions
class BoardRep:
    """Turns board into a bitboards"""
    def __init__(self):
        self.bitboard_black={
            "pawn": 0,
            "knight": 0,
            "bishop": 0,
            "queen": 0,
            "rook": 0,
            "king": 0
        }
        self.bitboard_white = { 
            "pawn": 0,
            "knight": 0,
            "bishop": 0,
            "queen": 0,
            "rook": 0,
            "king": 0        
        }
    
    def unset_bit(self,square:int,piece:str,color = "white"):
        if color.lower() == "white": 
            self.bitboard_white[piece] &= ~square
            return self.bitboard_white
        elif color.lower() == "black":
            self.bitboard_black[piece] &= ~square
            return self.bitboard_black
        else:
            raise ValueError("Color must be either 'white' or 'black'")

    def set_bit(self,square:int, piece: str,color = "white") -> int:
        """Set piece on a bit"""
        if color.lower() == "white": 
            self.bitboard_white[piece] |= square
            return self.bitboard_white
        elif color.lower() == "black":
            self.bitboard_black[piece] |= square
            return self.bitboard_black
        else:
            raise ValueError("Color must be either 'white' or 'black'")


    def full_bitboard(self):
        """Returns where all of the pieces are"""
        full_bitboard = 0
        for bitboard in self.bitboard_white.values():
            full_bitboard |= bitboard 
        for bitboard in self.bitboard_black.values():
            full_bitboard |= bitboard 
        return full_bitboard

    def initial_position(self)->tuple[dict,dict]:
        """Set initial positions of pieces on the chess board"""
        
        self.bitboard_white = constants.INITIAL_WHITE
        self.bitboard_black = constants.INITIAL_BLACK 
        print(self.bitboard_white)
        print(self.bitboard_black)
        return (self.bitboard_white,self.bitboard_black)

class ValidMoves:
    #TODO: REFACTOR THIS, WE GOT WAY TOO MANY OCCURRENCES OF "own_pieces" AND "occupied_squares", WE CAN'T
    #JUST PUT IT IN INIT BECAUSE IT HAS TO BE UPDATED AFTER EVERY MOVE AND THE IDEA IS CALLING
    #ONE OF THE FUNCTIONS DEPENDING ON WHAT PIECE WE CLICK ON
    def __init__(self,boardrep: BoardRep):
        self.board = {"white":boardrep.bitboard_white,"black":boardrep.bitboard_black}
        self.notHFile = ~sum(1 << (7 + 8 * i) for i in range(8))&0xFFFFFFFFFFFFFFFF
        self.notGHFile = (self.notHFile & (~sum(1<< (6+8*i) for i in range(8))))&0xFFFFFFFFFFFFFFFF
        self.notAFile = ~sum(1 << (8 * i) for i in range(8))&0xFFFFFFFFFFFFFFFF
        self.notABFile = (self.notAFile & (~sum(1<< (1+8*i) for i in range(8))))&0xFFFFFFFFFFFFFFFF

    def knight_attacks(self,piece_bitboard:int,color:str="white")-> int:
        own_pieces = sum(self.board[color].values()) 
        knight_attacks = ((piece_bitboard >> 15) & self.notAFile) | ((piece_bitboard << 15) & self.notHFile) | \
                ((piece_bitboard << 10) & self.notABFile) | ((piece_bitboard >> 10) & self.notGHFile) | \
                  ((piece_bitboard << 17) & self.notAFile) | ((piece_bitboard >> 17) & self.notHFile) | \
                  ((piece_bitboard << 6)  & self.notGHFile) | ((piece_bitboard >> 6)  & self.notABFile)

        #TODO: HARD CODE VALUES LIKE WE DID WITH BISHOPS,ROOKS AND QUEENS 
        knight_attacks &= ~own_pieces
        return knight_attacks
    
    def king_attacks(self,piece_bitboard:int,color:str="white")->int:
        own_pieces = sum(self.board[color].values())
        king_attacks = ((piece_bitboard >> 1) & self.notHFile) | ((piece_bitboard << 1) & self.notAFile) |  \
               ((piece_bitboard >> 7) & self.notAFile) | ((piece_bitboard >> 9) & self.notHFile) |  \
               ((piece_bitboard << 7) & self.notHFile) | ((piece_bitboard << 9) & self.notAFile) |  \
               (piece_bitboard >> 8) | (piece_bitboard << 8)
        
        opposite = "black" if color=="white" else "white" # opposite color to the one given in the argument above
        board_op = self.board[opposite] # opposite board 
        king_op = board_op["king"] #opposite color king
        #TODO: HARD CODE VALUES LIKE WE DID WITH BISHOPS,ROOKS AND QUEENS 
        opposite_king_attacks = ((king_op>> 1) & self.notHFile) | ((king_op<< 1) & self.notAFile) |  \
               ((king_op>> 7) & self.notAFile) | ((king_op>> 9) & self.notHFile) |  \
               ((king_op<< 7) & self.notHFile) | ((king_op<< 9) & self.notAFile) |  \
               (king_op>> 8) | (king_op<< 8)
        king_attacks &= ~(self.knight_attacks(board_op["knight"],opposite)|
                          opposite_king_attacks|
                          self.pawn_attacks(board_op["pawn"],opposite)|
                          self.queen_attacks(board_op["queen"].bit_length() - 1,opposite)|
                          self.bishop_attacks(board_op["bishop"].bit_length() - 1,opposite)|
                          self.rook_attacks(board_op["rook"].bit_length() - 1,opposite))
        king_attacks &= ~own_pieces 
        return king_attacks

    def pawn_attacks(self,piece_bitboard:int,color:str="white")->int:
        own_pieces = sum(self.board[color].values()) 
        occupied_squares = sum(self.board["white"].values())|sum(self.board["black"].values())
        if color == "white":
            enemy_pieces = sum(self.board["black"].values()) 
            attacks = ((piece_bitboard<< 9) & self.notAFile) | ((piece_bitboard<< 7) & self.notHFile)
            attacks &=enemy_pieces
            if piece_bitboard in [256, 512, 1024, 2048, 4096, 8192, 16384, 32768]:
                moves = ((piece_bitboard<<16)|(piece_bitboard<<8)) & ~occupied_squares #if we are in the initial squares we can move two
            else:
                moves = (piece_bitboard<<8) &~ occupied_squares
            return attacks|moves
        elif color=="black":  # Black pawns attack downward
            enemy_pieces = sum(self.board["white"].values()) 
            attacks = ((piece_bitboard>> 9) & self.notAFile) | ((piece_bitboard>> 7) & self.notHFile)
            attacks &=enemy_pieces
            if piece_bitboard in [281474976710656, 562949953421312, 1125899906842624, 2251799813685248, 4503599627370496, 9007199254740992, 18014398509481984, 36028797018963968]:
                moves = ((piece_bitboard>>16)|(piece_bitboard>>8)) & ~occupied_squares #if we are in the initial squares we can move two
            else:
                moves = (piece_bitboard>>8) & ~occupied_squares
            return attacks|moves

    def hyperbola_quint(self,slider_bitboard:int,mask:int,color:str = "white")->int: #slider attacks formula
        occupied_squares = sum(self.board["white"].values())|sum(self.board["black"].values()) #all occupied squares
        #formula : ((o&m)-2s)^reverse(reverse(o&m)-2reverse(s))&m
        sliderAttacks = (((occupied_squares & mask) - (slider_bitboard<< 1)) ^
                        conversions.reverse_bitboard(conversions.reverse_bitboard(occupied_squares & mask) - (conversions.reverse_bitboard(slider_bitboard) << 1))) & mask
        return sliderAttacks

    def rook_attacks(self,piece_bitboard:int,color:str = "white")->int:
        own_pieces = sum(self.board[color].values()) 
        index = conversions.square_to_index(piece_bitboard)
        hmask = constants.ROOK_MASK_RANK[index]
        vmask = constants.ROOK_MASK_FILE[index]
        rookAttacks = self.hyperbola_quint(piece_bitboard,hmask,color) | self.hyperbola_quint(piece_bitboard,vmask,color)
        rookAttacks &= ~own_pieces 
        return rookAttacks

    def bishop_attacks(self,piece_bitboard:int,color:str = "white")->int:
        own_pieces = sum(self.board[color].values())
        index = conversions.square_to_index(piece_bitboard)
        right_mask = constants.BISHOP_45DIAG[index]
        left_mask = constants.BISHOP_135DIAG[index]
        bishopAttacks = self.hyperbola_quint(piece_bitboard,right_mask,color) | self.hyperbola_quint(piece_bitboard,left_mask,color)
        bishopAttacks&= ~own_pieces
        return bishopAttacks

    def queen_attacks(self,piece_bitboard:int,color:str = "white")->int:
        return self.rook_attacks(piece_bitboard,color)|self.bishop_attacks(piece_bitboard,color)
