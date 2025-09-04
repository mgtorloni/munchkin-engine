import pygame
from boardrep import BoardRep, ValidMoves, MoveHandler
import pieces
import conversions
import constants
import munchkin
import os 
#------------------INIT-------------------
WIDTH, HEIGHT = 960, 960 # Size of window
SQUARE_SIZE:int = constants.SQUARE_SIZE  # The size of each square in the chess board
x = 600  # How far from the left of the screen
y = 30 # How far from the top of the screen
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y) # Set where the pygame window will appear

# Square colours
WHITE_SQUARE = (237,237,234)
BLACK_SQUARE = (50, 104, 75)

#-----------------------------------------

def board_gui(screen: pygame.Surface)->None:
    """Draw the chessboard """
    for i in range(8):
        for j in range(8):
            color = WHITE_SQUARE if (i + j) % 2 == 0 else BLACK_SQUARE # Alternate the colours
            pygame.draw.rect(screen, color, pygame.Rect(j * SQUARE_SIZE, i * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(
    screen: pygame.Surface, 
    board: tuple[dict[str, int], dict[str, int]], 
    piece_images: tuple[dict[str, pygame.Surface], dict[str, pygame.Surface]]) -> None:
    """
    Draw all pieces from both sides on the board.
    """

    for side_index, side_bitboards in enumerate(board):
        for piece_name, bitboard in side_bitboards.items():
            while bitboard:
                lsb = bitboard & -bitboard           # Isolate lowest set bit
                square_index = lsb.bit_length() - 1  # Take one away since we want [0..63] 
                
                # Compute x,y on display
                x = (square_index % 8) * SQUARE_SIZE
                y = (7 - (square_index // 8)) * SQUARE_SIZE  # flip rank

                # Get the correct piece image from piece_images[side_index]
                piece_surf = piece_images[side_index][piece_name]
                piece_rect = piece_surf.get_rect()
                piece_rect.center = (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2)
                screen.blit(piece_surf, piece_rect)

                # Clear the bit we just drew
                bitboard &= bitboard - 1

def mouse_on_piece(bitboard:dict[str,int]) -> tuple[bool,str]:
    """Returns if you have clicked on a piece, the square that piece is on and the piece as a tuple"""
    mouse_pos = pygame.mouse.get_pos()
    clicked_square = conversions.pixel_to_square(mouse_pos)
    for piece, bitboard in bitboard.items(): #for every piece and bitboard in the dictionary
        if clicked_square & bitboard: #if the clicked_square & bitboard != 0 then we have clicked on a piece
            return (True, clicked_square, piece)
    return False, 0, ""

def handle_move(board_rep: BoardRep, move_handler:MoveHandler, legal_moves:list,  colour: int = 0) -> bool:
    """Handles the user's move"""
    on_piece_result = mouse_on_piece(board_rep.bitboard_white if colour == "white" else board_rep.bitboard_black)
    if not on_piece_result[0]:
        return False # There wasn't a piece where the user clicked
    #Otherwise we clicked on a piece
    source_square,piece_moved = on_piece_result[1], on_piece_result[2]
    while True:
        evt = pygame.event.wait()
        if evt.type == pygame.MOUSEBUTTONUP: # When we 'unclick'
            target_square = conversions.pixel_to_square(pygame.mouse.get_pos()) #Figure out where it should go on the board
            move = (source_square,target_square) # Save the move

            if move in legal_moves: # If that move is a legal move
                move_handler.make_move(move = move, colour = colour) # Act on the board
                return True # We have made a move
            else:
                return False # If it wasn't a legal move don't act on the board and signal that a move wasn't made

    
def main():
    b = BoardRep()
    move_handler = MoveHandler(b)
    b.initial_position() # Set the pieces in position

    running, turn = True, 0  # 0 = white, 1 = black
    game_over = False
    game_mode = None

    while game_mode is None:
        choice = input("Select game mode:\n1: Player vs Player\n2: Player vs AI\nEnter choice (1 or 2): ")
        if choice == '1':
            game_mode = 'pvp'
        elif choice == '2':
            game_mode = 'pvai'
        else:
            print("Invalid choice. Please enter 1 or 2.")


    #------------------Config-----------------
    pygame.display.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    WHITE_PCS, BLACK_PCS = pieces.piece_images(pygame, constants.SQUARE_SIZE)
    clock = pygame.time.Clock()
    #-----------------------------------------
    #generate all legal moves for white's first turn
    validator = ValidMoves(b)
    current_legal_moves = validator.generate_all_legal_moves("white")
    
    while running:
        clock.tick(60)
        board_gui(screen)
        draw_pieces(screen, (b.bitboard_white, b.bitboard_black), (WHITE_PCS, BLACK_PCS))
        pygame.display.flip()

        if game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            continue

        current_player_colour = "white" if turn == 0 else "black"
        move_made = False
        
        is_ai_turn = (game_mode == 'pvai' and current_player_colour == 'black')

        if is_ai_turn:
            move_made = munchkin.munchkin_move(board_rep=b, legal_moves=current_legal_moves, colour=current_player_colour)
        
        for event in pygame.event.get(): # For every event
            if event.type == pygame.QUIT:
                running = False # If we click X we stop running
            
            # Handle human move only if it's not the AI's turn
            if not is_ai_turn and event.type == pygame.MOUSEBUTTONDOWN: # If the user clicked somewhere
                move_made = handle_move(b,move_handler, legal_moves=current_legal_moves, colour=current_player_colour)

        if move_made:
            turn ^= 1 # flip after a legal move
            next_player_colour = "white" if turn == 0 else "black"
            opponent_colour = "black" if turn == 0 else "white"
            
            current_legal_moves = validator.generate_all_legal_moves(next_player_colour)
            
            if not current_legal_moves: # If there is no legal moves 
                king_position = b.bitboard_white["king"] if next_player_colour == "white" else b.bitboard_black["king"]
                
                if validator.is_square_attacked(king_position, next_player_colour): # And the king is in check
                    print(f"CHECKMATE! {opponent_colour.upper()} wins!") # It is checkmate!
                else:
                    print("STALEMATE! It's a draw.") # If there is no legal moves and the king is not in check, it is stalemate
                game_over = True

if __name__ == '__main__':
    main()


