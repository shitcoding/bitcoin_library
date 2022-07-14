from script import Script
from py_bitcoin.utils import (
    hash256,
    little_endian_to_int,
)


class Tx:
    """Bitcoin transaction object."""
    def __init__(self, version, tx_ins, tx_outs, locktime, testnet=False):
        self.version = version
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs
        self.locktime = locktime
        self.testnet = testnet

    def __repr__(self):
        """Return string representation of Bitcoin transaction."""
        tx_ins = ''
        for tx_in in self.tx_ins:
            tx_ins += tx_in.__repr__() + '\n'
        tx_outs = ''
        for tx_out in self.tx_outs:
            tx_outs += tx_out.__repr__() + '\n'
        return f'tx: {self.id()}\n' + \
            f'version: {self.version}\n' + \
            f'tx_ins:\n{tx_ins}' + \
            f'tx_outs:\n{tx_outs}' + \
            f'locktime: {self.locktime}'

    def hash(self):
        """Return binary hash of the legacy serialization."""
        return hash256(self.serialize())[::-1]

    def id(self):
        """Return human-readable hexadecimal of the transaction hash."""
        return self.hash().hex()


class TxIn:
    """Class representing a Bitcoin transaction input."""
    def __init__(
            self, prev_tx, prev_index, script_sig=None, sequence=0xffffffff
    ):
        self.prev_tx = prev_tx
        self.prev_index = prev_index
        # we default to empty ScriptSig
        if script_sig is None:
            self.script_sig = Script()
        else:
            self.script_sig = script_sig
        self.sequence = sequence

    def __repr__(self):
        """Return string representation of transaction input."""
        return '{}:{}'.format(
            self.prev_tx.hex(),
            self.prev_index,
        )

    @classmethod
    def parse(cls, stream):
        """
        Parses transaction input from a byte stream.
        Returns TxIn object.
        """
        # parsing previous transaction ID
        prev_tx = stream.read(32)[::-1]
        # parsing previous transaction index
        prev_index = little_endian_to_int(stream.read(4))
        # parsing ScriptSig from the stream
        script_sig = Script.parse(stream)
        # parsing sequence of the input
        sequence = little_endian_to_int(stream.read(4))
        return cls(prev_tx, prev_index, script_sig, sequence)
