def piece_images(pygame,square_size:int)->dict: 
    white={
            "pawn": pygame.transform.scale(pygame.image.load("_pieces/white_pawn.png"), (square_size*3/5, square_size*3/5)),
            "knight": pygame.transform.scale(pygame.image.load("_pieces/white_knight.png"), (square_size*3/4, square_size*3/4)), 
            "bishop": pygame.transform.scale(pygame.image.load("_pieces/white_bishop.png"), (square_size*3/4, square_size*3/4)),
            "rook": pygame.transform.scale(pygame.image.load("_pieces/white_rook.png"), (square_size*3/4, square_size*3/4)),
            "queen": pygame.transform.scale(pygame.image.load("_pieces/white_queen.png"), (square_size*3/4, square_size*3/4)),
            "king": pygame.transform.scale(pygame.image.load("_pieces/white_king.png"), (square_size*3/4, square_size*3/4)),
            }
    black={
            "pawn": pygame.transform.scale(pygame.image.load("_pieces/black_pawn.png"), (square_size*3/5, square_size*3/5)),
            "knight": pygame.transform.scale(pygame.image.load("_pieces/black_knight.png"), (square_size*3/4, square_size*3/4)),
            "bishop": pygame.transform.scale(pygame.image.load("_pieces/black_bishop.png"), (square_size*3/4, square_size*3/4)),
            "rook": pygame.transform.scale(pygame.image.load("_pieces/black_rook.png"), (square_size*3/4, square_size*3/4)),
            "queen": pygame.transform.scale(pygame.image.load("_pieces/black_queen.png"), (square_size*3/4, square_size*3/4)),
            "king": pygame.transform.scale(pygame.image.load("_pieces/black_king.png"), (square_size*3/4, square_size*3/4)),
            }
    
    return white,black 
