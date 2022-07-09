import pytest
from py_bitcoin.ecc import Point


def test_point_not_on_the_curve():
    """Creating a point not on the curve should raise ValueError."""
    x1, y1 = 2, 4
    x2, y2 = 5, 7
    a, b = 5, 7
    with pytest.raises(ValueError):
        p1 = Point(x1, y1, a, b)
    with pytest.raises(ValueError):
        p2 = Point(x2, y2, a, b)


def test_points_eq():
    """Testing points equality."""
    a = Point(x=3, y=-7, a=5, b=7)
    b = Point(x=3, y=-7, a=5, b=7)
    assert a == b


def test_points_ne():
    """Testing points inequality."""
    a = Point(x=3, y=-7, a=5, b=7)
    b = Point(x=3, y=-7, a=5, b=7)
    c = Point(x=18, y=77, a=5, b=7)
    assert a != c
    assert not a != b


def test_points_add():
    """Testing points addition."""
    # Addition of points with different a or b should raise TypeError
    p1 = Point(-1, -1, 5, 7)
    p2 = Point(-1, 1, 6, 8)
    with pytest.raises(TypeError):
        p3 = p1 + p2

    # Testing addition with point at infinity
    p1 = Point(-1, -1, 5, 7)
    p2 = Point(-1, 1, 5, 7)
    inf = Point(None, None, 5, 7)
    assert (p1 + inf == p1)
    assert (p2 + inf == p2)
    assert (p1 + p2 == inf)

    # Testing addition with x1 != x2
    p1 = Point(2, 5, 5, 7)
    p2 = Point(-1, -1, 5, 7)
    assert (p1 + p2 == Point(3, -7, 5, 7))

    # Testing addition with p1 == p2 (tangential slope)
    p = Point(-1, -1, 5, 7)
    assert (p + p == Point(18, 77, 5, 7))
