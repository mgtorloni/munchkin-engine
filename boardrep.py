import constants
import conversions
import copy
from typing import TypedDict

class BoardRep:
    """Turns board into a bitboards"""

    def __init__(self):
        """Just initialise the board"""
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

        #[King-side castling, Queen-side castling] 
        self.castling_white = [True,True]
        self.castling_black = [True,True]

        self.en_passant_square = 0 #Stores the target square for potential EP capture
   

    def initial_position(self)->tuple[dict,dict]:
        """Set initial positions of pieces on the chess board"""

        #Calculated using the generating functions
        self.bitboard_white = constants.INITIAL_WHITE
        self.bitboard_black = constants.INITIAL_BLACK

        # We haven't lost our ability to castle in the future yet
        # (it is the start of the game!)
        self.castling_white = [True,True]
        self.castling_black = [True,True]

        self.en_passant_square = 0 # There is no en passants

        return (self.bitboard_white,self.bitboard_black)

    def to_fen(self, colour_to_move: str) -> str:
        """Turns a position into FEN"""
        piece_to_char = {
            "pawn": 'p', "knight": 'n', "bishop": 'b',
            "rook": 'r', "queen": 'q', "king": 'k'
        }
        
        fen = ""
        for r in range(7, -1, -1):
            empty = 0
            for f in range(8):
                square_index = r * 8 + f
                square_bb = 1 << square_index
                
                char_found = None
                
                # Check white pieces
                for piece_name, bb in self.bitboard_white.items():
                    if bb & square_bb:
                        char_found = piece_to_char[piece_name].upper()
                        break
                
                # Check black pieces if no white piece was found
                if not char_found:
                    for piece_name, bb in self.bitboard_black.items():
                        if bb & square_bb:
                            char_found = piece_to_char[piece_name].lower()
                            break

                if char_found:
                    if empty > 0:
                        fen += str(empty)
                        empty = 0
                    fen += char_found
                else:
                    empty += 1
            
            if empty > 0:
                fen += str(empty)
            if r > 0:
                fen += '/'

        # Active color
        fen += ' w' if colour_to_move == "white" else ' b'

        # Castling rights
        castling = ""
        if self.castling_white[0]: castling += 'K'
        if self.castling_white[1]: castling += 'Q'
        if self.castling_black[0]: castling += 'k'
        if self.castling_black[1]: castling += 'q'
        fen += f" {castling if castling else '-'}"

        # En passant square
        if self.en_passant_square == 0:
            fen += ' -'
        else:
            fen += f" {conversions.square_to_algebraic(self.en_passant_square)}"

        # Halfmove and fullmove counters
        fen += ' 0 1'
        return fen

    def from_fen(self, fen: str):
        """Sets the board state from a FEN string"""
        self.bitboard_white = {p: 0 for p in self.bitboard_white}
        self.bitboard_black = {p: 0 for p in self.bitboard_black}

        parts = fen.split(' ')
        board_part = parts[0]
        
        rank = 7
        file = 0
        for char in board_part:
            if char == '/':
                rank -= 1
                file = 0
            elif char.isdigit():
                file += int(char)
            else:
                square_index = rank * 8 + file
                square_bb = 1 << square_index
                
                piece_map = {'P': 'pawn', 'N': 'knight', 'B': 'bishop', 'R': 'rook', 'Q': 'queen', 'K': 'king'}
                piece_type = piece_map[char.upper()]

                if char.isupper():
                    self.bitboard_white[piece_type] |= square_bb
                else:
                    self.bitboard_black[piece_type] |= square_bb
                file += 1

        # Castling rights
        castling_part = parts[2]
        self.castling_white = ['K' in castling_part, 'Q' in castling_part]
        self.castling_black = ['k' in castling_part, 'q' in castling_part]

        # En passant
        ep_part = parts[3]
        if ep_part == '-':
            self.en_passant_square = 0
        else:
            self.en_passant_square = conversions.algebraic_to_bitboard(ep_part)

        return parts[1] # Return the color to move

class UnmakeInfo(TypedDict):
    bitboard_white: dict[str, int]
    bitboard_black: dict[str, int]
    castling_white: list[bool]
    castling_black: list[bool]
    en_passant_square: int

class MoveHandler:
    def __init__(self, boardrep: BoardRep):
        self.board_rep = boardrep
    
    def unset_bit(self,square:int,piece:str,colour:str = "white"):
        """Unset piece from a bit"""
        if colour.lower() == "white": 
            self.board_rep.bitboard_white[piece] &= ~square
            return self.board_rep.bitboard_white

        elif colour.lower() == "black":
            self.board_rep.bitboard_black[piece] &= ~square
            return self.board_rep.bitboard_black
        else:
            raise ValueError("Color must be either 'white' or 'black'")

    def set_bit(self,square:int, piece: str,colour:str = "white") -> int:
        """Set piece on a bit"""

        if colour.lower() == "white": 
            self.board_rep.bitboard_white[piece] |= square # We want to add a bit to that position
            #in that pieces bitboard
            return self.board_rep.bitboard_white

        elif colour.lower() == "black":
            self.board_rep.bitboard_black[piece] |= square
            return self.board_rep.bitboard_black
        else:
            raise ValueError("Color must be either 'white' or 'black'") 

    def fast_copy_board(self) -> UnmakeInfo:
        """Creates a fast copy of the board, since deepcopy is very slow"""
        return {
            "bitboard_white":self.board_rep.bitboard_white.copy(),
            "bitboard_black":self.board_rep.bitboard_black.copy(),
            "castling_white":list(self.board_rep.castling_white),
            "castling_black":list(self.board_rep.castling_black),
            "en_passant_square":self.board_rep.en_passant_square
        }


    def make_move(self, move: tuple, colour: str) -> UnmakeInfo:
        """ 
        Makes a move, changing the board state and returns a
        unamke info backup of the board state before it made the change

        We don't care if the moves are legal in this function, we just make them as allowed by the rules
        """
        source_square,target_square = move
        current_player_board = self.board_rep.bitboard_white if colour=="white" else self.board_rep.bitboard_black
        moved_piece = next((p for p, bb in current_player_board.items() if bb & source_square))

        unmake_info = self.fast_copy_board() # Before we modify anything make a copy so that we can revert the changes later if needed

        ep_square_before_move = self.board_rep.en_passant_square

        self._handle_captures(move,moved_piece,colour,ep_square_before_move)

        self._update_game_state(move,moved_piece,colour)

        # If we moved the king to the square that is 2 squares away to the left or to the right,
        # we are trying to castle, and so we should 
        is_castle = moved_piece == 'king' and abs(conversions.square_to_index(source_square) - conversions.square_to_index(target_square)) == 2
        if is_castle:
            self.make_castle(move, colour)

        # Move piece
        self.unset_bit(source_square, moved_piece, colour)
        self.set_bit(target_square, moved_piece, colour)

        # If a pawn is on the last rank it is a promotion square we just moved into
        is_promotion_square = any(target_square == 1<<i for i in range(55,64)) if colour == "white" else any(target_square==1<<i for i in range(0,8))

        if moved_piece == "pawn" and is_promotion_square:
            self.unset_bit(target_square,moved_piece,colour) #unset the pawn from the back rank
            self.set_bit(target_square,"queen",colour) #set a new queen

        return unmake_info

    def _handle_captures(self, move:tuple[int,int], moved_piece:str, colour:str, ep_square_before_move:int) -> None:
        """Changes the states of a board if a piece has been captured"""
        _,target_square = move
        opponent_colour = "black" if colour=="white" else "white"
        opponent_board = self.board_rep.bitboard_black if colour == "white" else self.board_rep.bitboard_white
        if moved_piece == 'pawn' and target_square == ep_square_before_move:
            captured_pawn_square = (target_square >> 8) if colour == "white" else (target_square << 8)
            self.unset_bit(captured_pawn_square, 'pawn', opponent_colour)
        else: 
            captured_piece = next((p for p, bb in opponent_board.items() if bb & target_square), None)
            if captured_piece:
                self.unset_bit(target_square, captured_piece, opponent_colour)

                #if one of the rooks has been captured, castling on that side is not allowed anymore
                if target_square == 1: self.board_rep.castling_white[1] = False
                if target_square == 1<<7: self.board_rep.castling_white[0] = False

                if target_square == 1<<56: self.board_rep.castling_black[1] = False
                if target_square == 1<<63: self.board_rep.castling_black[0] = False

    def _update_game_state(self, move:tuple[int,int], moved_piece:str, colour:str):
        """Handles changes in state that don't involve captures"""
        source_square,target_square = move

        if moved_piece == "pawn" and abs(conversions.square_to_index(source_square) - conversions.square_to_index(target_square)) == 16:
            self.board_rep.en_passant_square = (source_square << 8) if colour == "white" else (source_square >> 8)
        else:
            self.board_rep.en_passant_square = 0

        # If the king moves it can't castle in any direction anymore
        if moved_piece == 'king':
            if colour == 'white':
                self.board_rep.castling_white = [False, False]
            else:
                self.board_rep.castling_black = [False, False]

        # If a rook moves the king can't castle in that direction anymore
        if moved_piece == 'rook':
            if colour == 'white':
                if source_square == 1: #a1 rook
                    self.board_rep.castling_white[1] = False
                elif source_square == 1<<7: #h8 rook
                    self.board_rep.castling_white[0] = False
            if colour == 'black':
                if source_square == 1<<56: #a8
                    self.board_rep.castling_black[1] = False
                elif source_square == 1<<63: #g8 rook
                    self.board_rep.castling_black[0] = False

    def make_castle(self, move:tuple[int,int], colour:str):
        """
        Castles the king: This involves going with the king to squares to the right
        (or to the left) and putting the rook on the square directly to the left 
        (or to the right) of the king
        """
        source_square,target_square = move

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

    def unmake_move(self, unmake_info:UnmakeInfo) -> None:
        """ Changes the board state to a whatever the user wants"""
        # This function is used primarily as a means to change the board state back
        # to what it was before a move was made, but it can realistically be use to change
        # to any board state a user wants
        self.board_rep.bitboard_white = unmake_info["bitboard_white"]
        self.board_rep.bitboard_black = unmake_info["bitboard_black"]
        self.board_rep.castling_white = unmake_info["castling_white"]
        self.board_rep.castling_black = unmake_info["castling_black"]
        self.board_rep.en_passant_square = unmake_info["en_passant_square"]

class ValidMoves:
    """Adds the rules to the board representation"""
    def __init__(self,boardrep: BoardRep):
        self.board_rep = boardrep
        self.move_handler = MoveHandler(self.board_rep)

        self.FILE_A = 0x0101010101010101
        self.FILE_H = 0x8080808080808080
        self.FILE_AB = self.FILE_A | (self.FILE_A << 1);
        self.FILE_GH = self.FILE_H | (self.FILE_H >> 1);

    #Every time these are "called" (no need for ()) they are calculated/updated
    @property
    def white_pieces(self) -> int:
        return sum(self.board_rep.bitboard_white.values())
    @property
    def black_pieces(self) -> int:
        return sum(self.board_rep.bitboard_black.values())
    @property
    def occupied_squares(self) -> int:
        return self.white_pieces|self.black_pieces

    def king_attacks(self,king_bitboard:int,colour:str="white")->int:
        """This returns only the raw attacks, see is_square_attacked for checking if the king is in check"""
        own_pieces = self.white_pieces if colour == "white" else self.black_pieces 
        attacks = ((king_bitboard >> 1) & ~self.FILE_H) | ((king_bitboard << 1) & ~self.FILE_A) |  \
           ((king_bitboard >> 7) & ~self.FILE_A) | ((king_bitboard >> 9) & ~self.FILE_H) |  \
           ((king_bitboard << 7) & ~self.FILE_H) | ((king_bitboard << 9) & ~self.FILE_A) |  \
           (king_bitboard >> 8) | (king_bitboard << 8)
        
        # Add a 64-bit mask to discard any "off-board" bits before returning
        # Since the king works solely off bit operations we could shift a bit so much it goes off the board
        return attacks & 0xFFFFFFFFFFFFFFFF & ~own_pieces

    def can_castle(self,colour:str="white") -> tuple[bool,bool]:
        """Returns a tuple showing if that colour can castle king-side or queen-side""" 
        rights = self.board_rep.castling_white if colour == "white" else self.board_rep.castling_black

        #King-side Check
        can_castle_ks = rights[0]  # Start with the stored right
        if can_castle_ks:  # Only check further if the right hasn't been lost
            # f1 | g1 if white else f8 | g8
            path_squares = (1 << 5) | (1 << 6) if colour == "white" else (1 << 61) | (1 << 62)
            if self.occupied_squares & path_squares: # If there are pieces in the path squares we know we can't castle
                can_castle_ks = False
            else:
                # We need to check that the king isn't in check and that the squares between it and c8 aren't aren't being attacked
                attack_check_squares = [1 << 4, 1 << 5, 1 << 6] if colour == "white" else [1 << 60, 1 << 61, 1 << 62]
                if any(self.is_square_attacked(sq, colour) for sq in attack_check_squares):
                    can_castle_ks = False

        #Queen-side Check
        can_castle_qs = rights[1]  # Start with the stored right
        if can_castle_qs:  # Only check further if the right hasn't been lost

            # a1 | b1 | c1 if white else b8 | c8 | d8                                  
            path_squares = (1 << 1) | (1 << 2) | (1 << 3) if colour == "white" else (1 << 57) | (1 << 58) | (1 << 59)
            if self.occupied_squares & path_squares: # If there are pieces in the path squares we know we can't castle
                can_castle_qs = False
            else:
                # We need to check that the king isn't in check and that the squares between it and c8 aren't aren't being attacked
                attack_check_squares = [1 << 4, 1 << 3, 1 << 2] if colour == "white" else [1 << 60, 1 << 59, 1 << 58] 
                if any(self.is_square_attacked(sq, colour) for sq in attack_check_squares):
                    can_castle_qs = False

        return (can_castle_ks, can_castle_qs)

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
            return True #if there is a king a 'king-away' from this square it means that it is being attacked by that king 

        return False #if no pieces attacks that square, then return false

    def knight_attacks(self,piece_bitboard:int,colour:str="white") -> int:
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
            # If we are white we go up the board so <<8 is the correct direction to push
            enemy_pieces = self.black_pieces
            single_push = (pawn_bitboard << 8) & ~self.occupied_squares #We can't move if there is a piece right in from
            if single_push and (pawn_bitboard & constants.RANK_2): # If we are in the starting rank we may double push
                double_push = (pawn_bitboard << 16) & ~self.occupied_squares
                moves = single_push | double_push
            else:
                moves = single_push
            pseudo_attacks = ((pawn_bitboard << 9) & ~self.FILE_A) | ((pawn_bitboard << 7) & ~self.FILE_H) # If we are white the attacks are NW and NE the board
            attacks = pseudo_attacks & enemy_pieces # We can only attack those squares if there are enemy pieces there 
            if self.board_rep.en_passant_square: # If the enpassant square is not 0
                if pseudo_attacks & self.board_rep.en_passant_square:
                    en_passant_move = self.board_rep.en_passant_square

        elif colour == "black":
            enemy_pieces = self.white_pieces
            single_push = (pawn_bitboard >> 8) & ~self.occupied_squares
            if single_push and (pawn_bitboard & constants.RANK_7):
                double_push = (pawn_bitboard >> 16) & ~self.occupied_squares
                moves = single_push | double_push
            else:
                moves = single_push
            pseudo_attacks = ((pawn_bitboard >> 9) & ~self.FILE_H) | ((pawn_bitboard >> 7) & ~self.FILE_A)
            attacks = pseudo_attacks & enemy_pieces
            if self.board_rep.en_passant_square:
                if pseudo_attacks & self.board_rep.en_passant_square:
                    en_passant_move = self.board_rep.en_passant_square

        return attacks | moves | en_passant_move & 0xFFFFFFFFFFFFFFFF #Since these are shifting operations we are applying, we may leave the board, therefore it is safe to apply that board mask

    def hyperbola_quint(self,slider_bitboard:int,mask:int,colour:str = "white") -> int: #slider attacks formula
        """Uses the hyperbola quintessential formula to calculate how the slider attacks stop at a piece on their way"""
        #formula : ((o&m)-2s)^reverse(reverse(o&m)-2reverse(s))&m
        sliderAttacks = (((self.occupied_squares & mask) - (slider_bitboard<< 1)) ^
                        conversions.reverse_bitboard(conversions.reverse_bitboard(self.occupied_squares & mask) - (conversions.reverse_bitboard(slider_bitboard) << 1))) & mask

        return sliderAttacks

    def rook_attacks(self,rook_bitboard:int,colour:str = "white")->int:
        """Finds which square a rook is attacking using magic bitboards"""

        own_pieces = self.white_pieces if colour == "white" else self.black_pieces 
        square_index = conversions.square_to_index(rook_bitboard)

        blockers = self.occupied_squares & constants.ROOK_MAGIC_MASKS[square_index] # Get the relevant blockers

        # Use the injective function we catered for when creating the lookup table 
        magic_index = ((blockers * constants.ROOK_MAGICS[square_index]) & 0xFFFFFFFFFFFFFFFF) >> constants.ROOK_SHIFTS[square_index] 

        
        base_offset = constants.ROOK_ATTACK_OFFSETS[square_index] # Get the starting index for this square's data within the flat BISHOP_ATTACKS 
        #table. We have multiple "starts" of blocker patterns in one single list, so we need to navigate to the right one, which can be found in
        # the offset table

        attacks = constants.ROOK_ATTACKS[base_offset + magic_index]
        
        return attacks & ~own_pieces

    def bishop_attacks(self,bishop_bitboard:int,colour:str = "white") -> int:
        """Finds which squares a bishop is attacking using magic bitboards""" 

        own_pieces = self.white_pieces if colour == "white" else self.black_pieces 
        square_index = conversions.square_to_index(bishop_bitboard) #Convert the bitboard to index

        blockers = self.occupied_squares & constants.BISHOP_MAGIC_MASKS[square_index] # Get the relevant blockers

        # Use the injective function we catered for when creating the lookup table
        magic_index = ((blockers * constants.BISHOP_MAGICS[square_index]) & 0xFFFFFFFFFFFFFFFF) >> constants.BISHOP_SHIFTS[square_index] 
        
        base_offset = constants.BISHOP_ATTACK_OFFSETS[square_index] # Get the starting index for this square's data within the flat BISHOP_ATTACKS 
        #table. We have multiple "starts" of blocker patterns in one single list, so we need to navigate to the right one, which can be found in
        # the offset table
        
        attacks = constants.BISHOP_ATTACKS[base_offset + magic_index]
        
        return attacks & ~own_pieces

    def queen_attacks(self,queen_bitboard:int,colour:str = "white") -> int:
        """Finds the squares the queen is attacking (they are just a rooks and a bishop in one piece)"""
        return self.rook_attacks(queen_bitboard,colour)|self.bishop_attacks(queen_bitboard,colour) 

    def generate_pseudo_legal_moves(self, colour: str) -> list:
        """Generate all legal moves, without considering if the king is going to be in check"""
        pseudo_legal_moves = []
        attack_functions = {
            "pawn": self.pawn_attacks, "rook": self.rook_attacks,
            "knight": self.knight_attacks, "bishop": self.bishop_attacks,
            "queen": self.queen_attacks, "king": self.king_attacks
        }
        current_player_bb = self.board_rep.bitboard_white if colour == "white" else self.board_rep.bitboard_black

        # Generate all piece moves
        for piece, bitboard in current_player_bb.items():
            source_squares = bitboard
            while source_squares:
                source = source_squares & -source_squares # Take the first bit (from right to left) of that bitboard
                target_squares = attack_functions[piece](source, colour)
                while target_squares:
                    target = target_squares & -target_squares # Take the first bit (from right to left) of the target squares
                    pseudo_legal_moves.append((source, target)) # That is a move we can make 
                    target_squares &= target_squares - 1 # Clears the target square we just calculated
                source_squares &= source_squares - 1 # Clears the source square for the (single) piece we just calculated

        # Note can_castle already checks if the king passes through check, so this is safe
        castling_rights = self.can_castle(colour)
        if castling_rights[0]:  # King-side
            pseudo_legal_moves.append((1 << 4, 1 << 6) if colour == "white" else (1 << 60, 1 << 62))
        if castling_rights[1]:  # Queen-side
            pseudo_legal_moves.append((1 << 4, 1 << 2) if colour == "white" else (1 << 60, 1 << 58))
            
        return pseudo_legal_moves

    def generate_all_legal_moves(self, colour: str) -> list:
        """
        Generate all legal moves, checking if the king is going to be in check,
        we only use this for the user
        """
        pseudo_moves = self.generate_pseudo_legal_moves(colour) #Generate all moves
        legal_moves = []

        for move in pseudo_moves:
            unmake_info = self.move_handler.make_move(move, colour)
            king_bb = self.board_rep.bitboard_white["king"] if colour == "white" else self.board_rep.bitboard_black["king"]
            if not self.is_square_attacked(king_bb, colour): #Checks if the move we made  will leave the king in check
                legal_moves.append(move) # If not, that is a legal move
            self.move_handler.unmake_move(unmake_info)
        return legal_moves

