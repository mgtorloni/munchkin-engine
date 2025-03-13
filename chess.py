import pygame
from boardrep import BoardRep
import pieces
import conversions
#------------------INIT-------------------
pygame.init()
width, height= 1280, 960
screen = pygame.display.set_mode((width, height))
SQUARE_SIZE:int = min(width // 8, height // 8)
#-----------------------------------------

def board_gui(screen: pygame.Surface)->None:
    """Draw the chessboard """
    for i in range(8):
        for j in range(8):
            color = (122,74,61) if (i + j) % 2 == 0 else (95, 54, 53)
            pygame.draw.rect(screen, color, pygame.Rect(j * SQUARE_SIZE, i * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(screen: pygame.Surface, board: tuple[dict[str, int], dict[str, int]], piece_images: dict[str, pygame.Surface]) -> None:
    """Draw the pieces"""
    for side in board:  # two sides in a tuple
        for piece, bitboard in side.items():  # every piece has its own bitboard
            while bitboard:
                lsb = bitboard & -bitboard  # extract least significant bit
                index = lsb.bit_length() - 1  # find square index
                x = (index % 8) * SQUARE_SIZE
                y = (7 - index // 8) * SQUARE_SIZE  # invert rank for correct display
                
                piece_rect = piece_images[piece].get_rect()
                piece_rect.center = (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2)  # center piece in square
                screen.blit(piece_images[piece], piece_rect)  # draw piece
                
                bitboard &= bitboard - 1  # remove processed bit


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

