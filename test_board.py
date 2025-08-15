import pytest
from boardrep import BoardRep, ValidMoves
import munchkin
import conversions
def bitboard_to_string(bitboard: int, piece_bb:int = 0) -> str:
    board_str = ""
    for rank in range(7, -1, -1):
        board_str += f"{rank + 1} | "
        for file in range(8):
            square_index = rank * 8 + file
            square_bit = 1<<square_index
            if piece_bb & square_bit:
                board_str += "P "
            elif bitboard & square_bit:
                board_str += "X "
            else:
                board_str += ". "
        board_str += "\n"
    board_str += "  +-----------------\n"
    board_str += "    A B C D E F G H\n"
    return board_str

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
    ("e2", (False,), "white", ("e3", "e4")), 
    ("e4", (False,), "white", ("e5",)),
    ("e4", (True,"e5"), "white", ()),
    ("e7", (False,), "black", ("e6", "e5")), 
    ("e5", (False,), "black", ("e4",)),
])
def test_pawn_forward_moves(square,blocked, colour, expected_moves, board_factory, validator_factory):

    board_rep = board_factory()
    validator = validator_factory(board_rep)


    board_rep.set_bit(
        square=conversions.algebraic_to_bitboard(square),
        piece="pawn",
        colour=colour
    )

    opponent_colour = "black" if colour == "white" else "white"
    if blocked[0]:
        board_rep.set_bit(conversions.algebraic_to_bitboard(blocked[1]),"pawn",colour = opponent_colour)

    board = board_rep.bitboard_white if colour == "white" else board_rep.bitboard_black
    
    bitboard_expected_moves = 0
    for move in expected_moves:
        bitboard_expected_moves |= conversions.algebraic_to_bitboard(move)
    
    actual_moves = validator.pawn_attacks(board["pawn"], colour)
    print(f"\nTesting pawn on {square} with {colour}. Blocked = {blocked[0]}")
    print(f"\n{bitboard_to_string(actual_moves,conversions.algebraic_to_bitboard(square))}")

    assert actual_moves == bitboard_expected_moves
   
    




