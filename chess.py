import pygame
from boardrep import BoardRep,ValidMoves
import pieces
import conversions
import constants
from functools import partial 
import munchkin
#------------------INIT-------------------
pygame.init()
WIDTH, HEIGHT = 1280, 960
screen = pygame.display.set_mode((WIDTH, HEIGHT))
SQUARE_SIZE:int = constants.SQUARE_SIZE 

#-----------------------------------------

def board_gui(screen: pygame.Surface)->None:
    """Draw the chessboard """
    for i in range(8):
        for j in range(8):
            color = (237,237,234) if (i + j) % 2 == 0 else (50, 104, 75)
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
                lsb = bitboard & -bitboard           # isolate lowest set bit
                square_index = lsb.bit_length() - 1  # take one away since we want [0..63] 
                
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
    """ Returns if you have clicked on a piece, the square that piece is on and the piece as a tuple e.g. (True,clicked_square,piece)"""
    mouse_pos = pygame.mouse.get_pos()
    clicked_square = conversions.pixel_to_square(mouse_pos)
    for piece, bitboard in bitboard.items(): #for every piece and bitboard in the dictionary
        if clicked_square & bitboard: #if the clicked_square & bitboard != 0 then we have clicked on a piece
            return (True, clicked_square, piece)
    return False, 0, ""

def handle_move(board_rep: BoardRep, legal_moves:list,  colour: int = 0):   
    on_piece_result = mouse_on_piece(board_rep.bitboard_white if colour == "white" else board_rep.bitboard_black)
    if not on_piece_result[0]:
        return False
    source_square,piece_moved = on_piece_result[1], on_piece_result[2]
    while True:
        evt = pygame.event.wait()
        if evt.type == pygame.MOUSEBUTTONUP:
            target_square = conversions.pixel_to_square(pygame.mouse.get_pos())
            move = (source_square,target_square)

            if move in legal_moves:
                board_rep.make_move(move = move,moved_piece = piece_moved, colour = colour)
                return True
            else:
                return False

    
def main():
    b = BoardRep()
    b.initial_position()
    WHITE_IMGS, BLACK_IMGS = pieces.piece_images(pygame, constants.SQUARE_SIZE)

    running, turn = True, 0  # 0 = white, 1 = black
    game_over = False
    game_mode = None
    clock = pygame.time.Clock()

    while game_mode is None:
        choice = input("Select game mode:\n1: Player vs Player\n2: Player vs AI\nEnter choice (1 or 2): ")
        if choice == '1':
            game_mode = 'pvp'
        elif choice == '2':
            game_mode = 'pvai'
        else:
            print("Invalid choice. Please enter 1 or 2.")

    #generate all legal moves for white's first turn
    validator = ValidMoves(b)
    current_legal_moves = validator.generate_all_legal_moves("white")
    
    while running:
        clock.tick(60)
        board_gui(screen)
        draw_pieces(screen, (b.bitboard_white, b.bitboard_black), (WHITE_IMGS, BLACK_IMGS))
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
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle human move only if it's not the AI's turn
            if not is_ai_turn and event.type == pygame.MOUSEBUTTONDOWN:
                move_made = handle_move(b, legal_moves=current_legal_moves, colour=current_player_colour)

        if move_made:
            turn ^= 1 # flip after a legal move
            next_player_colour = "white" if turn == 0 else "black"
            opponent_colour = "black" if turn == 0 else "white"
            
            current_legal_moves = validator.generate_all_legal_moves(next_player_colour)
            
            if not current_legal_moves:
                king_position = b.bitboard_white["king"] if next_player_colour == "white" else b.bitboard_black["king"]
                if validator.is_square_attacked(king_position, next_player_colour):
                    print(f"CHECKMATE! {opponent_colour.upper()} wins!")
                else:
                    print("STALEMATE! It's a draw.")
                game_over = True

if __name__ == '__main__':
    main()


