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
    return False, ""

def make_move(board_rep: BoardRep, bitboards:tuple, legal_moves:list,colour:int=0):   
    colour_name = "white" if colour == 0 else "black"
    opponent_colour = "black" if colour_name == "white" else "white"

    on_piece = mouse_on_piece(bitboards[colour])
    if not on_piece[0]:
        return None
    clicked_square, piece = on_piece[1],on_piece[2]
    # wait for release for release of left click
    while True:
        evt = pygame.event.wait()
        if evt.type == pygame.MOUSEBUTTONUP:
            target_square = conversions.pixel_to_square(pygame.mouse.get_pos())
            if (clicked_square,target_square) in legal_moves:
                is_castle = piece == 'king' and abs(conversions.square_to_index(clicked_square) - conversions.square_to_index(target_square)) == 2
                if is_castle:
                    # King-side castle (king moves right)
                    if target_square > clicked_square:
                        rook_start_square = 1 << (conversions.square_to_index(target_square) + 1)
                        rook_end_square = 1 << (conversions.square_to_index(target_square) - 1)
                    # Queen-side castle (king moves left)
                    else:
                        rook_start_square = 1 << (conversions.square_to_index(target_square) - 2)
                        rook_end_square = 1 << (conversions.square_to_index(target_square) + 1)

                    # Move the rook
                    board_rep.unset_bit(rook_start_square, 'rook', colour_name)
                    board_rep.set_bit(rook_end_square, 'rook', colour_name)
                board_rep.capture_at(target_square,opponent_colour)
                board_rep.unset_bit(clicked_square,piece,colour_name)
                board_rep.set_bit(target_square, piece, colour_name)
                return (piece,clicked_square) 
            else:
                return None 
                
            
def main():
    b = BoardRep()
    bitboards = b.initial_position()
    WHITE_IMGS, BLACK_IMGS = pieces.piece_images(pygame, constants.SQUARE_SIZE)

    running, turn = True, 0  # 0 = white, 1 = black
    game_over = False
    clock = pygame.time.Clock()

    #generate all legal moves for white's first turn
    validator = ValidMoves(b)
    castling_white = [False,False,False]
    castling_black = [False,False,False]
    validator.castling_white = castling_white  
    validator.castling_black = castling_black 

    current_legal_moves = validator.generate_all_legal_moves("white")

    while running:
        clock.tick(60)
        board_gui(screen)
        draw_pieces(screen, (b.bitboard_white, b.bitboard_black), (WHITE_IMGS, BLACK_IMGS))
        pygame.display.flip()

        if game_over: # if the game is over I still want to be able to see the board
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False #quit only after the quit event
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN: 
                current_player_colour = "white" if turn==0 else "black"
                move_info = make_move(b, (b.bitboard_white, b.bitboard_black),legal_moves=current_legal_moves, colour=turn)
                if move_info:
                    moved_piece, start_square = move_info
                    #generate all new legal moves
                    if moved_piece == "king":
                        if current_player_colour == "white":
                            castling_white[0] = True
                        if current_player_colour == "black": 
                            castling_black[0] = True

                    if moved_piece == "rook":
                        if current_player_colour == "white":
                            if start_square == 1: #queen-side
                                castling_white[2] = True
                            if start_square == 1<<7: #king-side
                                castling_white[1] = True
                        if current_player_colour == "black": 
                            if start_square == 1<<56: #queen-side
                                castling_black[2] = True
                            if start_square == 1<<63: #king-side
                                castling_black[1] = True

                    turn ^= 1 # flip after a legal move
                    next_player_colour = "white" if turn ==0 else "black"
                    opponent_colour = "black" if turn==0 else "white"
                    validator = ValidMoves(b)
                    validator.castling_white = castling_white 
                    validator.castling_black = castling_black
                    current_legal_moves = validator.generate_all_legal_moves(next_player_colour)
                    #print(current_legal_moves)
                    if not current_legal_moves:
                        king_position = b.bitboard_white["king"] if current_player_colour == "white" else b.bitboard_black["king"]
                        if validator.is_square_attacked(king_position,opponent_colour):
                            print(f"CHECKMATE! {opponent_colour.upper()} wins!")

                        else:
                            print("STALEMATE! It's a draw.")

                        game_over=True

if __name__ == '__main__':
    main()

