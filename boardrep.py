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
    def make_move(self, move: tuple, colour: str, en_passant_square: int = 0):
        """
        Applies a move to the board for simulation, correctly handling en passant.
        """
        source_square, target_square = move
        opponent_colour = "black" if colour == "white" else "white"

        current_player_board = self.bitboard_white if colour == "white" else self.bitboard_black
        opponent_board = self.bitboard_black if colour == "white" else self.bitboard_white

        moved_piece = next((p for p, bb in current_player_board.items() if bb & source_square), None)
        captured_piece = next((p for p, bb in opponent_board.items() if bb & target_square), None)

        # Prepare info needed to undo the move
        unmake_info = {
            "move": move, "moved_piece": moved_piece, "colour": colour,
            "captured_piece": captured_piece, "was_en_passant": False
        }

        # En Passant Logic 
        if moved_piece == 'pawn' and target_square == en_passant_square:
            captured_pawn_square = target_square >> 8 if colour == "white" else target_square << 8
            # The captured piece is a pawn, but it's not on the target square
            captured_piece = 'pawn'
            self.unset_bit(captured_pawn_square, 'pawn', opponent_colour)

            # Update unmake_info for this special case
            unmake_info["was_en_passant"] = True
            unmake_info["captured_piece_square"] = captured_pawn_square
            unmake_info["captured_piece"] = 'pawn' # Ensure this is set

        # --- Regular Move Logic ---
        elif captured_piece:
            self.unset_bit(target_square, captured_piece, opponent_colour)

        self.unset_bit(source_square, moved_piece, colour)
        self.set_bit(target_square, moved_piece, colour)
        return unmake_info

    def unmake_move(self, unmake_info: dict):
        """
        Reverts a move during simulation, correctly handling en passant.
        """
        source_square, target_square = unmake_info["move"]
        moved_piece, colour = unmake_info["moved_piece"], unmake_info["colour"]
        captured_piece = unmake_info["captured_piece"]
        opponent_colour = "black" if colour == "white" else "white"

        # Put the moved piece back
        self.set_bit(source_square, moved_piece, colour)
        self.unset_bit(target_square, moved_piece, colour)
        
        #En Passant and Regular Capture Logic 
        if captured_piece:
            # If it was en passant, put the captured pawn back on its special square
            if unmake_info.get("was_en_passant"):
                captured_square = unmake_info["captured_piece_square"]
                self.set_bit(captured_square, captured_piece, opponent_colour)
            # Otherwise, it was a regular capture on the target square
            else:
                self.set_bit(target_square, captured_piece, opponent_colour)

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

    def capture_at(self,square: int, colour:str):
        """Removes that piece out of the general bitboard"""
        bitboard = (self.bitboard_white if colour.lower()=="white" else self.bitboard_black)
        for piece, bb in bitboard.items():
            if bb & square:
                bitboard[piece] &=~square
                break

class ValidMoves:
    def __init__(self,boardrep: BoardRep, en_passant_square:int =0 ):
        self.board_rep = boardrep
        self.board = {"white":self.board_rep.bitboard_white,"black":self.board_rep.bitboard_black}

        self.white_pieces = sum(self.board["white"].values())
        self.black_pieces = sum(self.board["black"].values())
        self.occupied_squares = self.white_pieces|self.black_pieces

        self.notHFile = ~sum(1 << (7 + 8 * i) for i in range(8))
        self.notGHFile = (self.notHFile & (~sum(1<< (6+8*i) for i in range(8))))
        self.notAFile = ~sum(1 << (8 * i) for i in range(8))
        self.notABFile = (self.notAFile & (~sum(1<< (1+8*i) for i in range(8))))

        #[King moved,Rook king-side moved, Rook queen-side moved] 
        self.castling_white = [False,False,False]
        self.castling_black = [False,False,False]

        self.en_passant_square = en_passant_square

    def king_attacks(self,king_bitboard:int,colour:str="white")->int:
        """This returns only the raw attacks, see is_square_attacked for checking if the king is in check"""
        own_pieces = self.white_pieces if colour == "white" else self.black_pieces 
        attacks = ((king_bitboard >> 1) & self.notHFile) | ((king_bitboard << 1) & self.notAFile) |  \
           ((king_bitboard >> 7) & self.notAFile) | ((king_bitboard >> 9) & self.notHFile) |  \
           ((king_bitboard << 7) & self.notHFile) | ((king_bitboard << 9) & self.notAFile) |  \
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
        has_moved = self.castling_white if colour == "white" else self.castling_black
        print(f"Has anything moved? {has_moved}")
        #if any square on the queen/king side is attacked return false
        if colour == "white":
            sqrs_att_queen_sd = any(self.is_square_attacked(square, attacker_colour) for square in [1<<4,1<<3,1<<2]) 
            sqrs_att_king_sd = any(self.is_square_attacked(square, attacker_colour) for square in [1<<4,1<<5,1<<6]) 
        if colour == "black":
            sqrs_att_queen_sd = any(self.is_square_attacked(square, attacker_colour) for square in [1<<60,1<<59,1<<58]) 
            sqrs_att_king_sd = any(self.is_square_attacked(square, attacker_colour) for square in [1<<60,1<<61,1<<62]) 

        #If the king has moved
        if has_moved[0]: result = (False,False)
        #If there is a piece in the way or any of the squares in the kings path is attacked or the rook on that side has moved return False on that side 
        if self.occupied_squares & castling_king or sqrs_att_king_sd or has_moved[1]:
            result = (False,result[1])
        #If there is a piece in the way or any of the squares in the kings path is attacked or the rook on that side has moved return False on that side 
        if self.occupied_squares & castling_queen or sqrs_att_queen_sd or has_moved[2]:
            result = (result[0],False) 
        return result

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
        """Finds which squares a pawn is attacking, including moves, captures, and en passant."""
        moves = 0
        attacks = 0
        en_passant_move = 0

        if colour == "white":
            enemy_pieces = self.black_pieces
            # 1. Pawn pushes (forward moves)
            single_push = (pawn_bitboard << 8) & ~self.occupied_squares
            if single_push and (pawn_bitboard & constants.RANK_2):
                double_push = (pawn_bitboard << 16) & ~self.occupied_squares
                moves = single_push | double_push
            else:
                moves = single_push
            # 2. Pawn captures (diagonal attacks)
            attacks = ((pawn_bitboard << 9) & self.notAFile) | ((pawn_bitboard << 7) & self.notHFile)
            attacks &= enemy_pieces
            # 3. En passant capture
            if self.en_passant_square:
                ep_attacks = ((pawn_bitboard << 9) & self.notAFile) | ((pawn_bitboard << 7) & self.notHFile)
                if ep_attacks & self.en_passant_square:
                    en_passant_move = self.en_passant_square

        elif colour == "black":
            enemy_pieces = self.white_pieces
            # 1. Pawn pushes
            single_push = (pawn_bitboard >> 8) & ~self.occupied_squares
            if single_push and (pawn_bitboard & constants.RANK_7):
                double_push = (pawn_bitboard >> 16) & ~self.occupied_squares
                moves = single_push | double_push
            else:
                moves = single_push
            # 2. Pawn captures
            attacks = ((pawn_bitboard >> 7) & self.notHFile) | ((pawn_bitboard >> 9) & self.notAFile)
            attacks &= enemy_pieces
            # 3. En passant capture
            if self.en_passant_square:
                ep_attacks = ((pawn_bitboard >> 7) & self.notHFile) | ((pawn_bitboard >> 9) & self.notAFile)
                if ep_attacks & self.en_passant_square:
                    en_passant_move = self.en_passant_square

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

    def rebuild_state(self):
        """Rebuilds the validator's internal state from the board representation."""
        self.white_pieces = sum(self.board["white"].values())
        self.black_pieces = sum(self.board["black"].values())
        self.occupied_squares = self.white_pieces | self.black_pieces

    def generate_all_legal_moves(self,colour:str)->list:
        """Generates a list of all legal moves for a given colour."""
        legal_moves = []
        castling_rights = self.can_castle(colour) 
        print(castling_rights)
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

        for piece,bitboard in self.board[colour].items():
            source_squares = bitboard
            print("Piece:"+piece+", Colour:"+colour)
            
            while source_squares:
                source = source_squares & -source_squares
                pseudo_legal_moves = attack_functions[piece](source,colour)

                target_squares = pseudo_legal_moves
                while target_squares:
                    target = target_squares & -target_squares
                    unmake_info = self.board_rep.make_move((source, target), colour, en_passant_square = self.en_passant_square)
                    self.rebuild_state() # Update validator state to match temp board

                    king_bb = self.board_rep.bitboard_white["king"] if colour == "white" else self.board_rep.bitboard_black["king"]
                    if not self.is_square_attacked(king_bb, opponent_colour):
                        legal_moves.append((source, target))

                    # Restore the board and validator to their original state
                    self.board_rep.unmake_move(unmake_info)
                    self.rebuild_state()

                    target_squares &= target_squares -1 #move to the next target square
                #print(target_squares)
                source_squares &= source_squares - 1
        print("==============================================")
        return legal_moves

