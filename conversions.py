import pygame
import constants 
SQUARE_SIZE = constants.SQUARE_SIZE
def square_to_index(bitboard: int) -> int:
    """Returns index given a bitboard with one bit in it"""     
    return (bitboard & -bitboard).bit_length()-1

def pixel_to_square(coords: tuple[int, int]) -> int:
    x, y = coords
    rank = 8 - int(y) // SQUARE_SIZE
    file = int(x) // SQUARE_SIZE
    index = (rank - 1) * 8 + file
    return 1 << index

def square_to_pixel(square: str) -> tuple[int,int]:
    """Converts algebraic notation to pixel coordinates with a1 at bottom left"""
    file = square[0].lower()
    rank = int(square[1])
    x = (ord(file) - ord('a')) * SQUARE_SIZE
    y = (8 - rank) * SQUARE_SIZE
    return (x, y)

def reverse_bitboard(n):
    result = 0
    for i in range(64):
        bit = (n>>i) & 1
        result |= bit << (63 - i)
    return result

