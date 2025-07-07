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

        self.white_kingside_ctl = True
        self.white_queenside_ctl = True
        self.black_kingside_ctl = True
        self.black_queenside_ctl = True
    
    def copy(self):
        """Creates a copy of the BoardRep object."""
        new_rep = BoardRep()
        new_rep.bitboard_white = self.bitboard_white.copy()
        new_rep.bitboard_black = self.bitboard_black.copy()
        
        new_rep.white_kingside_ctl = self.white_kingside_ctl
        new_rep.white_queenside_ctl = self.white_queenside_ctl
        
        new_rep.black_kingside_ctl = self.black_kingside_ctl
        new_rep.black_queenside_ctl = self.black_queenside_ctl
        
        return new_rep

    def unset_bit(self,square:int,piece:str,colour = "white"):
        if colour.lower() == "white": 
            self.bitboard_white[piece] &= ~square
            return self.bitboard_white
        elif colour.lower() == "black":
            self.bitboard_black[piece] &= ~square
            return self.bitboard_black

    def set_bit(self,square:int, piece: str,colour = "white") -> int:
        """Set piece on a bit"""
        if colour.lower() == "white": 
            self.bitboard_white[piece] |= square
            return self.bitboard_white
        elif colour.lower() == "black":
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

        self.white_kingside_ctl = True
        self.white_queenside_ctl = True
        self.black_kingside_ctl = True
        self.black_queenside_ctl = True
        return (self.bitboard_white,self.bitboard_black)

    def capture_at(self,square: int, colour:str):
        """Removes that piece out of the general bitboard"""
        bitboard = (self.bitboard_white if colour.lower()=="white" else self.bitboard_black)
        for piece, bb in bitboard.items():
            if bb & square:
                bitboard[piece] &=~square
                break

class ValidMoves:
    def __init__(self,boardrep: BoardRep):
        self.board_rep = boardrep
        self.board = {"white":self.board_rep.bitboard_white,"black":self.board_rep.bitboard_black}

        self.white_pieces = sum(self.board["white"].values())
        self.black_pieces = sum(self.board["black"].values())
        self.occupied_squares = self.white_pieces|self.black_pieces

        self.notHFile = ~sum(1 << (7 + 8 * i) for i in range(8))
        self.notGHFile = (self.notHFile & (~sum(1<< (6+8*i) for i in range(8))))
        self.notAFile = ~sum(1 << (8 * i) for i in range(8))
        self.notABFile = (self.notAFile & (~sum(1<< (1+8*i) for i in range(8))))

    def king_attacks(self,king_bitboard:int,colour:str="white")->int:
        """This returns only the raw attacks, see is_square_attacked for checking if the king is in check"""
        own_pieces = self.white_pieces if colour == "white" else self.black_pieces 
        attacks = ((king_bitboard >> 1) & self.notHFile) | ((king_bitboard << 1) & self.notAFile) |  \
           ((king_bitboard >> 7) & self.notAFile) | ((king_bitboard >> 9) & self.notHFile) |  \
           ((king_bitboard << 7) & self.notHFile) | ((king_bitboard << 9) & self.notAFile) |  \
           (king_bitboard >> 8) | (king_bitboard << 8)
        
        # Add a 64-bit mask to discard any "off-board" bits before returning
        return attacks & 0xFFFFFFFFFFFFFFFF & ~own_pieces

    """
    def castling_right(self,colour:str="white")->bool:
        attacker_colour = "black" if colour == "white" else "white"  
        castling_queen = [] #castling queen-side squares
        castling_king = [] #castling king-side squares

        #if any square on the queen/king side is attacked return false
        queen_side = any(self.is_square_attacked(square, attacker_colour) for square in castling_queen) 
        king_side = any(self.is_square_attacked(square, attacker_colour) for square in castling_king) 
        if self.occupied_squares & castling_queen:
    """  

    def is_square_attacked(self,square_bb:int,attacker_colour:str) ->bool:
        """Checks if a (single) square is under attack"""
        attacker_board = self.board[attacker_colour]
        defender_colour = "black" if attacker_colour =="white" else "white"
        if attacker_colour == "white":
            #if the colour of the attacker is white then the pawn atttacks up meaning
            #we need to check if there are pawns behind us
            potential_attackers = ((square_bb>>9) & self.notHFile) | ((square_bb>>7) & self.notAFile)
            if potential_attackers & attacker_board["pawn"]:
                return True
        elif attacker_colour == "black":
            #if the colour of the attacker is white then the pawn atttacks down meaning
            #we need to check if there are pawns above us
            potential_attackers = ((square_bb<<9) & self.notAFile) | ((square_bb<<7) & self.notHFile)
            if potential_attackers & attacker_board["pawn"]:
                return True

        if self.knight_attacks(square_bb, defender_colour) & attacker_board["knight"]:
            return True #if there is a knight a 'knight-away' from this square it means that it is being attacked by that knight 
        
        if self.queen_attacks(square_bb, defender_colour) & attacker_board["queen"]:
            return True #if there is a queen a 'queen-away' from this square it means that it is being attacked by that queen 

        if self.bishop_attacks(square_bb, defender_colour) & attacker_board["bishop"]:
            return True #if there is a bishop a 'bishop-away' from this square it means that it is being attacked by that bishop 

        if self.rook_attacks(square_bb, defender_colour) & attacker_board["rook"]:
            return True #if there is a rook a 'rook-away' from this square it means that it is being attacked by that rook 
        if self.king_attacks(square_bb,defender_colour) & attacker_board["king"]:
            return True

        return False #if no pieces attacks that square, then return false

    def knight_attacks(self,piece_bitboard:int,colour:str="white")-> int:
        """Finds which square a knight is attacking"""
        
        own_pieces = self.white_pieces if colour == "white" else self.black_pieces 
        knight_attacks = ((piece_bitboard >> 15) & self.notAFile) | ((piece_bitboard << 15) & self.notHFile) | \
                ((piece_bitboard << 10) & self.notABFile) | ((piece_bitboard >> 10) & self.notGHFile) | \
                  ((piece_bitboard << 17) & self.notAFile) | ((piece_bitboard >> 17) & self.notHFile) | \
                  ((piece_bitboard << 6)  & self.notGHFile) | ((piece_bitboard >> 6)  & self.notABFile)

        #TODO: HARD CODE VALUES LIKE WE DID WITH BISHOPS,ROOKS AND QUEENS 
        knight_attacks &= ~own_pieces
        return knight_attacks
    
    def pawn_attacks(self,pawn_bitboard:int,colour:str="white")->int:
        """Finds which squares a pawn is attacking"""
        
        if colour == "white":
            enemy_pieces = sum(self.board["black"].values()) #get a single bitboard to locate where all pieces are 

            attacks = ((pawn_bitboard<< 9) & self.notAFile) | ((pawn_bitboard<< 7) & self.notHFile) #raw attacks to its diagonals
            attacks &= enemy_pieces #there need to be a piece there for a pawn to move there

            if pawn_bitboard in [256, 512, 1024, 2048, 4096, 8192, 16384, 32768]:
                moves = ((pawn_bitboard<<16)|(pawn_bitboard<<8)) & ~self.occupied_squares #if we are in the initial squares we can move two
            else:
                moves = (pawn_bitboard<<8) &~ self.occupied_squares
            return attacks|moves

        elif colour=="black":  # black pawns attack downward
            enemy_pieces = sum(self.board["white"].values()) 

            attacks = ((pawn_bitboard>> 9) & self.notAFile) | ((pawn_bitboard>> 7) & self.notHFile) #raw attacks to its diagonals
            attacks &= enemy_pieces #there need to be a piece there for a pawn to move there

            if pawn_bitboard in [281474976710656, 562949953421312, 1125899906842624, 2251799813685248, 4503599627370496, 9007199254740992, 18014398509481984, 36028797018963968]:
                moves = ((pawn_bitboard>>16)|(pawn_bitboard>>8)) & ~self.occupied_squares #if we are in the initial squares we can move two
            else:
                moves = (pawn_bitboard>>8) & ~self.occupied_squares
            return attacks|moves #combine the attacks and moves

    def hyperbola_quint(self,slider_bitboard:int,mask:int,colour:str = "white")->int: #slider attacks formula
        """Uses the hyperbola quintessential formula to calculate how the slider attacks stop at a piece on their way"""
        #formula : ((o&m)-2s)^reverse(reverse(o&m)-2reverse(s))&m
        sliderAttacks = (((self.occupied_squares & mask) - (slider_bitboard<< 1)) ^
                        conversions.reverse_bitboard(conversions.reverse_bitboard(self.occupied_squares & mask) - (conversions.reverse_bitboard(slider_bitboard) << 1))) & mask

        return sliderAttacks

    def rook_attacks(self,rook_bitboard:int,colour:str = "white")->int:
        """Finds which square a rook is attacking"""
        if rook_bitboard ==0:
            return 0

        own_pieces = sum(self.board[colour].values()) 
        index = conversions.square_to_index(rook_bitboard)

        #refer to generating functions to see how these were obtained 
        hmask = constants.ROOK_MASK_RANK[index] 
        vmask = constants.ROOK_MASK_FILE[index]

        rookAttacks = self.hyperbola_quint(rook_bitboard,hmask,colour) | self.hyperbola_quint(rook_bitboard,vmask,colour)
        rookAttacks &= ~own_pieces 
        return rookAttacks

    def bishop_attacks(self,bishop_bitboard:int,colour:str = "white")->int:
        """Finds which squares a bishop is attacking""" 
        own_pieces = sum(self.board[colour].values())
        index = conversions.square_to_index(bishop_bitboard)

        #refer to generating functions to see how these were obtained 
        right_mask = constants.BISHOP_45DIAG[index]
        left_mask = constants.BISHOP_135DIAG[index]

        bishopAttacks = self.hyperbola_quint(bishop_bitboard,right_mask,colour) | self.hyperbola_quint(bishop_bitboard,left_mask,colour)
        bishopAttacks &= ~own_pieces
        return bishopAttacks

    def queen_attacks(self,queen_bitboard:int,colour:str = "white")->int: #queens are just a bishop and a rook in one piece
        return self.rook_attacks(queen_bitboard,colour)|self.bishop_attacks(queen_bitboard,colour) 

    def generate_all_legal_moves(self,colour:str)->list:
        """Generates a list of all legal moves for a given colour."""
        legal_moves = []
        opponent_colour = "black" if colour == "white" else "white"
        attack_functions = {
                "pawn":self.pawn_attacks,"rook":self.rook_attacks,
                "knight":self.knight_attacks,"bishop":self.bishop_attacks,
                "queen":self.queen_attacks,"king":self.king_attacks}

        for piece,bitboard in self.board[colour].items():
            source_squares = bitboard
            print("Piece:"+piece+", Colour:"+colour)
            
            while source_squares:
                source = source_squares & -source_squares
                pseudo_legal_moves = attack_functions[piece](source,colour)

                target_squares = pseudo_legal_moves
                while target_squares:
                    target = target_squares & -target_squares

                    virtual_board = self.board_rep.copy()
                    virtual_board.capture_at(target, opponent_colour)
                    virtual_board.unset_bit(source, piece,colour)
                    virtual_board.set_bit(target,piece,colour)

                    virtual_validator = ValidMoves(virtual_board)
                    king_bitboard = virtual_board.bitboard_white["king"] if colour=="white" else virtual_board.bitboard_black["king"]
                    print(f"square_to_index result: {conversions.square_to_index(source)}")
                    if not virtual_validator.is_square_attacked(king_bitboard,opponent_colour):
                        legal_moves.append((source,target))

                    target_squares &= target_squares -1 #move to the next target square
                #print(target_squares)
                source_squares &= source_squares - 1
        print("==============================================")
        return legal_moves

