import pygame
from boardrep import BoardRep
import pieces

def pixel_to_square(coords:tuple[int,int])->str:
    x = coords[0]
    y = coords[1]
    rank = 8-int(y)//SQUARE_SIZE
    file_ord = int(x)//SQUARE_SIZE+ord('a')
    return f"{chr(file_ord)+str(rank)}"

def square_to_pixel(square: str) -> tuple[int,int]:
    """Converts algebraic notation to pixel coordinates with a1 at bottom left"""
    file = square[0].lower()
    rank = int(square[1])
    x = (ord(file) - ord('a')) * SQUARE_SIZE
    y = (8 - rank) * SQUARE_SIZE
    return (x, y)

def board_gui(screen: pygame.Surface)->None:
    """Draw the chessboard """
    for i in range(8):
        for j in range(8):
            color = (122,74,61) if (i + j) % 2 == 0 else (95, 54, 53)
            pygame.draw.rect(screen, color, pygame.Rect(j * SQUARE_SIZE, i * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                

def draw_pieces(screen: pygame.Surface, board:dict[str,list[str]], piece_images:dict[str,pygame.Surface])->None:
    """Draw the pieces"""
    for piece, squares in board.items():
        for square in squares:
            x, y = square_to_pixel(square)
            piece_rect = piece_images[piece].get_rect()
            piece_rect.center = (x+SQUARE_SIZE//2,y+SQUARE_SIZE//2)#define the centre of the rectangle 
            screen.blit(piece_images[piece],piece_rect)#draw 


def mouse_on_piece(board: dict[str,list[str]]) -> bool:
    """Returns True if you clicked on a piece, False otherwise"""
    mouse_pos = pygame.mouse.get_pos()
    for piece,squares in list(board.items())[::2]: #we are only white for now, so only check the even values
        for square in squares:
            x, y = square_to_pixel(square)
            piece_rect = pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE)
            if piece_rect.collidepoint(mouse_pos):
                return (True,piece)
    return (False,None)

#------------------INIT-------------------
pygame.init()
width, height= 1280, 960
screen = pygame.display.set_mode((width, height))
SQUARE_SIZE:int = min(width // 8, height // 8)
#-----------------------------------------

def main():
    b = BoardRep()
    bitboards = b.initial_position()
    
    # dictionary mapping piece names to algebraic square lists
    board = {piece: b.squares_from_rep(bitboards[piece]) for piece in bitboards}
    
    #Variables that we are going to need for the main loop:
    running = True
    clicked = False
    piece = None 
    #-----------------
    while running:
        board_gui(screen)
        draw_pieces(screen, board, pieces.piece_images(pygame,SQUARE_SIZE))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                on_piece = mouse_on_piece(board)
                if on_piece[0]:#if we have clicked on a piece
                    clicked = True
                    piece = on_piece[1] # we save that piece
                if not on_piece[0] and clicked: # If we have clicked on a piece and now we are clicking on another square
                    print(f"Move {piece} to: {pixel_to_square(pygame.mouse.get_pos())}") #This is a progression into updating the board, the next
                    #part is you have to find which of the knights/pawns/rooks/bishops we are moving and then we can redraw the board
                    clicked = False 
            if event.type == pygame.MOUSEBUTTONUP:
                board_gui(screen)
                draw_pieces(screen, board, pieces.piece_images(pygame,SQUARE_SIZE))
                pygame.display.flip()
        
    pygame.quit()

if __name__ == '__main__':
    main()

