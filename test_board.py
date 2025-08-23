import pytest
from boardrep import BoardRep, ValidMoves, MoveHandler
import munchkin
import conversions


@pytest.mark.parametrize("square, blocked, colour, expected_moves", [
    ("e2", False, "white", ("e3", "e4")), 
    ("e4", False, "white", ("e5",)),
    ("e4", True, "white", ()),
    ("e7", False, "black", ("e6", "e5")), 
    ("e5", False, "black", ("e4",)),
    ("e5", True, "black", ()),

    ("a2", False, "white", ("a3", "a4")),
    ("h2", False, "white", ("h3", "h4")),
    ("a7", False, "black", ("a6", "a5")),
    ("h7", False, "black", ("h6", "h5")),

    ("d2", True, "white", ()),
    ("g2", True, "white", ()),
    ("c7", True, "black", ()),
    ("f7", True, "black", ()),

    ("c3", False, "white", ("c4",)),
    ("f6", False, "white", ("f7",)),
    ("b6", False, "black", ("b5",)),
    ("g4", False, "black", ("g3",)),

    ("c3", True, "white", ()),
    ("f6", True, "white", ()),
    ("b6", True, "black", ()),
    ("g4", True, "black", ()),
])
def test_pawn_forward_moves(square, blocked, colour, expected_moves):

    board_rep = BoardRep()
    move_handler = MoveHandler(board_rep)
    validator = ValidMoves(board_rep)


    move_handler.set_bit(
        square=conversions.algebraic_to_bitboard(square),
        piece="pawn",
        colour=colour
    )

    opponent_colour = "black" if colour == "white" else "white"
    if blocked:
        if colour == "white":
            move_handler.set_bit(conversions.algebraic_to_bitboard(square)<<8,"pawn",colour = opponent_colour)
        else:
            move_handler.set_bit(conversions.algebraic_to_bitboard(square)>>8,"pawn",colour = opponent_colour)


    board = board_rep.bitboard_white if colour == "white" else board_rep.bitboard_black
    
    bitboard_expected_moves = 0
    for move in expected_moves:
        bitboard_expected_moves |= conversions.algebraic_to_bitboard(move)
    
    actual_moves = validator.pawn_attacks(board["pawn"], colour)

    #print(f"\nTesting pawn on {square} with {colour}. Blocked = {blocked}")

    assert actual_moves == bitboard_expected_moves

@pytest.mark.parametrize("square, not_squares, colour, expected_moves", [
    ("e4", (), "white", ("d5", "f5")),       # Both capture squares are occupied
    ("e4", ("d5",), "white", ("f5",)),       # d5 is empty, can only capture on f5
    ("e4", ("f5",), "white", ("d5",)),       # f5 is empty, can only capture on d5
    ("e4", ("d5", "f5"), "white", ()),       # Both capture squares are empty

    ("d5", (), "black", ("c4", "e4")),       # Both capture squares are occupied
    ("d5", ("c4",), "black", ("e4",)),       # c4 is empty, can only capture on e4
    ("d5", ("e4",), "black", ("c4",)),       # e4 is empty, can only capture on c4
    ("d5", ("c4", "e4"), "black", ()),       # Both capture squares are empty

    ("a2", (), "white", ("b3",)),            # Capture square b3 is occupied
    ("a2", ("b3",), "white", ()),            # Capture square b3 is empty

    ("h7", (), "black", ("g6",)),            # Capture square g6 is occupied
    ("h7", ("g6",), "black", ()),            # Capture square g6 is empty

    ("c7", (), "white", ("b8", "d8")),       # Both promotion capture squares are occupied
    ("c7", ("b8",), "white", ("d8",)),       # b8 is empty, can only capture on d8
    ("f2", (), "black", ("e1", "g1")),       # Both promotion capture squares are occupied
    ("f2", ("e1",), "black", ("g1",)),       # e1 is empty, can only capture on g1
])

def test_pawn_captures(square, not_squares, colour, expected_moves):

    board_rep = BoardRep() 
    move_handler = MoveHandler(board_rep)
    validator = ValidMoves(board_rep)

    move_handler.set_bit(
        square=conversions.algebraic_to_bitboard(square),
        piece="pawn",
        colour=colour
    )

    do_not_populate_mask = conversions.algebraic_to_bitboard(square)
    for s in not_squares:
        do_not_populate_mask |= conversions.algebraic_to_bitboard(s)

    opponent_colour = "black" if colour == "white" else "white"
    #Populate the whole board apart from the squares we specify
    for i in range(0, 64):
        square_bit = 1 << i
        if not (square_bit & do_not_populate_mask):
            move_handler.set_bit(square_bit, "rook", colour=opponent_colour)

    board = board_rep.bitboard_white if colour == "white" else board_rep.bitboard_black
    bitboard_expected_moves = 0
    for move in expected_moves:
        bitboard_expected_moves |= conversions.algebraic_to_bitboard(move)

    actual_moves = validator.pawn_attacks(board["pawn"], colour)
    
    #print(f"\nTesting pawn on {square} ({colour}). Empty squares: {not_squares or 'None'}")
    
    assert actual_moves == bitboard_expected_moves 

@pytest.mark.parametrize("square, blocked_squares, colour, expected_squares", [
    # Central squares, full movement
    ("e4", (), "white", ("d2", "f2", "c3", "g3", "c5", "g5", "d6", "f6")),
    ("d4", (), "black", ("b3", "f3", "b5", "f5", "c2", "e2", "c6", "e6")),
    
    # Corner squares, limited movement
    ("a1", (), "white", ("b3", "c2")),
    ("a8", (), "black", ("b6", "c7")),
    ("h1", (), "white", ("f2", "g3")),
    ("h8", (), "black", ("f7", "g6")),
    
    # Edge squares, partially limited
    ("a4", (), "white", ("b2", "c3", "c5", "b6")),
    ("h5", (), "black", ("f4", "g3", "g7", "f6")),
    ("d1", (), "white", ("b2", "f2", "c3", "e3")),
    ("e8", (), "black", ("c7", "g7", "d6", "f6")),
    
    # Near-edge squares
    ("b2", (), "white", ("a4", "c4", "d1", "d3")),
    ("g7", (), "black", ("e6", "e8", "f5", "h5")),
    
    # Blocked scenarios, some squares occupied
    ("e4", ("d2", "f6"), "white", ("f2", "c3", "g3", "c5", "g5", "d6")),
    ("d4", ("b3", "c6", "e2"), "black", ("f3", "b5", "f5", "e6", "c2")),
    ("c3", ("a2", "e2"), "white", ("a4", "b1", "d1", "e4", "b5", "d5")),
    
    # Heavily blocked
    ("e4", ("d2", "f2", "c3", "g3"), "white", ("c5", "g5", "d6", "f6")),
    ("d4", ("b3", "f3", "c2", "e2"), "black", ("b5", "f5", "c6", "e6")),
    
    # All moves blocked
    ("e4", ("d2", "f2", "c3", "g3", "c5", "g5", "d6", "f6"), "white", ()),
    ("d4", ("b3", "f3", "b5", "f5", "c2", "e2", "c6", "e6"), "black", ()),
    
    # Edge cases with blocking
    ("a1", ("b3",), "white", ("c2",)),
    ("a1", ("b3", "c2"), "white", ()),
    ("h8", ("f7", "g6"), "black", ()),
    
    # Single move available
    ("b1", ("a3", "c3"), "white", ("d2",)),
    ("g8", ("e7", "h6"), "black", ("f6",)),
])
def test_knight_attacks(square, blocked_squares, colour, expected_squares):
    board_rep = BoardRep()
    move_handler = MoveHandler(board_rep)
    validator = ValidMoves(board_rep)

    move_handler.set_bit(
        square=conversions.algebraic_to_bitboard(square),
        piece="knight",
        colour=colour
    )
    expected_moves = 0 
    for expected_square in expected_squares:
        expected_moves |= conversions.algebraic_to_bitboard(expected_square)

    for blocked_square in blocked_squares:
        move_handler.set_bit(
            square = conversions.algebraic_to_bitboard(blocked_square),
            piece="pawn",
            colour=colour)
    board = board_rep.bitboard_white if colour == "white" else board_rep.bitboard_black
    actual_moves = validator.knight_attacks(board["knight"], colour)
    assert actual_moves==expected_moves

def test_bishop_attacks(square,blocked_squares,colour,expected_squares):
    board_rep = BoardRep()
    move_handler = MoveHandler(board_rep)
    validator = ValidMoves(board_rep)
    move_handler.set_bit(
        square = conversions.algebraic_to_bitboard(square),
        piece = "knight",
        colour = colour
    )
