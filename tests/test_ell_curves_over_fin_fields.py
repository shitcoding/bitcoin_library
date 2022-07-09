import pytest
from py_bitcoin.ecc import FieldElement, Point


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
    points = (
        ((170,142), (60, 139), (220, 181)),
        ((47, 71), (17, 56), (215, 68)),
        ((143, 98), (76, 66), (47, 71)),
    )
    prime = 223
    a = FieldElement(0, prime)
    b = FieldElement(7, prime)
    for (x1, y1), (x2, y2), (x3, y3) in points:
        p1 = Point(FieldElement(x1, prime), FieldElement(y1, prime), a, b)
        p2 = Point(FieldElement(x2, prime), FieldElement(y2, prime), a, b)
        p3 = Point(FieldElement(x3, prime), FieldElement(y3, prime), a, b)
        assert p1 + p2 == p3

