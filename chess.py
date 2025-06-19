import pygame
from boardrep import BoardRep,ValidMoves
import pieces
import conversions
import constants
from functools import partial 
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

def make_move(board_rep, bitboards, colour=0):   
    colour_name = "white" if colour == 0 else "black"
    opponent_colour = "black" if colour_name == "white" else "white"

    on_piece = mouse_on_piece(bitboards[colour])
    if not on_piece[0]:
        return False
    clicked_square, piece = on_piece[1],on_piece[2]
    v = ValidMoves(board_rep)

    # bind the colour argument once, so later we only pass the square
    attack_functions = {
        "pawn":   partial(v.pawn_attacks,   color=colour_name),
        "rook":   partial(v.rook_attacks,   color=colour_name),
        "knight": partial(v.knight_attacks, color=colour_name),
        "bishop": partial(v.bishop_attacks, color=colour_name),
        "queen":  partial(v.queen_attacks,  color=colour_name),
        "king":   partial(v.king_attacks,   color=colour_name),
    }

    valid_attacks = attack_functions[piece](clicked_square)
    # wait for release for release of left click
    while True:
        evt = pygame.event.wait()
        if evt.type == pygame.MOUSEBUTTONUP:
            target = conversions.pixel_to_square(pygame.mouse.get_pos())
            if target & valid_attacks:
                board_rep.capture_at(target, opponent_colour)
                board_rep.unset_bit(clicked_square, piece, colour_name) #colour passed
                print(colour_name, opponent_colour)
                board_rep.set_bit(target,piece, colour_name)
                return True # legal move made
            return False   # illegal square 
def main():
    b = BoardRep()
    bitboards = b.initial_position()
    WHITE_IMGS, BLACK_IMGS = pieces.piece_images(pygame, constants.SQUARE_SIZE)

    running, turn = True, 0  # 0 = white, 1 = black
    clock = pygame.time.Clock()

    while running:
        clock.tick(60)
        board_gui(screen)
        draw_pieces(screen, (b.bitboard_white, b.bitboard_black), (WHITE_IMGS, BLACK_IMGS))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                moved = make_move(b, (b.bitboard_white, b.bitboard_black), colour=turn)
                if moved:
                    turn ^= 1 # flip after a legal move

if __name__ == '__main__':
    main()

