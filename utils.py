import hashlib

def addr_to_ident(conn):
    return "{}:{}".format(conn[0], conn[1])

def get_sha224(s):
    return hashlib.sha224(s).hexdigest()
