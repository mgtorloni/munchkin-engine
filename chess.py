import pygame
from boardrep import BoardRep,ValidMoves
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
    """

    for side_index, side_bitboards in enumerate(board):
        for piece_name, bitboard in side_bitboards.items():
            while bitboard:
                lsb = bitboard & -bitboard           # isolate lowest set bit
                square_index = lsb.bit_length() - 1  # square [0..63]
                
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
    return False, ""

def main():
    b = BoardRep()
    bitboards = b.initial_position()
    print(b)
    #Variables that we are going to need for the main loop:
    running = True
    clicked = False
    square = None
    piece = None 
    attack_functions = dict()  
    #-----------------
    
    while running:
        board_gui(screen)
        draw_pieces(screen, bitboards, pieces.piece_images(pygame,SQUARE_SIZE))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                on_piece = mouse_on_piece(bitboards[0]) #we are only checking for white pieces

                if on_piece[0]: #if we have clicked on a piece
                    clicked = True
                    square = on_piece[1] # we save that square 
                    piece = on_piece[2] #we save that piece

                    v = ValidMoves(b)
                    attack_functions = {
                        "pawn": v.pawn_attacks,   
                        "rook": v.rook_attacks,   
                        "knight": v.knight_attacks, 
                        "bishop": v.bishop_attacks,
                        "queen": v.queen_attacks,
                        "king": v.king_attacks
                    }
                    valid_attacks = attack_functions[piece](square) #Since we are not specifying the color we always get "white"
                if not on_piece[0] and clicked: # If we have clicked on a piece and now we are clicking on another square
                    if (conversions.pixel_to_square(pygame.mouse.get_pos()) & valid_attacks):
                        print(f"Move {piece} on {conversions.squares_from_rep(square)} to {conversions.squares_from_rep(conversions.pixel_to_square(pygame.mouse.get_pos()))}")

                    clicked = False 
                
            if event.type == pygame.MOUSEBUTTONUP:
                board_gui(screen)
                draw_pieces(screen, bitboards, pieces.piece_images(pygame,SQUARE_SIZE))
                v = ValidMoves(b)
                pygame.display.flip()
                #TODO: pygame.display.update(rectangles_to_update) 
    pygame.quit()

if __name__ == '__main__':
    main()

