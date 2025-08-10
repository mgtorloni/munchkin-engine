def piece_images(pygame,square_size:int)->dict: 
    white={
            "pawn": pygame.transform.smoothscale(pygame.image.load("_pieces/white_pawn.png"), (square_size, square_size)),
            "knight": pygame.transform.smoothscale(pygame.image.load("_pieces/white_knight.png"), (square_size, square_size)), 
            "bishop": pygame.transform.smoothscale(pygame.image.load("_pieces/white_bishop.png"), (square_size, square_size)),
            "rook": pygame.transform.smoothscale(pygame.image.load("_pieces/white_rook.png"), (square_size, square_size)),
            "queen": pygame.transform.smoothscale(pygame.image.load("_pieces/white_queen.png"), (square_size, square_size)),
            "king": pygame.transform.smoothscale(pygame.image.load("_pieces/white_king.png"), (square_size, square_size)),
            }
    black={
            "pawn": pygame.transform.smoothscale(pygame.image.load("_pieces/black_pawn.png"), (square_size, square_size)),
            "knight": pygame.transform.smoothscale(pygame.image.load("_pieces/black_knight.png"), (square_size, square_size)),
            "bishop": pygame.transform.smoothscale(pygame.image.load("_pieces/black_bishop.png"), (square_size, square_size)),
            "rook": pygame.transform.smoothscale(pygame.image.load("_pieces/black_rook.png"), (square_size, square_size)),
            "queen": pygame.transform.smoothscale(pygame.image.load("_pieces/black_queen.png"), (square_size, square_size)),
            "king": pygame.transform.smoothscale(pygame.image.load("_pieces/black_king.png"), (square_size, square_size)),
            }
    
    return white,black 
