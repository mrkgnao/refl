from struct import pack

CONSTANTS = {
    'BEGIN_SIZE_SIZE': 0x0000,
    'BEGIN_FILE_CHUNK': 0x00f0,
    'END_FILE_CHUNK': 0x00ff,
    'HASH_MISMATCH': 0xffff
    }

"""Get a packed version of a constant, suitable for network transmission."""
def get_constant_bytes(s):
    return struct.pack("!H", CONSTANTS[s])
