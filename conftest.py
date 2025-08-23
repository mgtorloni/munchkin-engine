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

def pytest_assertrepr_compare(op, left, right):
    if op == "==" and isinstance(left, int) and isinstance(right, int):
        report = [
            "Bitboard assertion failed!",
            "---------------------------",
            "Expected moves:"
        ]
        # Extend the report with each line of the board string
        report.extend(bitboard_to_string(right).splitlines())

        report.append("Actual moves:")
        # Do the same for the actual moves board
        report.extend(bitboard_to_string(left).splitlines())
        
        report.append("---------------------------")
        return report

