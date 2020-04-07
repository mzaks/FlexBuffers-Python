import enum


class BitWidth(enum.IntEnum):
    Width8 = 0
    Width16 = 1
    Width32 = 2
    Width64 = 3

    @staticmethod
    def width(value):
        if isinstance(value, int):
            v = abs(value)
            if v >> 7 == 0:
                return BitWidth.Width8
            if v >> 15 == 0:
                return BitWidth.Width16
            if v >> 31 == 0:
                return BitWidth.Width32
            return BitWidth.Width64
        return BitWidth.Width64

    @staticmethod
    def padding_size(buf_size, scalar_size):
        return (~buf_size + 1) & (scalar_size - 1)


class ValueType(enum.IntEnum):
    Null = 0
    Int = 1
    UInt = 2
    Float = 3
    Key = 4
    String = 5
    IndirectInt = 6
    IndirectUInt = 7
    IndirectFloat = 8
    Map = 9
    Vector = 10
    VectorInt = 11
    VectorUInt = 12
    VectorFloat = 13
    VectorKey = 14
    VectorString_DEPRECATED = 15
    VectorInt2 = 16
    VectorUInt2 = 17
    VectorFloat2 = 18
    VectorInt3 = 19
    VectorUInt3 = 20
    VectorFloat3 = 21
    VectorInt4 = 22
    VectorUInt4 = 23
    VectorFloat4 = 24
    Blob = 25
    Bool = 26
    VectorBool = 36

    def is_inline(self):
        return self == ValueType.Bool or self <= ValueType.Float

    def is_number(self):
        return ValueType.Int <= self <= ValueType.Float

    def is_typed_vector_element(self):
        return self == ValueType.Bool or (ValueType.Int <= self <= ValueType.String)

    def is_typed_vector(self):
        return self == ValueType.VectorBool or (ValueType.VectorInt <= self <= ValueType.VectorString_DEPRECATED)

    def is_fixed_typed_vector(self):
        return ValueType.VectorInt2 <= self <= ValueType.VectorFloat4

    def is_a_vector(self):
        return self.is_typed_vector() or self.is_fixed_typed_vector() or self == ValueType.Vector

    def to_typed_vector(self, length):
        if length == 0:
            return ValueType(self - ValueType.Int + ValueType.VectorInt)
        if length == 2:
            return ValueType(self - ValueType.Int + ValueType.VectorInt2)
        if length == 3:
            return ValueType(self - ValueType.Int + ValueType.VectorInt3)
        if length == 4:
            return ValueType(self - ValueType.Int + ValueType.VectorInt4)
        raise Exception("Unexpected length" + length)

    def typed_vector_element_type(self):
        return self - ValueType.VectorInt + ValueType.Int

    def fixed_typed_vector_element_type(self):
        return ((self - ValueType.VectorInt2) % 3) + ValueType.Int

    def fixed_typed_vector_element_size(self):
        return ((self - ValueType.VectorInt2) // 3) + 2

    def packed_type(self, bit_width):
        return bit_width | (self << 2)
