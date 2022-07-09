import pytest
from py_bitcoin.ecc import FieldElement


def test_field_element_not_in_range():
    """Creating field element not in field range should raise ValueError."""
    with pytest.raises(ValueError):
        a = FieldElement(-1, 31)
    with pytest.raises(ValueError):
        b = FieldElement(32, 31)


def test_field_element_eq():
    """Test field elements equality."""
    a = FieldElement(2, 31)
    b = FieldElement(2, 31)
    c = FieldElement(3, 31)
    assert a == b
    assert not a == c


def test_field_element_ne():
    """Test field elements inequality."""
    a = FieldElement(2, 31)
    b = FieldElement(5, 31)
    c = FieldElement(5, 31)
    assert a != b
    assert not b != c


def test_field_element_add():
    """Testing field elements addition."""
    # Adding elements in different fields should raise TypeError.
    with pytest.raises(TypeError):
        a = FieldElement(2, 23) + FieldElement(3, 33)

    a = FieldElement(2, 31)
    b = FieldElement(15, 31)
    assert (a + b == FieldElement(17, 31))

    a = FieldElement(17, 31)
    b = FieldElement(21, 31)
    assert (a + b == FieldElement(7, 31))


def test_field_element_sub():
    """Testing field elements substraction."""
    # Substractiong elements in different fields should raise TypeError.
    with pytest.raises(TypeError):
        a = FieldElement(12, 23) - FieldElement(3, 33)

    a = FieldElement(29, 31)
    b = FieldElement(4, 31)
    assert (a - b == FieldElement(25, 31))

    a = FieldElement(15, 31)
    b = FieldElement(30, 31)
    assert (a - b == FieldElement(16, 31))


def test_field_element_mul():
    """Testing field elements multiplication."""
    # Multiplying elements in different fields should raise TypeError.
    with pytest.raises(TypeError):
        a = FieldElement(12, 23) * FieldElement(3, 33)

    a = FieldElement(24, 31)
    b = FieldElement(19, 31)
    assert (a * b == FieldElement(22, 31))


def test_field_element_pow():
    """Testing field elements exponentiation."""
    a = FieldElement(17, 31)
    assert (a**3 == FieldElement(15, 31))

    a = FieldElement(5, 31)
    b = FieldElement(18, 31)
    assert (a**5 * b == FieldElement(16, 31))


def test_field_element_div():
    """Testing field elements division."""
    # Dividing elements in different fields should raise TypeError.
    with pytest.raises(TypeError):
        a = FieldElement(12, 23) / FieldElement(3, 33)

    a = FieldElement(3, 31)
    b = FieldElement(24, 31)
    assert (a / b == FieldElement(4, 31))

    a = FieldElement(17, 31)
    assert (a**-3 == FieldElement(29, 31))

    a = FieldElement(4, 31)
    b = FieldElement(11, 31)
    assert (a**-4 * b == FieldElement(13, 31))

