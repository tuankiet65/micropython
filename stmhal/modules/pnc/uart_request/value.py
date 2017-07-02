import ustruct


class Value:
    value = None
    size = None

    def __init__(self, value = None):
        if value is None:
            return

        self.value = value
        valid, err_msg = self.__valid__()
        if not valid:
            raise ValueError(err_msg)

    def __valid__(self):
        raise NotImplementedError

    def _from_byte(self, b):
        raise NotImplementedError

    def __bytes__(self):
        raise NotImplementedError

    def from_bytes(self, b):
        if type(b) is not bytes:
            raise TypeError('b must be bytes')
        if len(b) != self.size:
            raise ValueError('b must be {} byte(s) long'.format(self.size))
        self._from_byte(b)
        return self.value


class BooleanValue(Value):
    size = 1

    def __valid__(self):
        if type(self.value) is not bool:
            return False, "value must be bool"
        return True, ""

    def __bytes__(self):
        if self.value:
            return b'\x01'
        else:
            return b'\x00'

    def _from_byte(self, b):
        # \x01 => \xff is true, \x00 is false
        self.value = (b != b'\x00')


class UInt8Value(Value):
    size = 1

    def __valid__(self):
        if type(self.value) is not int:
            return False, "value must be int"
        if (self.value < 0) or (self.value >= (1 << 8)):
            return False, "value must be between 0 and 255"
        return True, ""

    def __bytes__(self):
        return bytes([self.value])

    def _from_byte(self, b):
        self.value = b[0]


class UInt32Value(Value):
    size = 4

    def __valid__(self):
        if type(self.value) is not int:
            return False, "value must be int"
        if (self.value < 0) or (self.value >= (1 << 32)):
            return False, "value must be between 0 and 4294967295"
        return True, ""

    def __bytes__(self):
        return ustruct.pack("<l", self.value)

    def _from_byte(self, b):
        return ustruct.unpack("<l", b)


class FloatValue(Value):
    size = 4

    def __valid__(self):
        if type(self.value) is not float:
            return False, "value must be int"
        return True, ""

    def __bytes__(self):
        return ustruct.pack("<f", self.value)

    def _from_byte(self, b):
        return ustruct.unpack("<f", b)


class CharValue(Value):
    def __valid__(self):
        if type(self.value) is not str:
            return False, "value must be str"
        if len(self.value) != len(self.value.encode('ascii')):
            return False, "CharValue currently does not support Unicode characters"
        return True, ""

    def __init__(self, value):
        super().__init__(value)
        self.size = len(value)

    def __bytes__(self):
        return self.value.encode('ascii')

    def _from_byte(self, b):
        return


__all__ = [
    Value,
    BooleanValue,
    UInt8Value,
    UInt32Value,
    FloatValue,
    CharValue
]