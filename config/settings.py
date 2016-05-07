SERVER_PORT = 40001
SERVER_HOST = "127.0.0.1"  # at home, of course
SERVER_ADDR = (SERVER_HOST, SERVER_PORT)
SERVER_LISTEN_QUEUE_MAXLEN = 10

"""
The maximum number of times to retry a send operation if there is a hash
mismatch.
"""
MAX_RETRIES = 10

CHUNK_SIZE = 1024*1024
FILE_CHUNK_SIZE = 1024
HASH_ALGORITHM = 'md5'
HASH_LEN = 16

FAKE_ERROR_THRESHOLD = 2
