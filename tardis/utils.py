import hashlib
from functools import partial


def checksum(filename, algorithm='md5', bs=0):
    hasher = hashlib.new(algorithm)
    chunksize = max(bs, hasher.block_size * 32)
    with open(filename, 'rb') as f:
        for chunk in iter(partial(f.read, chunksize), b''):
            hasher.update(chunk)
    return hasher.hexdigest()
