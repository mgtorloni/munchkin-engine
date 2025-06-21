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
    
    def copy(self):
        """Creates a copy of the BoardRep object."""
        new_rep = BoardRep()
        new_rep.bitboard_white = self.bitboard_white.copy()
        new_rep.bitboard_black = self.bitboard_black.copy()
        return new_rep

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
        return (self.bitboard_white,self.bitboard_black)

    def capture_at(self,square: int, color:str):
        """Removes that piece out of the general bitboard"""
        bitboard = (self.bitboard_white if color.lower()=="white" else self.bitboard_black)
        for piece, bb in bitboard.items():
            if bb & square:
                bitboard[piece] &=~square
                #break

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

    

    def king_attacks(self,king_bitboard:int,color:str="white")->int:
        """This returns only the raw attacks, see is_square_attacked for checking if the king is in check"""
        own_pieces = sum(self.board[color].values()) 
        attacks = ((king_bitboard >> 1) & self.notHFile) | ((king_bitboard << 1) & self.notAFile) |  \
           ((king_bitboard >> 7) & self.notAFile) | ((king_bitboard >> 9) & self.notHFile) |  \
           ((king_bitboard << 7) & self.notHFile) | ((king_bitboard << 9) & self.notAFile) |  \
           (king_bitboard >> 8) | (king_bitboard << 8)
        return attacks & ~own_pieces

    def is_square_attacked(self,square_bb:int,attacker_color:str) ->bool:
        """Checks if a (single) square is under attack"""
        attacker_board = self.board[attacker_color]
        defender_color = "black" if attacker_color =="white" else "white"
        if attacker_color == "white":
            #if the color of the attacker is white then the pawn atttacks up meaning
            #we need to check if there are pawns behind us
            potential_attackers = ((square_bb>>9) & self.notHFile) | ((square_bb>>7) & self.notAFile)
            if potential_attackers & attacker_board["pawn"]:
                return True
        elif attacker_color == "black":
            #if the color of the attacker is white then the pawn atttacks down meaning
            #we need to check if there are pawns above us
            potential_attackers = ((square_bb<<9) & self.notAFile) | ((square_bb<<7) & self.notHFile)
            if potential_attackers & attacker_board["pawn"]:
                return True

        if self.knight_attacks(square_bb, defender_color) & attacker_board["knight"]:
            return True #if there is a knight a 'knight-away' from this square it means that it is being attacked by that knight 
        
        if self.queen_attacks(square_bb, defender_color) & attacker_board["queen"]:
            return True #if there is a queen a 'queen-away' from this square it means that it is being attacked by that queen 

        if self.bishop_attacks(square_bb, defender_color) & attacker_board["bishop"]:
            return True #if there is a bishop a 'bishop-away' from this square it means that it is being attacked by that bishop 

        if self.rook_attacks(square_bb, defender_color) & attacker_board["rook"]:
            return True #if there is a rook a 'rook-away' from this square it means that it is being attacked by that rook 
        if self.king_attacks(square_bb,defender_color) & attacker_board["king"]:
            return True

        return False #if no pieces attacks that square, then return false

    def knight_attacks(self,piece_bitboard:int,color:str="white")-> int:
        """Finds which square a knight is attacking"""
        
        own_pieces = sum(self.board[color].values()) 
        knight_attacks = ((piece_bitboard >> 15) & self.notAFile) | ((piece_bitboard << 15) & self.notHFile) | \
                ((piece_bitboard << 10) & self.notABFile) | ((piece_bitboard >> 10) & self.notGHFile) | \
                  ((piece_bitboard << 17) & self.notAFile) | ((piece_bitboard >> 17) & self.notHFile) | \
                  ((piece_bitboard << 6)  & self.notGHFile) | ((piece_bitboard >> 6)  & self.notABFile)

        #TODO: HARD CODE VALUES LIKE WE DID WITH BISHOPS,ROOKS AND QUEENS 
        knight_attacks &= ~own_pieces
        return knight_attacks
    


    def pawn_attacks(self,pawn_bitboard:int,color:str="white")->int:
        """Finds which squares a pawn is attacking"""

        #no need for own_pieces here since the pawn stops no matter if it is your own or the enemy's pieces
        occupied_squares = sum(self.board["white"].values())|sum(self.board["black"].values())

        if color == "white":
            enemy_pieces = sum(self.board["black"].values()) #get a single bitboard to locate where all pieces are 

            attacks = ((pawn_bitboard<< 9) & self.notAFile) | ((pawn_bitboard<< 7) & self.notHFile) #raw attacks to its diagonals
            attacks &= enemy_pieces #there need to be a piece there for a pawn to move there

            if pawn_bitboard in [256, 512, 1024, 2048, 4096, 8192, 16384, 32768]:
                moves = ((pawn_bitboard<<16)|(pawn_bitboard<<8)) & ~occupied_squares #if we are in the initial squares we can move two
            else:
                moves = (pawn_bitboard<<8) &~ occupied_squares
            return attacks|moves

        elif color=="black":  # black pawns attack downward
            enemy_pieces = sum(self.board["white"].values()) 

            attacks = ((pawn_bitboard>> 9) & self.notAFile) | ((pawn_bitboard>> 7) & self.notHFile) #raw attacks to its diagonals
            attacks &= enemy_pieces #there need to be a piece there for a pawn to move there

            if pawn_bitboard in [281474976710656, 562949953421312, 1125899906842624, 2251799813685248, 4503599627370496, 9007199254740992, 18014398509481984, 36028797018963968]:
                moves = ((pawn_bitboard>>16)|(pawn_bitboard>>8)) & ~occupied_squares #if we are in the initial squares we can move two
            else:
                moves = (pawn_bitboard>>8) & ~occupied_squares
            return attacks|moves #combine the attacks and moves

    def hyperbola_quint(self,slider_bitboard:int,mask:int,color:str = "white")->int: #slider attacks formula
        """Uses the hyperbola quintessential formula to calculate how the slider attacks stop at a piece on their way"""

        #no need for own_pieces here since the slider stops no matter if it is your own or the enemy's pieces
        occupied_squares = sum(self.board["white"].values())|sum(self.board["black"].values()) #all occupied squares

        #formula : ((o&m)-2s)^reverse(reverse(o&m)-2reverse(s))&m
        sliderAttacks = (((occupied_squares & mask) - (slider_bitboard<< 1)) ^
                        conversions.reverse_bitboard(conversions.reverse_bitboard(occupied_squares & mask) - (conversions.reverse_bitboard(slider_bitboard) << 1))) & mask

        return sliderAttacks

    def rook_attacks(self,rook_bitboard:int,color:str = "white")->int:
        """Finds which square a rook is attacking"""

        own_pieces = sum(self.board[color].values()) 
        index = conversions.square_to_index(rook_bitboard)

        #refer to generating functions to see how these were obtained 
        hmask = constants.ROOK_MASK_RANK[index] 
        vmask = constants.ROOK_MASK_FILE[index]

        rookAttacks = self.hyperbola_quint(rook_bitboard,hmask,color) | self.hyperbola_quint(rook_bitboard,vmask,color)
        rookAttacks &= ~own_pieces 
        return rookAttacks

    def bishop_attacks(self,bishop_bitboard:int,color:str = "white")->int:
        """Finds which squares a bishop is attacking""" 
        own_pieces = sum(self.board[color].values())
        index = conversions.square_to_index(bishop_bitboard)

        #refer to generating functions to see how these were obtained 
        right_mask = constants.BISHOP_45DIAG[index]
        left_mask = constants.BISHOP_135DIAG[index]

        bishopAttacks = self.hyperbola_quint(bishop_bitboard,right_mask,color) | self.hyperbola_quint(bishop_bitboard,left_mask,color)
        bishopAttacks &= ~own_pieces
        return bishopAttacks

    def queen_attacks(self,queen_bitboard:int,color:str = "white")->int: #queens are just a bishop and a rook in one piece
        return self.rook_attacks(queen_bitboard,color)|self.bishop_attacks(queen_bitboard,color) 
