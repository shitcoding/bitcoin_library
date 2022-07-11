import pytest
from py_bitcoin.ecc import A, B, G, N, FieldElement, Point, S256Field, S256Point


def test_finite_field_point_is_on_curve():
    """
    Testing if the finite field point is on curve.
    If the point is not on curve, ValueError should be raised.
    """
    prime = 223
    a = FieldElement(0, prime)
    b = FieldElement(7, prime)
    valid_points = ((192, 105), (17, 56), (1, 193))
    invalid_points = ((200, 119), (42, 99))
    for x_raw, y_raw in valid_points:
        x = FieldElement(x_raw, prime)
        y = FieldElement(y_raw, prime)
        Point(x, y, a, b)
    for x_raw, y_raw in invalid_points:
        x = FieldElement(x_raw, prime)
        y = FieldElement(y_raw, prime)
        with pytest.raises(ValueError):
            Point(x, y, a, b)


def test_finite_field_point_add():
    test_cases = (
        ((170,142), (60, 139), (220, 181)),
        ((47, 71), (17, 56), (215, 68)),
        ((143, 98), (76, 66), (47, 71)),
    )
    prime = 223
    a = FieldElement(0, prime)
    b = FieldElement(7, prime)
    for (x1, y1), (x2, y2), (x3, y3) in test_cases:
        p1 = Point(FieldElement(x1, prime), FieldElement(y1, prime), a, b)
        p2 = Point(FieldElement(x2, prime), FieldElement(y2, prime), a, b)
        p3 = Point(FieldElement(x3, prime), FieldElement(y3, prime), a, b)
        assert p1 + p2 == p3


def test_finite_field_point_scalar_add():
    """
    Testing scalar addition for elliptic curve points
    over finite field.
    """
    test_cases = ( # scalar addition of points for field over 223
        # (x, y), multiplier, (x_res, y_res)
        ((192, 105), 2, (49, 71)), # 2 ⋅ (192,105) == (49, 71)
        ((143, 98), 2, (64, 168)), # 2 ⋅ (143,98) == (64, 168)
        ((47, 71), 2, (36, 111)), # 2 ⋅ (47,71) == (36, 111)
        ((47, 71), 4, (194, 51)), # 4 ⋅ (47,71) == (194, 51)
        ((47, 71), 8, (116, 55)), # 8 ⋅ (47,71) == (116, 55)
        ((47, 71), 21, (None, None)), # 21 ⋅ (47,71) == (None, None)
    )
    prime = 223
    a = FieldElement(0, prime)
    b = FieldElement(7, prime)
    for (x1, y1), multiplier, (x_res, y_res) in test_cases:
        counter = 1
        p1 = Point(FieldElement(x1, prime), FieldElement(y1, prime), a, b)
        p = p1
        while counter < multiplier:
            p = p + p1
            counter += 1
        if x_res is None: # the resulting point is the point at infinity
            p_res = Point(None, None, a, b)
        else:
            p_res = Point(
                FieldElement(x_res, prime), FieldElement(y_res, prime), a, b
            )
        assert p == p_res


def test_finite_field_point_scalar_mul():
    """
    Testing scalar multiplication of elliptic curve point
    over finite field.
    """
    test_cases = ( # scalar multiplication of points for field over 223
        # (x, y), multiplier, (x_res, y_res)
        ((192, 105), 2, (49, 71)), # 2 ⋅ (192,105) == (49, 71)
        ((143, 98), 2, (64, 168)), # 2 ⋅ (143,98) == (64, 168)
        ((47, 71), 2, (36, 111)), # 2 ⋅ (47,71) == (36, 111)
        ((47, 71), 4, (194, 51)), # 4 ⋅ (47,71) == (194, 51)
        ((47, 71), 8, (116, 55)), # 8 ⋅ (47,71) == (116, 55)
        ((47, 71), 21, (None, None)), # 21 ⋅ (47,71) == (None, None)
    )
    prime = 223
    a = FieldElement(0, prime)
    b = FieldElement(7, prime)
    for (x, y), multiplier, (x_res, y_res) in test_cases:
        p = Point(
            FieldElement(x, prime), FieldElement(y, prime), a, b
        )
        if x_res is None: # the resulting point is the point at infinity
            p_res = Point(None, None, a, b)
        else:
            p_res = Point(
                FieldElement(x_res, prime), FieldElement(y_res, prime), a, b
            )
        assert multiplier * p == p_res


def test_secp256k1_point():
    assert N*G == S256Point(None, None, A, B)
