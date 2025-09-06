import random

def bitboard_to_string(bitboard: int) -> str:
    """Converts a bitboard to a string for visualization"""
    board_str = ""
    for r in range(7, -1, -1):
        board_str += f"{r + 1} | "
        for f in range(8):
            if (bitboard >> (r * 8 + f)) & 1:
                board_str += "X "
            else:
                board_str += ". "
        board_str += "\n"
    board_str += "  +-----------------\n"
    board_str += "    A B C D E F G H\n"
    return board_str

def pop_count(b: int) -> int:
    """Counts the number of set bits in a bitboard"""
    return bin(b).count('1')

def get_lsb_index(b: int) -> int:
    """Gets the index of the least significant bit"""
    return (b & -b).bit_length() - 1

def set_occupancy(index: int, bits_in_mask: int, attack_mask: int) -> int:
    """Generates an occupancy bitboard from an index"""
    occupancy = 0
    for i in range(bits_in_mask):
        square = get_lsb_index(attack_mask)
        attack_mask &= attack_mask - 1
        if (index & (1 << i)):
            occupancy |= (1 << square)
    return occupancy

def generate_rook_mask_magic(square: int) -> int:
    """Generates the blocker mask for a rook on a given square, avoiding edges of the board"""
    mask = 0
    r, f = square // 8, square % 8
    for i in range(1, 7): mask |= (1 << (r * 8 + i))
    for i in range(1, 7): mask |= (1 << (i * 8 + f))
    mask &= ~(1 << square)
    return mask

def generate_rook_attacks_for_table(square: int, occupancy: int) -> int:
    """Generates the full attack set for a rook given a specific blocker pattern"""
    attacks = 0
    r, f = square // 8, square % 8
    # North
    for i in range(r + 1, 8):
        sq_bit = 1 << (i * 8 + f)
        attacks |= sq_bit
        if occupancy & sq_bit: break
    # South
    for i in range(r - 1, -1, -1):
        sq_bit = 1 << (i * 8 + f)
        attacks |= sq_bit
        if occupancy & sq_bit: break
    # East
    for i in range(f + 1, 8):
        sq_bit = 1 << (r * 8 + i)
        attacks |= sq_bit
        if occupancy & sq_bit: break
    # West
    for i in range(f - 1, -1, -1):
        sq_bit = 1 << (r * 8 + i)
        attacks |= sq_bit
        if occupancy & sq_bit: break
    return attacks

def generate_bishop_mask_magic(square: int) -> int:
    """
    Generates the blocker mask for a bishop on a given square avoiding the edges of board
    """
    mask = 0
    r, f = square // 8, square % 8
    # NE
    for i, j in zip(range(r + 1, 7), range(f + 1, 7)): mask |= (1 << (i * 8 + j))
    # NW
    for i, j in zip(range(r + 1, 7), range(f - 1, 0, -1)): mask |= (1 << (i * 8 + j))
    # SE
    for i, j in zip(range(r - 1, 0, -1), range(f + 1, 7)): mask |= (1 << (i * 8 + j))
    # SW
    for i, j in zip(range(r - 1, 0, -1), range(f - 1, 0, -1)): mask |= (1 << (i * 8 + j))
    return mask

def generate_bishop_attacks_for_table(square: int, occupancy: int) -> int:
    """Generates the full attack set for a bishop given a specific blocker pattern"""
    attacks = 0
    r, f = square // 8, square % 8
    # NE
    for i, j in zip(range(r + 1, 8), range(f + 1, 8)):
        sq_bit = 1 << (i * 8 + j)
        attacks |= sq_bit
        if occupancy & sq_bit: break
    # NW
    for i, j in zip(range(r + 1, 8), range(f - 1, -1, -1)):
        sq_bit = 1 << (i * 8 + j)
        attacks |= sq_bit
        if occupancy & sq_bit: break
    # SE
    for i, j in zip(range(r - 1, -1, -1), range(f + 1, 8)):
        sq_bit = 1 << (i * 8 + j)
        attacks |= sq_bit
        if occupancy & sq_bit: break
    # SW
    for i, j in zip(range(r - 1, -1, -1), range(f - 1, -1, -1)):
        sq_bit = 1 << (i * 8 + j)
        attacks |= sq_bit
        if occupancy & sq_bit: break
    return attacks


def find_magic_number(square: int, mask: int, is_bishop: bool) -> tuple[int, int]:
    """
    Finds a suitable magic number and shift for a given square and mask.
    This is a brute-force process.
    """
    attack_generator = generate_bishop_attacks_for_table if is_bishop else generate_rook_attacks_for_table

    bits = pop_count(mask)
    occupancy_variations = 1 << bits
    shift = 64 - bits # The index needs N number of bits. To get the top N bits from a 64-bit result, we must dicard the bottom 64-N bits 
    occupancies = [set_occupancy(i, bits, mask) for i in range(occupancy_variations)]
    attacks = [attack_generator(square, occ) for occ in occupancies]
    
    used_attacks = [0] * occupancy_variations

    for _ in range(100_000_000): # Limit attempts
        magic_number = random.getrandbits(64) & random.getrandbits(64) & random.getrandbits(64)
        # Magic numbers with fewer ones tend to have a better chance of working 
        if pop_count((mask * magic_number) & 0xFF00000000000000) < 6: # This number is unlikely to work
            continue # Try a new magic number

        fail = False
        used_attacks = [0] * occupancy_variations
        for i in range(occupancy_variations):
            # Apply 64-bit mask to simulate C-style integer overflow
            magic_index = ((occupancies[i] * magic_number) & 0xFFFFFFFFFFFFFFFF) >> shift # This is the formula we are trying to cater for
            # and it is a good formula since multiplication by the magic number should scramble the bits enough avoiding as many collisions
            # as possible, then we shift puts it in the size we want. The purpose of this function is MAKING this formula work 

            if used_attacks[magic_index] == 0: # If it is empty we haven't used that slot yet
                used_attacks[magic_index] = attacks[i]
            elif used_attacks[magic_index] != attacks[i]: # If it is not empty and the contents don't match the correct
                #attack pattern for the current occupancy we have a collision. Two different blocker setups produced the same index
                # but require different results.
                fail = True # Therefore this magic number is a failure
                break # Try a new magic number
        
        if not fail:
            return magic_number, shift
    
    print(f"ERROR: Magic number not found for square {square}")
    return 0, 0


if __name__ == "__main__":
    # We create the lookup tables here 
    
    # We use the same logic to do the rooks, just substitute rooks for bishops here
    bishop_magics = [0] * 64
    bishop_shifts = [0] * 64
    bishop_masks = [0] * 64
    bishop_attack_table = []
    
    for square in range(64):
        mask = generate_bishop_mask_magic(square)
        bishop_masks[square] = mask
        
        magic, shift = find_magic_number(square, mask, is_bishop=True)
        bishop_magics[square] = magic
        bishop_shifts[square] = shift
        
        bits = pop_count(mask)
        occupancy_variations = 1 << bits
        
        attack_table_for_square = [0] * occupancy_variations
        for i in range(occupancy_variations):
            occupancy = set_occupancy(i, bits, mask)
            magic_index = ((occupancy * magic) & 0xFFFFFFFFFFFFFFFF) >> shift
            
            attack_table_for_square[magic_index] = generate_bishop_attacks_for_table(square, occupancy)
            
        bishop_attack_table.extend(attack_table_for_square)

    
    print("\n# --- COPY THE OUTPUT BELOW INTO constants.py --- #\n")
    print(f"BISHOP_MAGIC_MASKS = {bishop_masks}\n")
    print(f"BISHOP_MAGICS = {bishop_magics}\n")
    print(f"BISHOP_SHIFTS = {bishop_shifts}\n")
    
    bishop_attack_offsets = [0] * 64
    offset = 0
    for i in range(64):
        bishop_attack_offsets[i] = offset
        offset += (1 << pop_count(bishop_masks[i]))
        
    print(f"BISHOP_ATTACK_OFFSETS = {bishop_attack_offsets}\n")
    print(f"BISHOP_ATTACKS = {bishop_attack_table}\n")
    
    print("# --- END OF DATA --- #")
