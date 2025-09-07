
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

for each side. This can be seen [here](https://github.com/mgtorloni/MunchkinEngine-Chess/blob/master/boardrep.py#L11) in my code. They are initialised as 0s (which is still under a 64-bit integer of course).

So a piece on `a1`, for example, would be expressed as `100000...0 = 1 = 2^0`. And every rank is appended to the end of the next rank, so a piece on `a2` would be `000000001...0 = 2^8` and so on.
## Shifting pieces  
Those are pieces you can generate attacks for simply by shifting bits and applying file masks. These are:
- [Knight](#knight)
- [Pawn](#pawn)
- [King](#king)
### Knight
For this, the knight pattern [page](#resources) of the [Chess Programming Wiki](https://www.chessprogramming.org) is particularly useful. 
To summarise, for this particular pattern, we want to do `attacks & ~own_pieces & 64-bit_mask` where `own_pices` is just the sum of all of the piece bitboards of the colour we care about and `64-bit_mask` is simply `0xFFFFFFFFFFFFFFFF` . The attacks also need to be masked appropriately, as shifting the bits for a knight on `h4` for example will give bits on the `A` and `B` files. Refer to the `knight_attacks` function in [boardrep.py](boardrep.py) for more details.

**Note**: Usually summing is NOT the same as the `OR` operation, in this case though, we are allowed to make use of python's `sum()` function, since no two bits are ever in the same place, so there is no carry overs. Another important point that should be made is that if we also dont `AND` it with a 64-bit mask, we might add an attack that is outside of the board, since the knight attacks function works on shifting bits, we might shift it "too far".

### King
In my implementation of the king move generation, you will see it divided in a few parts:
- **The pseudo move calculation**: This can be done in exactly the same way as the knight pattern, but instead shifting the bits so that the it matches the king pattern.The shifts need to be masked appropriately with certain files as in the same way as with the [knights](#knight) if we have a king on the `H` file, we will get attack squares in the `A` file, see `king_attacks` in [boardrep.py](boardrep.py) for more details.
- **Checking for checks**: For kings, it is important to check if the move we are making isn't going to leave us in check. This is done separately, so in [boardrep.py](boardrep.py) you will see that I have two functions, one named `generate_all_legal_moves` which does this check and `generate_pseudo_legal_moves`, which doesn't do this check. In either case the checking is done, I just call this "checking" in different places to make things more performant in the [Minimax algorithm]() as the `is_square_attacked` function is very expensive.
- **Castling rights**: Checking for castling rights is also done separately, I have made two lists (one for white and one for black) which have each two elements, representing, if that colour can castle king-side, or queen-side. The function `can_castle` in [boardrep.py](boardrep.py) does this check and the function `make_move` (more specifically `_handle_captures` and `_update_game_state`) changes the state appropriately. And if we can castle we add the moves manually at the end, see `generate_pseudo_legal_moves`.
- **Checkmate**:  Checking for checkmate, which is done by checking if there are no legal moves and then checking if the square the king is on is attacked, see [game.py](game.py) for reference 

**Note**: Using this implementation, checking if the king is in check or will be in check, is exactly the same thing i.e. if we don't get out of check we will be in check. The only situation where the distinction is important is when checking for checkmate.

### Pawn
The pawn is an interesting one, just because it has so many edge cases. Let's dive in! When building pawn implementation we need to consider:
- **Attacks**: This is done by shifting the bits so that the pawn in question is attacking the diagonals from it, for the white pawn for example we shift  the bit to the left (to the right for black) by `9 bits` and by `7 bits` so we get the diagonals the pawn should be attacking. The shifts need to be `AND`ded with the `opponents_pieces`, as pawns can only move diagonally if there is an opponent piece there. The shifts need to be masked appropriately with certain files as in the same way as with the [knights](#knight) if we have a pawn on the `H` file, we will get attack squares in the `A` file, see `pawn_attacks` in [boardrep.py](boardrep.py) for more details.
- **Forward moves**: This is done by shifting the bits so that if the pawn in question, is in the second rank we can move twice (or once) given that there are no pieces in the way, if it is not in the second rank and there is no piece in the way, we can move once. Refer to `pawn_attacks` in [boardrep.py](boardrep.py) for more details.
- **En passant**: We check this by making a pawn "double move" trigger the `_update_game_state` to set a special `en_passant_square` variable that is only valid for the immediately following turn.
The pawn_attacks function then generates a valid en passant move by checking if a friendly pawn's normal diagonal attack pattern intersects with this specific target square. 
Finally, if a player makes a move to this square, the `_handle_captures` function executes the special capture by correctly identifying and removing the opponent's pawn from the rank behind the landing square. For this state handling check the `MoveHandler` class in [boardrep.py](boardrep.py) and the end of each outer `if` statement of `pawn_attacks` for more details.
- **Promotion** : This is handled by the `make_move` function in [boardrep.py](boardrep.py), in summary if a pawn gets to `RANK 8` (or `RANK 1`) we unset that bit where the pawn is at, and set it to whatever piece we want (I did it only for queen promotion but it shouldn't be hard to do it for the other pieces). 

## Sliding Pieces
These are rooks, and bishops (and queens, but they are just a rook and a bishop in one).This is where most of the juice is. Here mathematics will be our friend, but fret not, I will be thorough, I promise. 

### Magic Bitboards

To make Magic Bitboards work, we need to make use of a technique called [Perfect Hashing](https://en.wikipedia.org/wiki/Perfect_hash_function#:~:text=In%20computer%20science%2C%20a%20perfect,it%20is%20an%20injective%20function). The whole point of Magic Bitboards, is instead of doing calculations on the fly, we pre-calculate those values and have a lookup table where we can retrieve the attacks we need. This presents a couple of immediate problems, here are some I can think of:
- First, we don't know what we are mapping from, because we need to know not only where (for example) a rook is, but the places of the blockers that affect the attack squares (mathematically, what is our [domain](https://en.wikipedia.org/wiki/Domain_of_a_function)?).
- Second, once we find where we are mapping from, how do we pick up the right index? In other words, what is the function we are going to use so that we are mapping the domain to the [codomain](https://en.wikipedia.org/wiki/Codomain) appropriately?

First lets do this in a formal manner then I will explain it in more simple terms:
The domain of our function as I eluded to before, will be the space of indexes the piece is at, say `I`, cross producted with the positions of the blockers say `B` i.e `IxB`, we need to find an appropriate map from this space to the index of a list which contains the appropriate attack. This involves making an [injective](https://en.wikipedia.org/wiki/Injective_function) function from `IxB` to the index, it has to be injective, since we can't get the same index (attacks) from different blocker patterns (we only consider the relevant blockers here). Also, because we also optimize memory, the function ends up also being [surjective](https://en.wikipedia.org/wiki/Surjective_function)(i.e. [bijective](https://en.wikipedia.org/wiki/Bijection)) but that is not the property we are ultimately solving for.

Logically the problem becomes a bit easier, you fix the piece's square first. For each of the 64 squares, the domain simplifies to just the set of relevant blocker patterns for that specific square. You then find a unique magic number (an injective map) for each of these 64 smaller problems. Easy, haha.

Put it simply, we want to, given a pattern of relevant blockers and the position of the rook, find what are the squares that rook is attacking. That involves finding a formula that maps these two to an index uniquely (no two positions should be the same otherwise there is something wrong).

Let's begin, we first make a list of all of the occupancy masks, for a rook on `a1` for example, we only care about the squares from `a1-g1` and `a1-a7` since a blocker on `a8` wouldn't do anything anyway. Then we make an attack table, which for each occupancy will figure out where the attack files/diagonals have to stop and give the full attack as a bitboard for that variation. Because this is a single list, we actually need to be able to find where the variations for each fixed square finishes and ends so we can navigate it, that is why we also have an `offset table`. Finally we need for each occupancy we need to find a `magic number` which we are going to truncate to find the index, this leaves us with a table of magic numbers and shifts as well.


### Hyperbola Quintessence
I used this youtube video when I was first exploring sliding pieces: [Hyperbola Quintessence](https://www.youtube.com/watch?v=bCH4YK6oq8M), but also, a very rich, well explained source is [Chess Programming Wiki](https://www.chessprogramming.org/Hyperbola_Quintessence). 


# Design & Future Work 
Some parts of this engine could certainly be implemented more elegantly. For those following this guide to build their own engine, I encourage you to focus on encapsulation and good object-oriented principles. Some parts of the codebase may be refactored to reflect this even better in the future. 

Furthermore, a very critical performance issue comes from the parallelism in my minimax algorithm, the alpha beta values are not shared, so each "thread" will have their own alpha beta values cutting less branches out of the tree. But the performance gain was enough that having one "thread" was worse than multiple cutting less branches. Having some kind of way of sharing the values would cut the amount of branches down significantly.  

Finally, there is something that doesn't feel good to me about the amount of for loops I use when I generate the legal moves, every bitboard has to be looped through for the the most relevant bit, it feels like this could be fixed by adding a bitboard for each individual piece, but it is not immediate to me how much that would help in terms of performance.

# Resources
- [A step-by-step guide to building a simple chess AI](https://www.freecodecamp.org/news/simple-chess-ai-step-by-step-1d55a9266977/)
- [Visualizing Chess bitboards](https://healeycodes.com/visualizing-chess-bitboards)
- [Magical Bitboards and How to Find Them: Sliding move generation in chess](https://analog-hors.github.io/site/magic-bitboards/)
- [Hyperbola Quintessence Explained](https://www.youtube.com/watch?v=bCH4YK6oq8M)
- [Chess Programming Wiki](https://www.chessprogramming.org):
  - [Knight attacks](https://www.chessprogramming.org/Knight_Pattern)
  - [King attacks](https://www.chessprogramming.org/King_Pattern)
  - [Pawn attacks](https://www.chessprogramming.org/Pawn_Attacks_(Bitboards))
  - [Hyperbola Quintessence](https://www.chessprogramming.org/Hyperbola_Quintessence)
  