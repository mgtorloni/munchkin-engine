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
    ("e4", (), "white", ("d5", "f5")),
    ("e4", ("d5",), "white", ("f5",)),
    ("e4", ("f5",), "white", ("d5",)),
    ("e4", ("d5", "f5"), "white", ()),

    ("d5", (), "black", ("c4", "e4")),
    ("d5", ("c4",), "black", ("e4",)),
    ("d5", ("e4",), "black", ("c4",)),
    ("d5", ("c4", "e4"), "black", ()),

    ("a2", (), "white", ("b3",)),
    ("a2", ("b3",), "white", ()),

    ("h7", (), "black", ("g6",)),
    ("h7", ("g6",), "black", ()),

    ("c7", (), "white", ("b8", "d8")),
    ("c7", ("b8",), "white", ("d8",)),
    ("f2", (), "black", ("e1", "g1")),
    ("f2", ("e1",), "black", ("g1",)),
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

@pytest.mark.parametrize("square,eat, blocked_squares, colour, expected_squares", [
    # Central squares, full diagonal movement
    ("d4",False, (), "white", ("a1", "b2", "c3", "e5", "f6", "g7", "h8", "a7", "b6", "c5", "e3", "f2", "g1")),
    ("e5",False, (), "black", ("a1", "b2", "c3", "d4", "f6", "g7", "h8", "b8", "c7", "d6", "f4", "g3", "h2")),
    
    # Corner squares, limited to one diagonal each
    ("a1",False, (), "white", ("b2", "c3", "d4", "e5", "f6", "g7", "h8")),
    ("h8",False, (), "black", ("a1", "b2", "c3", "d4", "e5", "f6", "g7")),
    ("a8",False, (), "white", ("b7", "c6", "d5", "e4", "f3", "g2", "h1")),
    ("h1",False, (), "black", ("a8", "b7", "c6", "d5", "e4", "f3", "g2")),
    
    # Edge squares
    ("a4",False, (), "white", ("b3", "c2", "d1", "b5", "c6", "d7", "e8")),
    ("h5",False, (), "black", ("g4", "f3", "e2", "d1", "g6", "f7", "e8")),
    ("d1",False, (), "white", ("a4", "b3", "c2", "e2", "f3", "g4", "h5")),
    ("e8",False, (), "black", ("a4", "b5", "c6", "d7", "f7", "g6", "h5")),
    
    # Near corner squares
    ("b2",False, (), "white", ("a1", "c1", "a3", "c3", "d4", "e5", "f6", "g7", "h8")),
    ("g7",False, (), "black", ("a1", "b2", "c3", "d4", "e5", "f6", "h8", "f8", "h6")),
    
    # Blocked by single piece on each diagonal
    ("d4",False, ("c3",), "white", ("e5", "f6", "g7", "h8", "a7", "b6", "c5", "e3", "f2", "g1")),
    ("d4",False, ("e5",), "black", ("a1", "b2", "c3", "a7", "b6", "c5", "e3", "f2", "g1")),
    ("d4",False, ("c5",), "white", ("a1", "b2", "c3", "e5", "f6", "g7", "h8", "e3", "f2", "g1")),
    ("d4",False, ("e3",), "black", ("a1", "b2", "c3", "e5", "f6", "g7", "h8","a7","b6","c5")),
    
    # Multiple blocks on same diagonal
    ("d4",False, ("c3", "b2"), "white", ("e5", "f6", "g7", "h8", "a7", "b6", "c5", "e3", "f2", "g1")),
    ("d4",False, ("e5", "f6"), "black", ("a1", "b2", "c3", "a7", "b6", "c5", "e3", "f2", "g1")),
    
    # Blocks on multiple diagonals
    ("d4",False, ("c3", "e5"), "white", ("a7", "b6", "c5", "e3", "f2", "g1")),
    ("d4",False, ("c5", "e3"), "black", ("a1", "b2", "c3", "e5", "f6", "g7", "h8")),
    
    # Heavy blocking
    ("d4",False, ("c3", "e5", "c5", "e3"), "white", ()),
    ("e5",False, ("d4", "f6", "d6", "f4"), "black", ()),
    
    # Edge cases, corner with blocking
    ("a1",False, ("b2",), "white", ()),
    ("a1",False, ("c3",), "black", ("b2",)),
    ("h8",False, ("g7", "f6"), "white", ()),
    
    ("b2",False, ("a1", "c3"), "white", ("c1", "a3")),
    ("g2",False, ("f1", "h1", "f3"), "black", ("h3",)),

    # Blocked by single piece on each diagonal
    ("d4",True, ("c3",), "white", ("c3","e5", "f6", "g7", "h8", "a7", "b6", "c5", "e3", "f2", "g1")),
    ("d4",True, ("e5",), "black", ("e5","a1", "b2", "c3", "a7", "b6", "c5", "e3", "f2", "g1")),
    ("d4",True, ("c5",), "white", ("c5","a1", "b2", "c3", "e5", "f6", "g7", "h8", "e3", "f2", "g1")),
    ("d4",True, ("e3",), "black", ("e3","a1", "b2", "c3", "e5", "f6", "g7", "h8","a7","b6","c5")),
    
    # Multiple blocks on same diagonal
    ("d4",True, ("c3", "b2"), "white", ("c3", "e5", "f6", "g7", "h8", "a7", "b6", "c5", "e3", "f2", "g1")),
    ("d4",True, ("e5", "f6"), "black", ("e5","a1", "b2", "c3", "a7", "b6", "c5", "e3", "f2", "g1")),
    
    # Blocks on multiple diagonals
    ("d4",True, ("c3", "e5"), "white", ("c3","e5","a7", "b6", "c5", "e3", "f2", "g1")),
    ("d4",True, ("c5", "e3"), "black", ("c5","e3","a1", "b2", "c3", "e5", "f6", "g7", "h8")),
    
    # Heavy blocking
    ("d4",True, ("c3", "e5", "c5", "e3"), "white", ("c3", "e5", "c5", "e3")),
    ("e5",True, ("d4", "f6", "d6", "f4"), "black", ("d4", "f6", "d6", "f4")),
    
    # Edge cases, corner with blocking
    ("a1",True, ("b2",), "white", ("b2",)),
    ("a1",True, ("c3",), "black", ("b2","c3")),
    ("h8",True, ("g7", "f6"), "white", ("g7",)),
    
    ("b2",True, ("a1", "c3"), "white", ("a1","c3","c1", "a3")),
    ("g2",True, ("f1", "h1", "f3"), "black", ("f1","h1","f3","h3")),

])
def test_bishop_attacks(square, eat, blocked_squares,colour,expected_squares):
    board_rep = BoardRep()
    move_handler = MoveHandler(board_rep)
    validator = ValidMoves(board_rep)
    opposite_colour = "white" if colour == "black" else "black"

    move_handler.set_bit(
        square = conversions.algebraic_to_bitboard(square),
        piece = "bishop",
        colour = colour
    )
    expected_moves = 0 
    for expected_square in expected_squares:
        expected_moves |= conversions.algebraic_to_bitboard(expected_square)
        
    for blocked_square in blocked_squares:
        move_handler.set_bit(
            square= conversions.algebraic_to_bitboard(blocked_square),
            piece = "pawn",
            colour = colour if eat == False else opposite_colour) #i.e. if we want the piece at the blocked square to be eaten we should make it the opposite_colour
    board = board_rep.bitboard_white if colour == "white" else board_rep.bitboard_black
    actual_moves = validator.bishop_attacks(board["bishop"], colour)
    assert actual_moves==expected_moves

@pytest.mark.parametrize("square,eat, blocked_squares, colour, expected_squares", [
    # Central squares - full horizontal and vertical movement
    ("d4", False, (), "white", ("d1", "d2", "d3", "d5", "d6", "d7", "d8", "a4", "b4", "c4", "e4", "f4", "g4", "h4")),
    ("e5", False, (), "black", ("e1", "e2", "e3", "e4", "e6", "e7", "e8", "a5", "b5", "c5", "d5", "f5", "g5", "h5")),
    
    # Corner squares - two directions available
    ("a1", False, (), "white", ("a2", "a3", "a4", "a5", "a6", "a7", "a8", "b1", "c1", "d1", "e1", "f1", "g1", "h1")),
    ("h8", False, (), "black", ("h1", "h2", "h3", "h4", "h5", "h6", "h7", "a8", "b8", "c8", "d8", "e8", "f8", "g8")),
    ("a8", False, (), "white", ("a1", "a2", "a3", "a4", "a5", "a6", "a7", "b8", "c8", "d8", "e8", "f8", "g8", "h8")),
    ("h1", False, (), "black", ("h2", "h3", "h4", "h5", "h6", "h7", "h8", "a1", "b1", "c1", "d1", "e1", "f1", "g1")),
    
    # Edge squares - three directions available
    ("a4", False, (), "white", ("a1", "a2", "a3", "a5", "a6", "a7", "a8", "b4", "c4", "d4", "e4", "f4", "g4", "h4")),
    ("h5", False, (), "black", ("h1", "h2", "h3", "h4", "h6", "h7", "h8", "a5", "b5", "c5", "d5", "e5", "f5", "g5")),
    ("d1", False, (), "white", ("d2", "d3", "d4", "d5", "d6", "d7", "d8", "a1", "b1", "c1", "e1", "f1", "g1", "h1")),
    ("e8", False, (), "black", ("e1", "e2", "e3", "e4", "e5", "e6", "e7", "a8", "b8", "c8", "d8", "f8", "g8", "h8")),
    
    # Middle edge squares
    ("b2", False, (), "white", ("b1", "b3", "b4", "b5", "b6", "b7", "b8", "a2", "c2", "d2", "e2", "f2", "g2", "h2")),
    ("g7", False, (), "black", ("g1", "g2", "g3", "g4", "g5", "g6", "g8", "a7", "b7", "c7", "d7", "e7", "f7", "h7")),
    
    # Single blocks - vertical direction blocked
    ("d4", False, ("d3",), "white", ("d5", "d6", "d7", "d8", "a4", "b4", "c4", "e4", "f4", "g4", "h4")),
    ("d4", False, ("d5",), "black", ("d1", "d2", "d3", "a4", "b4", "c4", "e4", "f4", "g4", "h4")),
    ("d4", False, ("d2",), "white", ("d3", "d5", "d6", "d7", "d8", "a4", "b4", "c4", "e4", "f4", "g4", "h4")),
    ("d4", False, ("d6",), "black", ("d1", "d2", "d3", "d5", "a4", "b4", "c4", "e4", "f4", "g4", "h4")),
    
    # Single blocks - horizontal direction blocked
    ("d4", False, ("c4",), "white", ("d1", "d2", "d3", "d5", "d6", "d7", "d8", "e4", "f4", "g4", "h4")),
    ("d4", False, ("e4",), "black", ("d1", "d2", "d3", "d5", "d6", "d7", "d8", "a4", "b4", "c4")),
    ("d4", False, ("b4",), "white", ("d1", "d2", "d3", "d5", "d6", "d7", "d8", "c4", "e4", "f4", "g4", "h4")),
    ("d4", False, ("f4",), "black", ("d1", "d2", "d3", "d5", "d6", "d7", "d8", "a4", "b4", "c4", "e4")),
    
    # Multiple blocks on same rank/file
    ("d4", False, ("d3", "d2"), "white", ("d5", "d6", "d7", "d8", "a4", "b4", "c4", "e4", "f4", "g4", "h4")),
    ("d4", False, ("d5", "d6"), "black", ("d1", "d2", "d3", "a4", "b4", "c4", "e4", "f4", "g4", "h4")),
    ("d4", False, ("c4", "b4"), "white", ("d1", "d2", "d3", "d5", "d6", "d7", "d8", "e4", "f4", "g4", "h4")),
    ("d4", False, ("e4", "f4"), "black", ("d1", "d2", "d3", "d5", "d6", "d7", "d8", "a4", "b4", "c4")),
    
    # Blocks on multiple directions
    ("d4", False, ("d3", "e4"), "white", ("d5", "d6", "d7", "d8", "a4", "b4", "c4")),
    ("d4", False, ("d5", "c4"), "black", ("d1", "d2", "d3", "e4", "f4", "g4", "h4")),
    
    # Heavy blocking
    ("d4", False, ("d3", "d5", "c4", "e4"), "white", ()),
    ("e5", False, ("e4", "e6", "d5", "f5"), "black", ()),
    
    
    # Edge cases, corner with blocking
    ("a1", False, ("a2",), "white", ("b1", "c1", "d1", "e1", "f1", "g1", "h1")),
    ("a1", False, ("b1",), "black", ("a2", "a3", "a4", "a5", "a6", "a7", "a8")),
    ("h8", False, ("h7", "g8"), "white", ()),
    
    # No move corner
    ("a1", False, ("a2", "b1"), "white", ()),
    ("h8", False, ("h7", "g8", "h6", "f8"), "black", ()),
    
    # EATING TESTS - when eat=True, blocked squares become capturable
    
    # Single capture - vertical direction
    ("d4", True, ("d3",), "white", ("d3","d5", "d6", "d7", "d8", "a4", "b4", "c4", "e4", "f4", "g4", "h4")),
    ("d4", True, ("d5",), "black", ("d5", "d1", "d2", "d3", "a4", "b4", "c4", "e4", "f4", "g4", "h4")),
    
    # Single capture - horizontal direction
    ("d4", True, ("c4",), "white", ("c4", "d1", "d2", "d3", "d5", "d6", "d7", "d8", "e4", "f4", "g4", "h4")),
    ("d4", True, ("e4",), "black", ("e4", "d1", "d2", "d3", "d5", "d6", "d7", "d8", "a4", "b4", "c4")),
    
    # Multiple captures on same direction
    ("d4", True, ("d3", "d2"), "white", ("d3", "d5", "d6", "d7", "d8", "a4", "b4", "c4", "e4", "f4", "g4", "h4")),
    ("d4", True, ("e4", "f4"), "black", ("e4", "d1", "d2", "d3", "d5", "d6", "d7", "d8", "a4", "b4", "c4")),
    
    # Captures on multiple directions
    ("d4", True, ("d3", "e4"), "white", ("d3", "e4", "d5", "d6", "d7", "d8", "a4", "b4", "c4")),
    ("d4", True, ("d5", "c4"), "black", ("d5", "c4", "d1", "d2", "d3", "e4", "f4", "g4", "h4")),
    
    # All directions with captures
    ("d4", True, ("d3", "d5", "c4", "e4"), "white", ("d3", "d5", "c4", "e4")),
    ("e5", True, ("e4", "e6", "d5", "f5"), "black", ("e4", "e6", "d5", "f5")),
    
    # Corner captures
    ("a1", True, ("a2",), "white", ("a2", "b1", "c1", "d1", "e1", "f1", "g1", "h1")),
    ("a1", True, ("a2", "b1"), "black", ("a2", "b1")),
    ("h8", True, ("h7", "g8"), "white", ("h7", "g8")),
    
    ("b2", True, ("b1", "c2"), "black", ("b1", "c2", "b3", "b4", "b5", "b6", "b7", "b8", "a2")),
    ("g7", True, ("g8", "f7", "h7"), "white", ("g8", "f7", "h7", "g1", "g2", "g3", "g4", "g5", "g6")),
])
def test_rook_attacks(square,eat,blocked_squares,colour,expected_squares):
    board_rep = BoardRep()
    move_handler = MoveHandler(board_rep)
    validator = ValidMoves(board_rep)
    opposite_colour = "white" if colour == "black" else "black"

    move_handler.set_bit(
        square = conversions.algebraic_to_bitboard(square),
        piece = "rook",
        colour = colour
    )
    expected_moves = 0 
    for expected_square in expected_squares:
        expected_moves |= conversions.algebraic_to_bitboard(expected_square)
        
    for blocked_square in blocked_squares:
        move_handler.set_bit(
            square= conversions.algebraic_to_bitboard(blocked_square),
            piece = "pawn",
            colour = colour if eat == False else opposite_colour) #i.e. if we want the piece at the blocked square to be eaten we should make it the opposite_colour
    board = board_rep.bitboard_white if colour == "white" else board_rep.bitboard_black
    actual_moves = validator.rook_attacks(board["rook"], colour)
    assert actual_moves==expected_moves

