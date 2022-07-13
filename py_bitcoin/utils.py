import hashlib


BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def hash256(s):
    """Makes two rounds of sha256 hashing."""
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()


def encode_base58(s):
    """
    Encodes public key to BASE58 format.

    args:
        s: public key in binary format.

    returns:
        private key in encode in BASE58 format.
    """
    count = 0
    # looping to determine how many bytes at the front are 0 bytes
    # to add them back at the end
    for c in s:
        if c == 0:
            count += 1
        else:
            break
    num = int.from_bytes(s, 'big')
    prefix = '1' * count
    result = ''
    # figuring out which BASE58 symbol to use
    while num > 0:
        num, mod = divmod(num, 58)
        result = BASE58_ALPHABET[mod] + result
    # prepend the zeros that we counted at the front
    return prefix + result


def encode_base58_checksum(b):
    """Encode to BASE58 with a checksum."""
    return encode_base58(b + hash256(b)[:4])


def hash160(s):
    """sha256 followed by ripemd160."""
    return hashlib.new('ripemd160', hashlib.sha256(s).digest()).digest()

