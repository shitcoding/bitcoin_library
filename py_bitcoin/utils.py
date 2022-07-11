import hashlib


def hash256(s):
    """Makes two rounds of sha256 hashing."""
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()
