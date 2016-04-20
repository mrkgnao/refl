import hashlib

def addr_to_ident(conn):
    return "{}:{}".format(conn[0], conn[1])

def get_hash(s):
    return hashlib.md5(s).hexdigest()

def get_hash_bytes(s):
    return hashlib.md5(s).digest()

def humanized_size(num, use_kibibyte=False):
    base, suffix = 1024, 'iB'
    for x in ['B'] + list(map(lambda x: x+suffix, list('kMGTP'))):
        if -base < num < base:
            return "%3.2f %s" % (num, x)
        num /= base
    return "%3.2f %s" % (num, x)
