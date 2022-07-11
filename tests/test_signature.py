import pytest
from py_bitcoin.ecc import A, B, G, N, S256Field, S256Point, Signature


def test_signature_verification():
    """Test ECDSA secp256k1 signature verification."""
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
