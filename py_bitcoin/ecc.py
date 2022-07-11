class FieldElement:
    """Finite field element."""

    def __init__(self, num, prime):
        if num >= prime or num < 0:
            error = f'Num {num} not in field range 0 to {prime - 1}'
            raise ValueError(error)
        self.num = num
        self.prime = prime


    def __repr__(self):
        return f'FieldElement_{self.prime}({self.num})'


    def __eq__(self, other):
        if other is None:
            return False
        return self.num == other.num and self.prime == other.prime


    def __ne__(self, other):
        return not (self == other)


    def __add__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot add two numbers in different Fields')
        num = (self.num + other.num) % self.prime
        return self.__class__(num, self.prime)


    def __sub__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot substract two numbers in different Fields')
        num = (self.num - other.num) % self.prime
        return self.__class__(num, self.prime)


    def __mul__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot multiply two numbers in different Fields')
        num = (self.num * other.num) % self.prime
        return self.__class__(num, self.prime)


    def __pow__(self, exponent):
        n = exponent % (self.prime - 1)
        num = pow(self.num, n, self.prime)
        return self.__class__(num, self.prime)


    def __truediv__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot divide two numbers in different Fields')
        num = (self.num * pow(other.num, self.prime-2, self.prime)) % self.prime
        return self.__class__(num, self.prime)


    def __rmul__(self, coefficient):
        num = (self.num * coefficient) % self.prime
        return self.__class__(num, self.prime)


class Point:
    """Point on the elliptic curve `y**2 = x**3 + a*x +b`."""
    def __init__(self, x, y, a, b):
        self.a = a
        self.b = b
        self.x = x
        self.y = y
        # Point at infinity case
        if self.x is None and self.y is None:
            return
        # Raise exception if point is not on the curve
        if self.y**2 != self.x**3 + a*x + b:
            raise ValueError(f'({x}, {y}) is not on the curve')


    def __repr__(self):
        '''String representation of Point object.'''
        if self.x is None:
            return 'Point(infinity)'
        elif isinstance(self.x, FieldElement):
            return 'Point({},{})_{}_{} FieldElement({})'.format(
                self.x.num, self.y.num, self.a.num, self.b.num, self.x.prime
            )
        return f'Point({self.x}, {self.y})_{self.a}_{self.b}'


    def __eq__(self, other):
        return self.x == other.x and self.y == other.y \
            and self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return not (self == other)


    def __add__(self, other):
        '''Add 2 points on elliptic curve, return resulting Point object.'''
        if self.a != other.a or self.b != other.b:
            raise TypeError(f'Points {self}, {other} are not on the same curve')

        if self.x is None: # self is the point at infinity, return other
            return other
        if other.x is None: # other is the point at infinity, return self
            return self

        # Additive inverse case (same x, different y), vertical line:
        # return point at infinity.
        if self.x == other.x and self.y != other.y:
            return self.__class__(None, None, self.a, self.b)

        # x1 != x2 case
        if self.x != other.x:
            s = (other.y - self.y) / (other.x - self.x)
            x3 = s**2 - self.x - other.x
            y3 = s * (self.x - x3) - self.y
            return self.__class__(x3, y3, self.a, self.b)

        # p1=p2 case (tangential slope)
        if self == other:
            # If p1=p2 and y=0, return point at infinity
            if self.y == 0 * self.x:
                return self.__class__(None, None, self.a, self.b)
            # Otherwise:
            s = (3 * self.x**2 + self.a) / (2 * self.y)
            x = s**2 - 2 * self.x
            y = s * (self.x - x) - self.y
            return self.__class__(x, y, self.a, self.b)



