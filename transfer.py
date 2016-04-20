from enum import Enum
import struct
from struct import pack, unpack

import utils
import config.settings as settings
import custom_logging

class Constant(Enum):
    BEG_TX = 0x0000
    END_TX = 0x1111
    BEG_SIZE = 0x2222
    END_SIZE = 0x3333
    BEG_DATA = 0x4444
    END_DATA = 0x5555
    BEG_HASH = 0x6666
    END_HASH = 0x7777

    MSG_TYPE_CHUNK = 0x8888
    MSG_TYPE_INFO = 0x9999
    MSG_TYPE_REQ = 0xAAAA
    MSG_TYPE_FILE = 0xBBBB
    MSG_TYPE_STRING = 0xCCCC

    BEG_CHUNK = 0xDDDD
    END_CHUNK = 0xEEEE

    INFO_HASH_MISMATCH = 0xDEAD
    INFO_RECV_OK = 0x2152
    REQ_RESEND = 0x1010

# ------------------------------------------------------------------------------
# ----------------------------- Transmission -----------------------------------
# ------------------------------------------------------------------------------

"""Convenience function that I'm not sure I should use"""
def fix_str(s):
    if type(s) == str:
        s = s.encode()
    return s

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

"""
Pack an unsigned short.
ushort_to_bytes :: UShort -> Bytes
"""
def ushort_to_bytes(num):
    return struct.pack("!H", num)

"""
Prepare a byte-sequence for transmission.
The "grammar" is
BEG_CHUNK
BEG_SIZE <size> END_SIZE
BEG_DATA <chnk> END_DATA
BEG_HASH <hash> END_HASH
END_CHUNK
An implicit assumption here is that the byteseq passed as an argument is not
larger than the chunk size set in the `settings` module.
"""
def bytes_to_hashed_chunk(s):
    if len(s) > settings.CHUNK_SIZE:
        custom_logging.logger.error("Too big a byteseq to fit in one chunk")
        return

    b = bytearray()

    # Marker for the beginning of the chunk
    b += const_string_to_bytes('BEG_CHUNK')

    # "Size block"
    b += const_string_to_bytes('BEG_SIZE')
    b += ushort_to_bytes(len(s))
    b += const_string_to_bytes('END_SIZE')

    # "Data block"
    b += const_string_to_bytes('BEG_DATA')
    b += s
    b += const_string_to_bytes('END_DATA')

    # "Hash block"
    b += const_string_to_bytes('BEG_HASH')
    b += utils.get_hash(s)
    b += const_string_to_bytes('END_HASH')

    # Marker for the end of the chunk
    b += const_string_to_bytes('END_CHUNK')

    return bytes(b)

def send_byte_chunk(bs, conn, num_retries=settings.MAX_RETRIES):
    tries_left = num_retries
    chunk = bytes_to_hashed_chunk(bs)
    while tries_left > 0:
        conn.sendall(chunk)
        if get_info(conn) != Constants.INFO_RECV_OK:
            tries_left -= 1
            custom_logging.logger.error(
            "Chunk apparently received incorrectly ({} out of {} retries left)".format(tries_left, num_retries))
        else:
            custom_logging.logger.debug("Chunk sent successfully")

def send_string(s, conn, num_retries=settings.MAX_RETRIES):
    lst = chunks_of(s, settings.CHUNK_SIZE)
    # I want to do something with map (bytes_to_hashed_chunk . encode) lst
    for ch in [bytes_to_hashed_chunk(k.encode()) for k in lst]:
        send_byte_chunk(ch, conn, num_retries=num_retries)

# ------------------------------------------------------------------------------
# ------------------------------- Reception ------------------------------------
# ------------------------------------------------------------------------------

"""
Convert a packed unsigned short into a Constant.
bytes_to_constant :: Bytes -> Constant
"""
def bytes_to_constant(b):
    return Constant((struct.unpack("!H", b))[0])

"""
Return None if parse fails because this is not Haskell and I don't know the
Pythonic way to emulate Maybe.
hashed_chunk_to_bytes :: Bytes -> Maybe Bytes
"""
def hashed_chunk_to_bytes(ch):
