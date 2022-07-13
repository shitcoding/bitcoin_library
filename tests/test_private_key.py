import pytest
from random import randint

from py_bitcoin.ecc import A, B, G, N, S256Field, S256Point, Signature, PrivateKey


def test_signature_verification():
    """
    Test ECDSA secp256k1 signature verification.
    """
    # Test signature verification with predefined private key and signature.
    point = S256Point(
        0x887387e452b8eacc4acfde10d9aaf7f6d9a0f975aabb10d006e4da568744d06c,
        0x61de6d95231cd89026e286df3b6ae4a894a3378e393e93a0f45b666329a0ae34
    )
    # signature 1
    z1 = 0xec208baa0fc1c19f708a9ca96fdeff3ac3f230bb4a7ba4aede4942ad003c0f60
    r1 = 0xac8d1c87e51d0d441be8b3dd5b05c8795b48875dffe00b7ffcfac23010d3a395
    s1 = 0x68342ceff8935ededd102dd876ffd6ba72d6a427a3edb13d26eb0781cb423c4
    signature1 = Signature(r1, s1)
    # signature 2
    z2 = 0x7c076ff316692a3d7eb3c3bb0f8b1488cf72e1afcd929e29307032997a838a3d
    r2 = 0xeff69ef2b1bd93a66ed5219add4fb51e11a840f404876325a1e8ffe0529a2c
    s2 = 0xc7207fee197d27c618aea621406f6bf5ef6fca38681d82b2f06fddbdce6feab6
    signature2 = Signature(r2, s2)

    assert point.verify(z1, signature1)
    assert point.verify(z2, signature2)

    # Test signature verification with random signature hash and
    # random private key
    pk = PrivateKey(randint(0, N))
    z = randint(0, 2**256)
    sig = pk.sign(z)
    assert pk.point.verify(z, sig)


SEC_TEST_CASES = (
    (
        999**3,
        '049d5ca49670cbe4c3bfa84c96a8c87df086c6ea6a24ba6b809c9de234496808d56fa15cc7f3d38cda98dee2419f415b7513dde1301f8643cd9245aea7f3f911f9',
        '039d5ca49670cbe4c3bfa84c96a8c87df086c6ea6a24ba6b809c9de234496808d5',
    ),
    (
        123,
        '04a598a8030da6d86c6bc7f2f5144ea549d28211ea58faa70ebf4c1e665c1fe9b5204b5d6f84822c307e4b4a7140737aec23fc63b65b35f86a10026dbd2d864e6b',
        '03a598a8030da6d86c6bc7f2f5144ea549d28211ea58faa70ebf4c1e665c1fe9b5',
    ),
    (
        42424242,
        '04aee2e7d843f7430097859e2bc603abcc3274ff8169c1a469fee0f20614066f8e21ec53f40efac47ac1c5211b2123527e0e9b57ede790c4da1e72c91fb7da54a3',
        '03aee2e7d843f7430097859e2bc603abcc3274ff8169c1a469fee0f20614066f8e',
    ),
)


def test_s256point_serialization_to_sec():
    """
    Testing S256Point serialization to uncompressed and
    compressed binary SEC format.
    """
    for (coef, uncompressed_sec, compressed_sec) in SEC_TEST_CASES:
        point = coef * G
        assert point.sec(compressed=False) == bytes.fromhex(uncompressed_sec)
        assert point.sec(compressed=True) == bytes.fromhex(compressed_sec)

