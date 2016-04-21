from enum import Enum
import struct
from struct import pack, unpack
from random import random

import utils
from utils import pretty_print
import config.settings as settings
from custom_logging import logger
from logged_exception import LoggedException


class Constant(Enum):
    BEG_TX = 0x0000
    END_TX = 0x1111
    BEG_CSIZE = 0x2222
    BEG_COUNT = 0x2020
    END_CSIZE = 0x3333
    END_COUNT = 0x3030
    BEG_DATA = 0x4444
    END_DATA = 0x5555
    BEG_HASH = 0x6666
    END_HASH = 0x7777

    MSG_TYPE_CHUNK = 0x8888
    MSG_TYPE_INFOREQ = 0x9999
    MSG_TYPE_FILE = 0xBBBB
    MSG_TYPE_STRING = 0xCCCC

    BEG_CHUNK = 0xDDDD
    END_CHUNK = 0xEEEE

    INFO_HASH_MISMATCH = 0xDEAD
    INFO_RECV_OK = 0x600D
    REQ_RESEND = 0x5E9D

# -----------------------------------------------------------------------------
# ----------------------------- Transmission ----------------------------------
# -----------------------------------------------------------------------------

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
Pack an unsigned int.
uint_to_bytes :: UInt -> Bytes
This gives us a range of upto 2e32, which means that we can send 4 TB of data
in one request, with 2e32 chunks.
Good enough.
"""


def uint_to_bytes(num):
    return struct.pack("!I", num)

"""
Send a constant.
"""


def send_constant(cst, conn):
    conn.sendall(constant_to_bytes(cst))

"""
Send a request for something.
"""


def send_req(s, conn):
    send_constant(Constant.BEG_TX, conn)
    send_constant(Constant.MSG_TYPE_INFOREQ, conn)
    send_constant(s, conn)
    send_constant(Constant.END_TX, conn)

"""
Send an information opcode.
"""


def send_info(s, conn):
    send_constant(Constant.BEG_TX, conn)
    send_constant(Constant.MSG_TYPE_INFOREQ, conn)
    send_constant(s, conn)
    send_constant(Constant.END_TX, conn)

"""
Prepare a byteseq for transmission.
The "grammar" is
BEG_CHUNK
BEG_CSIZE <size> END_CSIZE
BEG_DATA <data> END_DATA
BEG_HASH <hash> END_HASH
END_CHUNK
An implicit assumption here is that the byteseq passed as an argument is not
larger than the chunk size set in the `settings` module.
"""


def bytes_to_hashed_chunk(s):
    if len(s) > settings.CHUNK_SIZE:
        logger.error("Too big a byteseq to fit in one chunk")
        return

    b = bytearray()

    # Marker for the beginning of the chunk
    b += constant_to_bytes(Constant.BEG_CHUNK)

    # "Size block"
    b += constant_to_bytes(Constant.BEG_CSIZE)
    b += uint_to_bytes(len(s))
    b += constant_to_bytes(Constant.END_CSIZE)

    # "Data block"
    b += constant_to_bytes(Constant.BEG_DATA)
    b += s
    b += constant_to_bytes(Constant.END_DATA)

    # "Hash block"
    b += constant_to_bytes(Constant.BEG_HASH)
    b += utils.get_hash(s)
    b += constant_to_bytes(Constant.END_HASH)

    # Marker for the end of the chunk
    b += constant_to_bytes(Constant.END_CHUNK)

    # logger.debug("Constructed chunk {} for byteseq {}"
    #  .format(pretty_print(b), pretty_print(s)))
    return bytes(b)

"""
Takes a chunk and sends it over.
"""


def send_chunk(chunk, conn, num_retries=settings.MAX_RETRIES, ab=(0, 0)):
    tries_left = num_retries
    while tries_left > 0:
        conn.sendall(chunk)
        if recv_inforeq(conn) != Constant.INFO_RECV_OK:
            tries_left -= 1
            logger.error(
                "Chunk {} of {} apparently received incorrectly "
                "({} out of {} retries left)"
                .format(*ab, tries_left, num_retries))
        else:
            logger.debug("Chunk {} of {} sent successfully".format(*ab))
            break

"""
The grammar is:
BEG_TX
MSG_TYPE_STRING
BEG_COUNT <number of chunks> END_COUNT
<chunks>
END_TX
"""


def send_string(s, conn, num_retries=settings.MAX_RETRIES):
    lst = utils.chunks_of(s, settings.CHUNK_SIZE)
    # Mark the beginning of the transaction
    send_constant(Constant.BEG_TX, conn)
    send_constant(Constant.MSG_TYPE_STRING, conn)

    send_constant(Constant.BEG_COUNT, conn)
    conn.send(uint_to_bytes(len(lst)))
    send_constant(Constant.END_COUNT, conn)

    for ix, ch in enumerate([k.encode() for k in lst]):
        send_chunk(bytes_to_hashed_chunk(ch),
                   conn, num_retries=num_retries, ab=(ix+1, len(lst)))

    send_constant(Constant.END_TX, conn)

# -----------------------------------------------------------------------------
# ------------------------------- Reception -----------------------------------
# -----------------------------------------------------------------------------

"""
Convert a packed unsigned short into a Constant.
bytes_to_constant :: Bytes -> Constant
"""


def bytes_to_constant(b):
    return Constant((struct.unpack("!H", b))[0])

"""
Unpack an unsigned short.
bytes_to_ushort :: Bytes -> UShort
"""


def bytes_to_ushort(b):
    return (struct.unpack("!H", b))[0]

"""
Unpack an unsigned int.
bytes_to_ushort :: Bytes -> UShort
"""


def bytes_to_uint(b):
    return (struct.unpack("!I", b))[0]

"""
Return None if parse fails because this is not Haskell and I don't know the
Pythonic way to emulate Maybe.
hashed_chunk_to_bytes :: Bytes -> Maybe Bytes
"""


def hashed_chunk_to_bytes(ch):
    pass

"""
Receive a constant, really.
"""


def recv_inforeq(conn):
    try:
        match_next(Constant.BEG_TX, conn)
        match_next(Constant.MSG_TYPE_INFOREQ, conn)
        ir = bytes_to_constant(conn.recv(2))
        match_next(Constant.END_TX, conn)
        return ir
    except LoggedException as le:
        le.log()

"""

"""


def match_next(opcode, conn):
    received_bytes = conn.recv(2)
    expected_bytes = constant_to_bytes(opcode)

    if received_bytes != expected_bytes:
        logger.error("Unexpected opcode: "
                     "expected {}, received {}"
                     .format(
                      pretty_print(expected_bytes),
                      pretty_print(received_bytes)))
    else:
        pass  # logger.info("Received expected opcode {}".format(opcode))

"""

"""


def consume_till_next(opcode, conn):
    expected_bytes = constant_to_bytes(opcode)
    (fst, snd) = (expected_bytes[:1], expected_bytes[1:])
    skip = bytearray()
    done = False

    try:
        while not done:
            rfst = conn.recv(1)
            if rfst != fst:
                    skip += rfst
                    continue
            else:
                rsnd = conn.recv(1)
                if rsnd != snd:
                    skip += rsnd
                else:
                    done = True
        if len(skip) > 0:
            logger.warning("Skipping {} bytes".format(len(skip)))
    except LoggedException as le:
        le.log()

    # logger.info("Received expected opcode {}"
    # .format(opcode))

"""
Receive a packed ushort.
"""


def recv_ushort(conn):
    return bytes_to_ushort(conn.recv(2))


"""
Receive a packed uint.
"""


def recv_uint(conn):
    return bytes_to_uint(conn.recv(4))

"""
Receive a chunk.
"""


def recv_chunk(conn, num_retries):
    tries_left = num_retries
    while tries_left > 0:
        try:
            # Assume that the previous send failed, and skip over as much of
            # the stream as is required.
            consume_till_next(Constant.BEG_CHUNK, conn)

            match_next(Constant.BEG_CSIZE, conn)
            size = recv_uint(conn)
            match_next(Constant.END_CSIZE, conn)

            match_next(Constant.BEG_DATA, conn)
            data = conn.recv(size)
            match_next(Constant.END_DATA, conn)

            match_next(Constant.BEG_HASH, conn)
            actual_hash = conn.recv(settings.HASH_LEN)
            match_next(Constant.END_HASH, conn)

            match_next(Constant.END_CHUNK, conn)
            calc_hash = utils.get_hash(data)

            if (calc_hash == actual_hash and
                    random() < settings.FAKE_ERROR_THRESHOLD):

                logger.debug("Chunk received, hashes match (both {})"
                             .format(pretty_print(calc_hash)))
                send_info(Constant.INFO_RECV_OK, conn)
                return data
            else:
                tries_left -= 1
                send_info(Constant.INFO_HASH_MISMATCH, conn)
                raise LoggedException("Hash mismatch!")
        except LoggedException as le:
            tries_left -= 1
            le.log()

"""
Receive a string.
"""


def recv_string(conn, num_retries=settings.MAX_RETRIES):
    ba = bytearray()
    try:
        consume_till_next(Constant.BEG_TX, conn)
        match_next(Constant.MSG_TYPE_STRING, conn)
        match_next(Constant.BEG_COUNT, conn)
        num_chunks = recv_uint(conn)
        match_next(Constant.END_COUNT, conn)

        for i in range(num_chunks):
            ba += recv_chunk(conn, num_retries=num_retries)

        match_next(Constant.END_TX, conn)
        # logger.debug("Received string {}".format(pretty_print(ba)))
        # return bytes(ba)
    except LoggedException as le:
        le.log()
