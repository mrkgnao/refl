import hashlib

def addr_to_ident(conn):
    return "{}:{}".format(conn[0], conn[1])

def get_hash_str(s):
    return hashlib.md5(s).hexdigest()

"""Hashes a byte-sequence and returns a byte-sequence."""
def get_hash(s):
    return hashlib.md5(s).digest()

def humanized_size(num, use_kibibyte=False):
    base, suffix = 1024, 'iB'
    for x in ['B'] + list(map(lambda x: x+suffix, list('kMGTP'))):
        if -base < num < base:
            return "%3.2f %s" % (num, x)
        num /= base
    return "%3.2f %s" % (num, x)

def chunks_of(s, n):
    return [s[i:i+n] for i in range(0, len(s), n)]

"""Consume two bytes from a bytearray."""
def consume(ba):
    return (ba[:2], ba[2:])
