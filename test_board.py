import pytest
from boardrep import BoardRep, ValidMoves, MoveHandler
import munchkin
import conversions

@pytest.fixture
def board_factory():
    def _create_board():
        return BoardRep() 
    return _create_board

@pytest.fixture
def validator_factory():
    def _create_validator(board):
        return ValidMoves(board)
    return _create_validator

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
def test_pawn_forward_moves(square,blocked, colour, expected_moves, board_factory, validator_factory):

    board_rep = board_factory()
    move_handler = MoveHandler(board_rep)
    validator = validator_factory(board_rep)


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

def test_pawn_captures(square, not_squares, colour, expected_moves, board_factory, validator_factory):

    board_rep = board_factory()
    move_handler = MoveHandler(board_rep)
    validator = validator_factory(board_rep)

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


"""
def test_enpassant(square, en_passant_square, colour, expected_moved, board_factory, validator_factory):
    board_rep = board_factory()
    move_handler = MoveHandler(board_rep)
    validator = validator_factory(board_rep)

    move_handler.set_bit(
        square=conversions.algebraic_to_bitboard(square),
        piece="pawn",
        colour=colour
    )
"""
