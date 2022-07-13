from io import BytesIO
import hashlib
import hmac

from py_bitcoin.utils import encode_base58_checksum, hash160


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

    def sqrt(self):
        return self**((P + 1) // 4)


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

    def sec(self, compressed=True):
        """Serialize S256Point in binary version of SEC format."""
        # Compressed SEC format
        if compressed:
            if self.y.num % 2 == 0:
                return b'\x02' + self.x.num.to_bytes(32, 'big')
            else:
                return b'\x03' + self.x.num.to_bytes(32, 'big')
        # Uncompressed SEC format
        return b'\x04' + self.x.num.to_bytes(32, 'big') \
            + self.y.num.to_bytes(32, 'big')

    @classmethod
    def parse(self, sec_bin):
        """Returns a S256Point object parsed from SEC binary (not hex)."""
        if sec_bin[0] == 4:
            x = int.from_bytes(sec_bin[1:33], 'big')
            y = int.from_bytes(sec_bin[33:65], 'big')
            return S256Point(x=x, y=y)
        is_even = sec_bin[0] == 2
        x = S256Field(int.from_bytes(sec_bin[1:], 'big'))
        # right side of the equation y^2 = x^3 + 7
        alpha = x**3 + S256Field(B)
        # solving the left side of the equation
        beta = alpha.sqrt()
        if beta.num % 2 == 0:
            even_beta = beta
            odd_beta = S256Field(P - beta.num)
        else:
            even_beta = S256Field(P - beta.num)
            odd_beta = beta
        if is_even:
            return S256Point(x, even_beta)
        else:
            return S256Point(x, odd_beta)

    def hash160(self, compressed=True):
        """
        Return the result of sha256 followed by ripemd160 on
        binary SEC format serialization of given S256Point.
        """
        return hash160(self.sec(compressed))

    def address(self, compressed=True, testnet=False):
        """Return the bitcoin address string for a given S256Point."""
        h160 = self.hash160(compressed)
        if testnet:
            prefix = b'\x6f'
        else:
            prefix = b'\x00'
        return encode_base58_checksum(prefix + h160)



# Generator point for secp256k1 curve.
G = S256Point(GX, GY)


class Signature:
    """secp256k1 curve signature."""
    def __init__(self, r, s):
        self.r = r
        self.s = s

    def __repr__(self):
        return 'Signature({:x},{:x})'.format(self.r, self.s)

    def der(self):
        """Serialize Signature object in binary DER format."""
        rbin = self.r.to_bytes(32, byteorder='big')
        # remove all null bytes at the beginning
        rbin = rbin.lstrip(b'\x00')
        # if rbin has a high bit, add a \x00
        if rbin[0] & 0x80:
            rbin = b'\x00' + rbin
        result = bytes([2, len(rbin)]) + rbin
        sbin = self.s.to_bytes(32, byteorder='big')
        # remove all null bytes at the beginning
        sbin = sbin.lstrip(b'\x00')
        # if sbin has a high bit, add a \x00
        if sbin[0] & 0x80:
            sbin = b'\x00' + sbin
        result += bytes([2, len(sbin)]) + sbin
        return bytes([0x30, len(result)]) + result

    @classmethod
    def parse(cls, signature_bin):
        """
        Parse serialized signature from binary DER format
        to Signature object.

        args:
            signature_bin: signature in binary DER format

        returns:
            Signature(r, s)
        """
        s = BytesIO(signature_bin)
        compound = s.read(1)[0]
        if compound != 0x30:
            raise SyntaxError("Bad Signature")
        length = s.read(1)[0]
        if length + 2 != len(signature_bin):
            raise SyntaxError("Bad Signature Length")
        marker = s.read(1)[0]
        if marker != 0x02:
            raise SyntaxError("Bad Signature")
        rlength = s.read(1)[0]
        r = int.from_bytes(s.read(rlength), 'big')
        marker = s.read(1)[0]
        if marker != 0x02:
            raise SyntaxError("Bad Signature")
        slength = s.read(1)[0]
        s = int.from_bytes(s.read(slength), 'big')
        if len(signature_bin) != 6 + rlength + slength:
            raise SyntaxError("Signature too long")
        return cls(r, s)



class PrivateKey:
    """
    Private key used for signing messages and transactions.
    """
    def __init__(self, secret):
        """
        Initialize PrivateKey object.

        secret:
            secret used for private key generation
        point:
            public key
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

    def wif(self, compressed=True, testnet=False):
        """Return PrivateKey serialization in WIF format."""
        secret_bytes = self.secret.to_bytes(32, 'big')
        if testnet:
            prefix = b'\xef'
        else:
            prefix = b'\x80'
        if compressed:
            suffix = b'\x01'
        else:
            suffix = b''
        return encode_base58_checksum(prefix + secret_bytes + suffix)
