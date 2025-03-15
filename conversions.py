import pygame
import constants 
SQUARE_SIZE = constants.SQUARE_SIZE
def square_to_index(square: str) -> int:
    """Returns index given algebraic notation of a square"""
    file = square[0].lower()
    rank = int(square[1])
    file_index = ord(file) - ord('a')  # convert file into a decimal 0-7
    rank_index = rank - 1  # converting rank to 0-indexed 
    return rank_index * 8 + file_index

def squares_from_rep(bitboard: int) -> list:
    """Returns a list of the square(s) of the bitboard of a piece in algebraic notation""" 
    squares = []
    for index in range(64):
        if (bitboard >> index) & 1:
            rank_index = index // 8
            file_index = index % 8 
            square = chr(ord('a') + file_index) + str(rank_index + 1)
            squares.append(square)
    return squares

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

def sub_64(a: int, b: int) -> int:
    # (a - b) mod 2^64
    return (a - b) & 0xFFFFFFFFFFFFFFFF

def reverse_bitboard(n):
    result = 0
    for i in range(64):
        bit = (n>>i) & 1
        result |= bit << (63 - i)
    return result

