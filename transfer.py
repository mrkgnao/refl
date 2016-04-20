from enum import Enum
import struct
from struct import pack, unpack

class Constant(Enum):
    BEGIN_SIZE_SIZE = 0x0000
    BEGIN_FILE_CHUNK = 0x00f0
    END_FILE_CHUNK = 0x00ff
    HASH_MISMATCH = 0xffff

# ------------------------------------------------------------------------------
# ----------------------------- Transmission -----------------------------------
# ------------------------------------------------------------------------------

"""
Get a packed version of a two-byte constant (unsigned short), suitable for
network transmission.
get_constant_bytes :: Constant -> Bytes
"""
def constant_to_bytes(constant):
    return struct.pack("!H", constant.value)

"""
Convert a string to a packed unsigned short.
get_constant_bytes :: String -> Bytes
"""
def const_string_to_bytes(s):
    return struct.pack("!H", Constant[s].value)

# ------------------------------------------------------------------------------
# ------------------------------- Reception ------------------------------------
# ------------------------------------------------------------------------------

"""
Convert a packed unsigned short into a Constant.
bytes_to_constant :: Bytes -> Constant
"""
def bytes_to_constant(b):
    return Constant((struct.unpack("!H", b))[0])
