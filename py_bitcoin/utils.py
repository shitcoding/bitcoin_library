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


def little_endian_to_int(binary):
    """Return integer from given little-endian byte sequence."""
    return int.from_bytes(binary, 'little')


def int_to_little_endian(num, length):
    """Return little-endian byte sequence from given integer."""
    return num.to_bytes(length, 'little')


def read_varint(stream):
    """Read variable integer from a stream."""
    i = stream.read(1)[0]
    if i == 0xfd:
        # 0xfd means the next 2 bytes are the number
        return little_endian_to_int(stream.read(2))
    elif i == 0xfe:
        # 0xfe means the next 4 bytes are the number
        return little_endian_to_int(stream.read(4))
    elif i == 0xff:
        # 0xff means the next 8 bytes are the number
        return little_endian_to_int(stream.read(8))
    else:
        # anything else is just the integer
        return i


def encode_varint(i):
    """Encode an integer as a variable integer."""
    if i < 0xfd:
        return bytes([i])
    elif i < 0x10000:
        return b'\xfd' + int_to_little_endian(i, 2)
    elif i < 0x100000000:
        return b'\xfe' + int_to_little_endian(i, 4)
    elif i < 0x10000000000000000:
        return b'\xff' + int_to_little_endian(i, 8)
    else:
        raise ValueError(f'integer is too large: {i}')
