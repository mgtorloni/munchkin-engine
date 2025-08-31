import time
from boardrep import BoardRep,ValidMoves,MoveHandler
import chess

def perft(depth: int, board_rep: BoardRep, colour: str) -> int:
    if depth == 0:
        return 1

    move_generator = ValidMoves(board_rep)
    move_handler = MoveHandler(board_rep)
    nodes = 0
    
    legal_moves = move_generator.generate_all_legal_moves(colour)

    for move in legal_moves:
        unmake_info = move_handler.make_move(move, colour)
        nodes += perft(depth - 1, board_rep, "black" if colour == "white" else "white")
        move_handler.unmake_move(unmake_info)
        
    return nodes

def perft_python_chess(depth: int, board: chess.Board) -> int:
    if depth == 0:
        return 1

    nodes = 0
    for move in board.legal_moves:
        board.push(move)  # Make the move
        nodes += perft_python_chess(depth - 1, board)
        board.pop()       # Unmake the move

    return nodes

board = BoardRep()
board.initial_position()

depth = 4 # A depth of 4 or 5 is a good test.
start_time = time.time()
node_count = perft(depth, board, "white")
end_time = time.time()

duration = end_time - start_time
nps = node_count / duration

print(f"Depth: {depth}")
print(f"Nodes: {node_count}") 
print(f"Time: {duration:.2f}s")
print(f"Nodes per Second (NPS): {nps:,.0f}")

board = chess.Board()
start_time = time.time()
node_count = perft_python_chess(depth,board)
end_time = time.time()

duration = end_time - start_time
nps = node_count / duration

print(f"--- python-chess ---")
print(f"Nodes per Second (NPS): {nps:,.0f}")
