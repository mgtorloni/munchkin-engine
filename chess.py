import pygame
from boardrep import BoardRep
import pieces
import conversions
import constants
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
            color = (122,74,61) if (i + j) % 2 == 0 else (95, 54, 53)
            pygame.draw.rect(screen, color, pygame.Rect(j * SQUARE_SIZE, i * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(
    screen: pygame.Surface, 
    board: tuple[dict[str, int], dict[str, int]], 
    piece_images: tuple[dict[str, pygame.Surface], dict[str, pygame.Surface]]) -> None:
    """
    Draw all pieces from both sides on the board.
    `board[0]` = dict of white bitboards,
    `board[1]` = dict of black bitboards.
    `piece_images[0]` = dict of white piece images,
    `piece_images[1]` = dict of black piece images.
    """
    SQUARE_SIZE = 120  # or constants.SQUARE_SIZE, etc.

    for side_index, side_bitboards in enumerate(board):
        # side_index = 0 for white, 1 for black
        for piece_name, bitboard in side_bitboards.items():
            while bitboard:
                lsb = bitboard & -bitboard           # isolate lowest set bit
                square_index = lsb.bit_length() - 1  # square [0..63]
                
                # Compute x,y on your display
                x = (square_index % 8) * SQUARE_SIZE
                y = (7 - (square_index // 8)) * SQUARE_SIZE  # flip rank

                # Get the correct piece image from piece_images[side_index]
                piece_surf = piece_images[side_index][piece_name]
                piece_rect = piece_surf.get_rect()
                piece_rect.center = (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2)
                screen.blit(piece_surf, piece_rect)

                # Clear the bit we just drew
                bitboard &= bitboard - 1

def mouse_on_piece(board:dict[str,int]) -> tuple[bool,str]:
    mouse_pos = pygame.mouse.get_pos()
    clicked_square = conversions.pixel_to_square(mouse_pos)
    for piece, bitboard in board.items():
        squares = conversions.squares_from_rep(bitboard)
        if clicked_square in squares:
            return True, clicked_square
    return False, ""

def main():
    b = BoardRep()
    bitboards = b.initial_position()
    
    #Variables that we are going to need for the main loop:
    running = True
    clicked = False
    piece = None 
    #-----------------
    while running:
        board_gui(screen)
        draw_pieces(screen, bitboards, pieces.piece_images(pygame,SQUARE_SIZE))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                on_piece = mouse_on_piece(bitboards[0])#we are only checking for white pieces
                if on_piece[0]:#if we have clicked on a piece
                    clicked = True
                    piece = on_piece[1] # we save that piece
                if not on_piece[0] and clicked: # If we have clicked on a piece and now we are clicking on another square
                    print(f"Move {piece} to: {conversions.pixel_to_square(pygame.mouse.get_pos())}") #This is a progression into updating the board, the next
                    #part is you have to find which of the knights/pawns/rooks/bishops we are moving and then we can redraw the board
                    clicked = False 
            if event.type == pygame.MOUSEBUTTONUP:
                board_gui(screen)
                draw_pieces(screen, bitboards, pieces.piece_images(pygame,SQUARE_SIZE))
                pygame.display.flip()
                #TODO: pygame.display.update(rectangles_to_update) 
    pygame.quit()

if __name__ == '__main__':
    main()

