
# Introduction
Munchkin Engine is a simple move generation chess engine built from scratch that uses minimax with alpha-beta pruning to generate the best moves. 
Although, addimitedly not as powerful as [python-chess](https://github.com/niklasf/python-chess),
this repo is supposed to provide a stack of all the resources used to build a good base for a powerful engine,
but not all the micro-optimizations used to build something like python-chess.
Furthermore, code was tried to be made as clean and well-documented as possible,
making it a fantastic entry-point for beginners trying to get into the world of building chess engines. 

That said, this engine will be rated around 1600-1700 on Lichess, so it will beat the average Joe, but definitely no Masters.  

# The Ultimate Guide to Move Generation
This is a guide that is supposed to explain how each piece moves and common techniques used for move generation such as [Magic Bitboards]() and [Hyperbola Quintessence]().
## Bitboards
This is the most efficient way of representing the board, humans have come up with so far, we use a 64-bit integer to represent the board. Now, I have done this for every piece type, so we have a bitboard:
- For all pawns
- For all knights
- For all bishops
- For all rooks
- For the queen(s)
- For the king

for each side. This can be seen [here](https://github.com/mgtorloni/MunchkinEngine-Chess/blob/master/boardrep.py#L9) in my code. They are initialised as 0s (which is still under a 64-bit integer of course).

So a piece on `a1`, for example, would be expressed as `100000...0 = 1 = 2^0`. And every rank is appended to the end of the next rank, so a piece on `a2` would be `000000001...0 = 2^8` and so on.
## Shifting pieces  
Those are pieces you can generate attacks for simply by shifting bits and applying file masks. These are:
- [Knight](#knight)
- [Pawn](#pawn)
- [King](#king)
### Knight
For this, the knight pattern [page](#resources) of the [Chess Programming Wiki](https://www.chessprogramming.org) is particularly useful. 
To summarise, for this particular pattern, we want to do `attacks & ~own_pieces & 64-bit_mask` where `own_pices` is just the sum of all of the piece bitboards of the colour we care about and `64-bit_mask` is simply `0xFFFFFFFFFFFFFFFF` . 

**Note**: Usually summing is NOT the same as the `OR` operation, in this case though, we are allowed to make use of python's `sum()` function, since no two bits are ever in the same place, so there is no carry overs. Another important point that should be made is that if we also dont `AND` it with a 64-bit mask, we might add an attack that is outside of the board, since the knight attacks function works on shifting bits, we might shift it "too far".

### King
In my implementation of the king move generation, you will see it divided in a few parts:
- **The pseudo move calculation**: This can be done in exactly the same way as the knight pattern, but instead shifting the bits so that the it matches the king pattern.
- **Checking for checks**: For kings, it is important to check if the move we are making isn't going to leave us in check. This is done separately, so in [boardrep.py]() you will see that I have two functions, one named `generate_all_legal_moves` which does this check and `generate_pseudo_legal_moves`, which doesn't do this check. In either case the checking is done, I just call this "checking" in different places to make things more performant in the [Minimax algorithm]() as the `is_square_attacked` function is very expensive.
- **Castling rights**: Checking for castling rights is also done separately, I have made two lists (one for white and one for black) which have each two elements, representing, if that colour can castle king-side, or queen-side. The function `can_castle` in [boardrep.py](https://github.com/mgtorloni/MunchkinEngine-Chess) does this check and the function `make_move` changes the state appropriately. 
- **Checkmate**:  checking for checkmate, which is done by checking if there are no legal moves and then checking if the square the king is on is attacked, see [game.py](https://github.com/mgtorloni/MunchkinEngine-Chess) for reference 

I would say some of these could have been implemented in a more elegant way. And I would encourage the people doing their own chess engine and following this guide to encapsulate these into their own objects as much as one can, following good programming principles. This may well be refactored at a later date.

**Note**: Using this implementation, checking if the king is in check or will be in check, is exactly the same thing i.e. if we don't get out of check we will be in check. The only situation where the distinction is important is when checking for checkmate.

### Pawn
The pawn is an interesting one, just because it has so many edge cases.


# Resources
- [A step-by-step guide to building a simple chess AI](https://www.freecodecamp.org/news/simple-chess-ai-step-by-step-1d55a9266977/)
- [Visualizing Chess bitboards](https://healeycodes.com/visualizing-chess-bitboards)
- [Magical Bitboards and How to Find Them: Sliding move generation in chess](https://analog-hors.github.io/site/magic-bitboards/)
- [Hyperbola Quintessence Explained](https://www.youtube.com/watch?v=bCH4YK6oq8M)
- [Chess Programming Wiki](https://www.chessprogramming.org)
  - [Knight attacks](https://www.chessprogramming.org/Knight_Pattern)
  - [King attacks](https://www.chessprogramming.org/King_Pattern)
  - [Pawn attacks](https://www.chessprogramming.org/Pawn_Attacks_(Bitboards))
  