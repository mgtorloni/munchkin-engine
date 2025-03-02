def piece_images(pygame,square_size:int)->dict:
    piece_images = {
            "white_pawns": pygame.transform.scale(pygame.image.load("_pieces/white_pawn.png"), (square_size*3/5, square_size*3/5)),
            "black_pawns": pygame.transform.scale(pygame.image.load("_pieces/black_pawn.png"), (square_size*3/5, square_size*3/5)),
            "white_knights": pygame.transform.scale(pygame.image.load("_pieces/white_knight.png"), (square_size*3/4, square_size*3/4)), "black_knights": pygame.transform.scale(pygame.image.load("_pieces/black_knight.png"), (square_size*3/4, square_size*3/4)),
            "white_bishops": pygame.transform.scale(pygame.image.load("_pieces/white_bishop.png"), (square_size*3/4, square_size*3/4)),
            "black_bishops": pygame.transform.scale(pygame.image.load("_pieces/black_bishop.png"), (square_size*3/4, square_size*3/4)),
            "white_rooks": pygame.transform.scale(pygame.image.load("_pieces/white_rook.png"), (square_size*3/4, square_size*3/4)),
            "black_rooks": pygame.transform.scale(pygame.image.load("_pieces/black_rook.png"), (square_size*3/4, square_size*3/4)),
            "white_queen": pygame.transform.scale(pygame.image.load("_pieces/white_queen.png"), (square_size*3/4, square_size*3/4)),
            "black_queen": pygame.transform.scale(pygame.image.load("_pieces/black_queen.png"), (square_size*3/4, square_size*3/4)),
            "white_king": pygame.transform.scale(pygame.image.load("_pieces/white_king.png"), (square_size*3/4, square_size*3/4)),
            "black_king": pygame.transform.scale(pygame.image.load("_pieces/black_king.png"), (square_size*3/4, square_size*3/4)),
        }
    return piece_images 
