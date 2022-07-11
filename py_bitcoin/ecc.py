import hashlib
import hmac


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

        if self.x is None:  # self is the point at infinity, return other
            return other
        if other.x is None:  # other is the point at infinity, return self
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

    def __rmul__(self, coefficient):
        """
        Scalar multiplication of the point using binary expansion.
        """
        coef = coefficient
        # current - point that's at the current bit
        current = self
        # we start the result at 0, or the point at infinity
        result = self.__class__(None, None, self.a, self.b)
        while coef:
            # if the rightmost bit is a 1, add the value of current bit
            if coef & 1:
                result += current
            # double the point until we're past how big coef can be
            current += current
            # bit-shift the coef to the right
            coef >>= 1
        return result


# secp256k1 curve parameters.
A = 0
B = 7
P = 2**256 - 2**32 - 977
GX = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
GY = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141


class S256Field(FieldElement):
    """Field specific to secp256k1 elliptic curve."""
    def __init__(self, num, prime=None):
        super().__init__(num=num, prime=P)

    def __repr__(self):
        return '{:x}'.format(self.num).zfill(64)


class S256Point(Point):
    """A point on secp256k1 elliptic curve."""
    def __init__(self, x, y, a=None, b=None):
        a, b = S256Field(A), S256Field(B)
        if type(x) == int:
            super().__init__(x=S256Field(x), y=S256Field(y), a=a, b=b)
        else:
            # When initializing with the point at infinity
            # pass x and y directly instead of using S256Field class.
            super().__init__(x=x, y=y, a=a, b=b)

    def __repr__(self):
        if self.x is None:
            return 'S256Point(infinity)'
        else:
            return 'S256Point({}, {})'.format(self.x, self.y)

    def __rmul__(self, coefficient):
        # We can mod by n because nG = 0
        coef = coefficient % N
        return super().__rmul__(coef)

    def verify(self, z, sig):
        """
        Verify secp256k1 signature.

        args:
            z: signature hash
            sig: signature

        returns:
            True: signature is valid
            False: signature is invalid
        """
        s_inv = pow(sig.s, N - 2, N)
        u = z * s_inv % N
        v = sig.r * s_inv % N
        total = u * G + v * self
        return total.x.num == sig.r


# Generator point for secp256k1 curve.
G = S256Point(GX, GY)


class Signature:
    """secp256k1 curve signature."""
    def __init__(self, r, s):
        self.r = r
        self.s = s

    def __repr__(self):
        return 'Signature({:x},{:x})'.format(self.r, self.s)


class PrivateKey:
    """
    Private key used for signing messages and transactions.
    """
    def __init__(self, secret):
        """
        secret: secret used for private key generation
        point: public key
        """
        self.secret = secret
        self.point = secret * G

    def hex(self):
        """Return hex representation of private key."""
        return '{:x}'.format(self.secret).zfill(64)

    def deterministic_k(self, z):
        """
        Generate unique deterministic random number
        according to RFC 6979 specification.
        """
        k = b'\x00' * 32
        v = b'\x01' * 32
        if z > N:
            z -= N
        z_bytes = z.to_bytes(32, 'big')
        secret_bytes = self.secret.to_bytes(32, 'big')
        s256 = hashlib.sha256
        k = hmac.new(k, v + b'\x00' + secret_bytes + z_bytes, s256).digest()
        v = hmac.new(k, v, s256).digest()
        k = hmac.new(k, v + b'\x01' + secret_bytes + z_bytes, s256).digest()
        v = hmac.new(k, v, s256).digest()
        while True:
            v = hmac.new(k, v, s256).digest()
            candidate = int.from_bytes(v, 'big')
            if candidate >= 1 and candidate < N:
                return candidate
            k = hmac.new(k, v + b'\x00', s256).digest()
            v = hmac.new(k, v, s256).digest()

    def sign(self, z):
        """
        Sign a message or transaction with a private key.

        args:
            z: signature hash

        returns:
            signature
        """
        k = self.deterministic_k(z)
        r = (k*G).x.num
        k_inv = pow(k, N - 2, N)
        s = (z + r * self.secret) * k_inv % N
        if s > N / 2:
            s = N - s
        return Signature(r, s)
