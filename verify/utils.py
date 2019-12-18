import hashlib
from functools import partial
import xxhash


def checksum(filename, algorithm='md5', bs=0):
    if algorithm == 'xxh32':
        hasher = xxhash.xxh32()
    elif algorithm == 'xxh64':
        hasher = xxhash.xxh64()
    elif algorithm in ('md5', 'sha512'):
        hasher = hashlib.new(algorithm)
    else:
        raise NotImplementedError
    chunksize = max(bs, hasher.block_size * 32)
    with open(filename, 'rb') as f:
        for chunk in iter(partial(f.read, chunksize), b''):
            hasher.update(chunk)
    return hasher.hexdigest()
