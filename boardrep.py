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

        #[King moved, King-side castling, queen-side castling] 
        self.castling_white = [True,True]
        self.castling_black = [True,True]

        self.en_passant_square = 0 #Stores the target square for potential EP capture
    
    def unset_bit(self,square:int,piece:str,colour = "white"):
        if colour.lower() == "white": 
            self.bitboard_white[piece] &= ~square
            return self.bitboard_white

        elif colour.lower() == "black":
            self.bitboard_black[piece] &= ~square
            return self.bitboard_black

    def set_bit(self,square:int, piece: str,colour="white") -> int:
        """Set piece on a bit"""

        if colour.lower() == "white": 
            self.bitboard_white[piece] |= square
            return self.bitboard_white

        elif colour.lower() == "black":
            self.bitboard_black[piece] |= square
            return self.bitboard_black
        else:
            raise ValueError("Color must be either 'white' or 'black'")

    def make_move(self, move: tuple, moved_piece:str, colour: str):
        source_square,target_square = move

        unmake_info = {
            "white": self.bitboard_white.copy(),
            "black": self.bitboard_black.copy(),
            "en_passant_square": self.en_passant_square,
            "castling_white": list(self.castling_white),
            "castling_black": list(self.castling_black)
        }

        opponent_colour = "black" if colour=="white" else "white"
        opponent_board = self.bitboard_black if colour == "white" else self.bitboard_white


        ep_square_before_move = self.en_passant_square
        self.en_passant_square = 0

        if moved_piece == 'pawn' and target_square == ep_square_before_move:
            captured_pawn_square = (target_square >> 8) if colour == "white" else (target_square << 8)
            self.unset_bit(captured_pawn_square, 'pawn', opponent_colour)
        else: 
            captured_piece = next((p for p, bb in opponent_board.items() if bb & target_square), None)
            if captured_piece:
                self.unset_bit(target_square, captured_piece, opponent_colour)

        if moved_piece == "pawn" and abs(conversions.square_to_index(source_square) - conversions.square_to_index(target_square)) == 16:
            self.en_passant_square = (source_square << 8) if colour == "white" else (source_square >> 8)

        if moved_piece == 'king':
            if colour == 'white':
                self.castling_white = [False, False]
            else:
                self.castling_black = [False, False]

        if moved_piece == 'rook':
            if colour == 'white':
                if source_square == 1: #a1 rook
                    self.castling_white[1] = False
                elif source_square == 1<<7:
                    self.castling_white[0] = False
            if colour == 'black':
                if source_square == 1<<56:
                    self.castling_black[1] = False
                elif source_square == 1<<63:
                    self.castling_black[0] = False

        is_castle = moved_piece == 'king' and abs(conversions.square_to_index(source_square) - conversions.square_to_index(target_square)) == 2
        if is_castle:
            # king-side castle
            if target_square > source_square:
                rook_start_square = target_square << 1
                rook_end_square = target_square >> 1
            # Queen-side castle
            else:
                rook_start_square = target_square >> 2
                rook_end_square = target_square << 1

            self.unset_bit(rook_start_square, 'rook', colour)
            self.set_bit(rook_end_square, 'rook', colour)

        self.unset_bit(source_square, moved_piece, colour)
        self.set_bit(target_square, moved_piece, colour)
        return unmake_info


    def unmake_move(self, unmake_info: dict):
        self.bitboard_white = unmake_info["white"]
        self.bitboard_black = unmake_info["black"]
        self.en_passant_square = unmake_info["en_passant_square"]
        self.castling_white = unmake_info["castling_white"]
        self.castling_black = unmake_info["castling_black"]

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

        self.castling_white = [True,True]
        self.castling_black = [True,True]

        self.en_passant_square = 0

        return (self.bitboard_white,self.bitboard_black)


class ValidMoves:
    def __init__(self,boardrep: BoardRep):
        self.board_rep = boardrep

        self.white_pieces = sum(self.board_rep.bitboard_white.values())
        self.black_pieces = sum(self.board_rep.bitboard_black.values())

        self.occupied_squares = self.white_pieces|self.black_pieces

        self.FILE_A = 0x0101010101010101
        self.FILE_H = 0x8080808080808080
        self.FILE_AB = self.FILE_A | (self.FILE_A << 1);
        self.FILE_GH = self.FILE_H | (self.FILE_H >> 1);


    def king_attacks(self,king_bitboard:int,colour:str="white")->int:
        """This returns only the raw attacks, see is_square_attacked for checking if the king is in check"""
        own_pieces = self.white_pieces if colour == "white" else self.black_pieces 
        attacks = ((king_bitboard >> 1) & ~self.FILE_H) | ((king_bitboard << 1) & ~self.FILE_A) |  \
           ((king_bitboard >> 7) & ~self.FILE_A) | ((king_bitboard >> 9) & ~self.FILE_H) |  \
           ((king_bitboard << 7) & ~self.FILE_H) | ((king_bitboard << 9) & ~self.FILE_A) |  \
           (king_bitboard >> 8) | (king_bitboard << 8)
        
        # Add a 64-bit mask to discard any "off-board" bits before returning
        return attacks & 0xFFFFFFFFFFFFFFFF & ~own_pieces

    def can_castle(self,colour:str="white")->(bool,bool):
        """Returns a tuple showing if that colour can castle king-side or queen-side""" 
        attacker_colour = "black" if colour == "white" else "white"  
        castling_queen = 1<<3|1<<2 if colour=="white" else 1<<59|1<<58 #king path queen-side squares
        castling_king = 1<<5|1<<6 if colour =="white" else 1<<61|1<<62 #king path king-side squares
        sqrs_att_queen_sd = False
        sqrs_att_king_sd = False 
        result = (True,True)
        rights = self.board_rep.castling_white if colour == "white" else self.board_rep.castling_black
        #if any square on the queen/king side is attacked return false
        if colour == "white":
            sqrs_att_queen_sd = any(self.is_square_attacked(square, colour) for square in [1<<4,1<<3,1<<2]) 
            sqrs_att_king_sd = any(self.is_square_attacked(square, colour) for square in [1<<4,1<<5,1<<6]) 
        if colour == "black":
            sqrs_att_queen_sd = any(self.is_square_attacked(square, colour) for square in [1<<60,1<<59,1<<58]) 
            sqrs_att_king_sd = any(self.is_square_attacked(square, colour) for square in [1<<60,1<<61,1<<62]) 

        if self.occupied_squares & castling_king or sqrs_att_king_sd or not rights[0]:
            result = (False,result[1])
        #If there is a piece in the way or any of the squares in the kings path is attacked or the rook on that side has moved return False on that side 
        if self.occupied_squares & castling_queen or sqrs_att_queen_sd or not rights[1]:
            result = (result[0],False) 
        return result

    def is_square_attacked(self,square_bb:int,defender_colour:str) ->bool:
        """Checks if a (single) square is under attack"""

        attacker_board = self.board_rep.bitboard_white if defender_colour== "black" else self.board_rep.bitboard_black

        if defender_colour == "black":
            #if the colour of the attacker is white then the pawn atttacks up meaning
            #we need to check if there are pawns behind us
            potential_attackers = ((square_bb>>9) & ~self.FILE_H) | ((square_bb>>7) & ~self.FILE_A)
            if potential_attackers & attacker_board["pawn"]:
                return True
        elif defender_colour == "white":
            #if the colour of the attacker is white then the pawn atttacks down meaning
            #we need to check if there are pawns above us
            potential_attackers = ((square_bb<<9) & ~self.FILE_A) | ((square_bb<<7) & ~self.FILE_H)
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
        """Finds which squares a knight is attacking"""
        
        own_pieces = self.white_pieces if colour == "white" else self.black_pieces 
        knight_attacks = ((piece_bitboard >> 15) & ~self.FILE_A) | \
                ((piece_bitboard << 15) & ~self.FILE_H) | \
                ((piece_bitboard << 10) & ~self.FILE_AB) | \
                ((piece_bitboard >> 10) & ~self.FILE_GH) | \
                ((piece_bitboard << 17) & ~self.FILE_A) | \
                ((piece_bitboard >> 17) & ~self.FILE_H) | \
                ((piece_bitboard << 6)  & ~self.FILE_GH) | \
                ((piece_bitboard >> 6)  & ~self.FILE_AB)

        #TODO: HARD CODE VALUES LIKE WE DID WITH BISHOPS,ROOKS AND QUEENS 
        knight_attacks &= ~own_pieces
        return knight_attacks & 0xFFFFFFFFFFFFFFFF #We have to and it with the board
        #otherwise shifting the bits would leave the board to a square we don't know of
        #and therefore can't do &self.notSOMEFILE
    
    def pawn_attacks(self,pawn_bitboard:int,colour:str="white")->int:
        """Finds which squares a pawn is attacking, including moves, captures, and en passant."""
        moves = 0
        attacks = 0
        en_passant_move = 0

        if colour == "white":
            enemy_pieces = self.black_pieces
            single_push = (pawn_bitboard << 8) & ~self.occupied_squares
            if single_push and (pawn_bitboard & constants.RANK_2):
                double_push = (pawn_bitboard << 16) & ~self.occupied_squares
                moves = single_push | double_push
            else:
                moves = single_push
            attacks = ((pawn_bitboard << 9) & ~self.FILE_A) | ((pawn_bitboard << 7) & ~self.FILE_H)
            attacks &= enemy_pieces
            if self.board_rep.en_passant_square:
                ep_attacks = ((pawn_bitboard << 9) & ~self.FILE_A) | ((pawn_bitboard << 7) & ~self.FILE_H)
                if ep_attacks & self.board_rep.en_passant_square:
                    en_passant_move = self.board_rep.en_passant_square

        elif colour == "black":
            enemy_pieces = self.white_pieces
            single_push = (pawn_bitboard >> 8) & ~self.occupied_squares
            if single_push and (pawn_bitboard & constants.RANK_7):
                double_push = (pawn_bitboard >> 16) & ~self.occupied_squares
                moves = single_push | double_push
            else:
                moves = single_push
            attacks = ((pawn_bitboard >> 9) & ~self.FILE_H) | ((pawn_bitboard >> 7) & ~self.FILE_A)
            attacks &= enemy_pieces
            if self.board_rep.en_passant_square:
                ep_attacks = ((pawn_bitboard >> 9) & ~self.FILE_H) | ((pawn_bitboard >> 7) & ~self.FILE_A)
                if ep_attacks & self.board_rep.en_passant_square:
                    en_passant_move = self.board_rep.en_passant_square

        return attacks | moves | en_passant_move

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

        
        own_pieces = self.white_pieces if colour == "white" else self.black_pieces 

        index = conversions.square_to_index(rook_bitboard)

        #refer to generating functions to see how these were obtained 
        hmask = constants.ROOK_MASK_RANK[index] 
        vmask = constants.ROOK_MASK_FILE[index]

        rookAttacks = self.hyperbola_quint(rook_bitboard,hmask,colour) | self.hyperbola_quint(rook_bitboard,vmask,colour)
        rookAttacks &= ~own_pieces 
        return rookAttacks

    def bishop_attacks(self,bishop_bitboard:int,colour:str = "white")->int:
        """Finds which squares a bishop is attacking""" 
        own_pieces = self.white_pieces if colour == "white" else self.black_pieces 
        index = conversions.square_to_index(bishop_bitboard)

        #refer to generating functions to see how these were obtained 
        right_mask = constants.BISHOP_45DIAG[index]
        left_mask = constants.BISHOP_135DIAG[index]

        bishopAttacks = self.hyperbola_quint(bishop_bitboard,right_mask,colour) | self.hyperbola_quint(bishop_bitboard,left_mask,colour)
        bishopAttacks &= ~own_pieces
        return bishopAttacks

    def queen_attacks(self,queen_bitboard:int,colour:str = "white")->int: #queens are just a bishop and a rook in one piece
        return self.rook_attacks(queen_bitboard,colour)|self.bishop_attacks(queen_bitboard,colour) 

    def rebuild_state(self):
        """Rebuilds the validator's internal state from the board representation."""
        self.white_pieces = sum(self.board_rep.bitboard_white.values())
        self.black_pieces = sum(self.board_rep.bitboard_black.values())
        self.occupied_squares = self.white_pieces | self.black_pieces

    def generate_all_legal_moves(self,colour:str)->list:
        """Generates a list of all legal moves for a given colour."""
        legal_moves = []
        castling_rights = self.can_castle(colour) 
        #print(castling_rights)
        opponent_colour = "black" if colour == "white" else "white"
        attack_functions = {
                "pawn":self.pawn_attacks,"rook":self.rook_attacks,
                "knight":self.knight_attacks,"bishop":self.bishop_attacks,
                "queen":self.queen_attacks,"king":self.king_attacks}

        if castling_rights[0]: # King-side
            if colour == "white":
                legal_moves.append((1<<4, 1<<6))
            else: # Black
                legal_moves.append((1<<60, 1<<62))

        if castling_rights[1]: # Queen-side
            if colour == "white":
                legal_moves.append((1<<4, 1<<2))
            else: # Black
                legal_moves.append((1<<60, 1<<58))

        current_player_bb = self.board_rep.bitboard_white if colour == "white" else self.board_rep.bitboard_black

        for piece,bitboard in current_player_bb.items():
            source_squares = bitboard
            #print("Piece:"+piece+", Colour:"+colour)
            
            while source_squares:
                source = source_squares & -source_squares
                pseudo_legal_moves = attack_functions[piece](source,colour)

                target_squares = pseudo_legal_moves
                while target_squares:
                    target = target_squares & -target_squares
                    unmake_info = self.board_rep.make_move((source, target), piece, colour)
                    self.rebuild_state() # Update validator state to match temp board

                    king_bb = self.board_rep.bitboard_white["king"] if colour == "white" else self.board_rep.bitboard_black["king"]
                    if not self.is_square_attacked(king_bb, colour):
                        legal_moves.append((source, target))

                    # Restore the board and validator to their original state
                    self.board_rep.unmake_move(unmake_info)
                    self.rebuild_state()

                    target_squares &= target_squares -1 #move to the next target square
                #print(target_squares)
                source_squares &= source_squares - 1
        #print("==============================================")
        return legal_moves

