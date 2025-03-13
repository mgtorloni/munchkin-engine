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
    

    def rook_attacks(self,index:int)->int:
        rank = index//8
        file = index%8
        occupied_squares = sum(self.board["white"].values())|sum(self.board["black"].values())
        ROOK_MASK =[72340172838076926, 144680345676153597, 289360691352306939, 578721382704613623, 1157442765409226991, 2314885530818453727, 4629771061636907199, 9259542123273814143, 72340172838141441, 144680345676217602, 289360691352369924, 578721382704674568, 1157442765409283856, 2314885530818502432, 4629771061636939584, 9259542123273813888, 72340172854657281, 144680345692602882, 289360691368494084, 578721382720276488, 1157442765423841296, 2314885530830970912, 4629771061645230144, 9259542123273748608, 72340177082712321, 144680349887234562, 289360695496279044, 578721386714368008, 1157442769150545936, 2314885534022901792, 4629771063767613504, 9259542123257036928, 72341259464802561, 144681423712944642, 289361752209228804, 578722409201797128, 1157443723186933776, 2314886351157207072, 4629771607097753664, 9259542118978846848, 72618349279904001, 144956323094725122, 289632270724367364, 578984165983651848, 1157687956502220816, 2315095537539358752, 4629910699613634624, 9259541023762186368, 143553341945872641, 215330564830528002, 358885010599838724, 645993902138460168, 1220211685215703056, 2368647251370188832, 4665518383679160384, 9259260648297103488, 18302911464433844481, 18231136449196065282, 18087586418720506884, 17800486357769390088, 17226286235867156496, 16077885992062689312, 13781085504453754944, 9187484529235886208]       
        slider_square = 1<<index
        #formula : ((o&m)-2s)^((o&m)'-2s')')&m
        rookAttacks = (((occupied_squares & ROOK_MASK[index]) - 2 * slider_square) ^
                         conversions.reverse_bitboard((conversions.reverse_bitboard(occupied_squares & ROOK_MASK[index]) - 
                         2 * conversions.reverse_bitboard(slider_square)))) & ROOK_MASK[index]
        """
        rookAttacks = (((occupied_squares & ROOK_MASK) - 2 * slider_square) ^
                         conversions.reverse_bitboard((conversions.reverse_bitboard(occupied_squares & ROOK_MASK) - 
                         2 * conversions.reverse_bitboard(slider_square)))) & ROOK_MASK
        """
        return rookAttacks 
