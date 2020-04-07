import collections
import struct
from .value_types import (ValueType, BitWidth)


class _StackValue:
    def __init__(self, value):
        self._value = value
        if value is None:
            self._type = ValueType.Null
            self._width = BitWidth.Width8
        elif isinstance(value, bool):
            self._type = ValueType.Bool
            self._width = BitWidth.Width8
        elif isinstance(value, int):
            self._type = ValueType.Int
            self._width = BitWidth.width(value)
        elif isinstance(value, float):
            self._type = ValueType.Float
            self._width = BitWidth.width(value)
        else:
            raise Exception("Unexpected value type")

    @staticmethod
    def valueWithType(value, value_type: ValueType, width: BitWidth):
        result = _StackValue(value)
        result._width = width
        result._type = value_type
        return result

    def stored_width(self, bit_width=BitWidth.Width8):
        if self._type.is_inline():
            return BitWidth(max(self._width, bit_width))
        return self._width

    def stored_packed_type(self, bit_width=BitWidth.Width8):
        return ValueType.packed_type(self._type, self.stored_width(bit_width))

    def element_width(self, size, index):
        if self._type.is_inline():
            return self._width
        for i in range(4):
            width = 1 << i
            offset_loc = size + BitWidth.padding_size(size, width) + index * width
            offset = offset_loc - self._value
            bit_width = BitWidth.width(offset)
            if 1 << bit_width == width:
                return bit_width
        raise Exception("Element is of unknown width")

    def value(self):
        return self._value

    def type(self):
        return self._type

    def width(self):
        return self._width

    def is_offset(self):
        return not self._type.is_inline()

    def is_f32(self):
        return self._type == ValueType.Float and self._width == BitWidth.Width32


class _KeysHash:
    def __init__(self, keys):
        self.keys = keys

    def __eq__(self, o: object) -> bool:
        return (
            self.__class__ == o.__class__ and
            self.keys == o.keys
        )

    def __hash__(self) -> int:
        result = 17
        for key in self.keys:
            result = result * 23 + key
        return result


class FlxBuilder:
    def __init__(self, size=2048):
        self._buffer = bytearray(size)
        self._stack = []
        self._offset = 0
        self._finished = False
        self._string_cache = {}
        self._key_cache = {}
        self._key_vector_cache = {}

    @staticmethod
    def fromValue(value):
        fbb = FlxBuilder()
        fbb._addDynamic(value)
        return fbb._finish()

    def _addDynamic(self, value):
        if isinstance(value, bytes):
            self._addBlob(value)
            return ValueType.Blob
        if isinstance(value, collections.Mapping):
            start = self._startVector()
            keys = sorted(value.keys())
            for k in keys:
                self._addKey(k)
                self._addDynamic(value[k])
            self._endMap(start)
            return ValueType.Map
        if getattr(value, '__dict__', None) is not None:
            return self._addDynamic(vars(value))
        if isinstance(value, str):
            return self._addString(value)
        if isinstance(value, collections.Iterable):
            start = self._startVector()
            for v in value:
                self._addDynamic(v)
            self._endVector(start)
            return ValueType.Vector
        else:
            self._add(value)

    def _add(self, value):
        stack_value = _StackValue(value)
        self._stack.append(stack_value)
        return stack_value.type()

    def _addString(self, value):
        utf8 = bytes(value, 'utf-8')
        length = len(utf8)
        bit_width = BitWidth.width(length)
        if value in self._string_cache:
            self._stack.append(_StackValue.valueWithType(self._string_cache[value], ValueType.String, bit_width))
            return
        byte_width = self._align(bit_width)
        self._writeValue(length, byte_width)
        string_offset = self._offset
        new_offset = self._newOffset(length + 1)
        self._buffer[self._offset:self._offset + length] = utf8
        self._offset = new_offset
        self._stack.append(_StackValue.valueWithType(string_offset, ValueType.String, bit_width))
        self._string_cache[value] = string_offset
        return ValueType.String

    def _addKey(self, value):
        if value in self._key_cache:
            self._stack.append(_StackValue.valueWithType(self._key_cache[value], ValueType.Key, BitWidth.Width8))
            return
        utf8 = bytes(value, 'utf-8')
        length = len(utf8)
        key_offset = self._offset
        new_offset = self._newOffset(length + 1)
        self._buffer[self._offset:self._offset + length] = utf8
        self._offset = new_offset
        self._stack.append(_StackValue.valueWithType(key_offset, ValueType.Key, BitWidth.Width8))
        self._key_cache[value] = key_offset

    def _addBlob(self, value: bytes):
        length = len(value)
        bit_width = BitWidth.width(length)
        byte_width = self._align(bit_width)
        self._writeValue(length, byte_width)
        new_offset = self._newOffset(length)
        blob_offset = self._offset
        self._buffer[self._offset:self._offset + length] = value
        self._offset = new_offset
        self._stack.append(_StackValue.valueWithType(blob_offset, ValueType.Blob, bit_width))

    def _startVector(self):
        return len(self._stack)

    def _endVector(self, start):
        vec_len = len(self._stack) - start
        vec = self._createVector(start, vec_len, 1)
        del self._stack[start:]
        self._stack.append(vec)
        return vec.value()

    def _endMap(self, start):
        vec_len = (len(self._stack) - start) >> 1
        offsets = []
        for i in range(start, len(self._stack), 2):
            offsets.append(self._stack[i].value())
        keys_hash = _KeysHash(offsets)
        keys = self._key_vector_cache[keys_hash] \
            if keys_hash in self._key_vector_cache \
            else self._createVector(start, vec_len, 2)
        self._key_vector_cache[keys_hash] = keys
        vec = self._createVector(start + 1, vec_len, 2, keys)
        del self._stack[start:]
        self._stack.append(vec)

    def _finish(self):
        if not self._finished:
            self._finish_buffer()
        return bytes(self._buffer[:self._offset])

    def _finish_buffer(self):
        if self._finished:
            raise Exception("FlexBuffer is already finished")
        if len(self._stack) != 1:
            raise Exception("Stack needs to be exactly 1")
        value: _StackValue = self._stack[0]
        byte_width = self._align(value.element_width(self._offset, 0))
        self._writeStackValue(value, byte_width)
        self._writeValue(value.stored_packed_type(), 1)
        self._writeValue(byte_width, 1)
        self._finished = True

    def _align(self, width):
        byte_width = 1 << width
        self._offset += BitWidth.padding_size(self._offset, byte_width)
        return byte_width

    def _writeValue(self, value, width):
        new_offset = self._newOffset(width)
        _pack(self._buffer, value, width, self._offset)
        self._offset = new_offset

    def _writeStackValue(self, stack_value: _StackValue, width):
        new_offset = self._newOffset(width)
        if stack_value.is_offset():
            rel_offset = self._offset - stack_value.value()
            if width == 8 or rel_offset < (1 << (width * 8)):
                self._writeValue(rel_offset, width)
            else:
                raise Exception("Unexpected size")
        else:
            _pack(self._buffer, stack_value.value(), width, self._offset)
        self._offset = new_offset

    def _newOffset(self, width):
        new_offset = self._offset + width
        size = len(self._buffer)
        prev_size = size
        while size < new_offset:
            size <<= 1
        if prev_size < size:
            buffer = bytearray(size)
            buffer[0:len(self._buffer)] = self._buffer
            self._buffer = buffer
        return new_offset

    def _createVector(self, start, vec_len, step, keys: _StackValue = None):
        bit_width = BitWidth.width(vec_len)
        prefix_elements = 1
        if keys is not None:
            elem_width = keys.element_width(self._offset, 0)
            if elem_width > bit_width:
                bit_width = elem_width
            prefix_elements += 2
        vector_type = ValueType.Key
        typed = keys is None
        for i in range(start, len(self._stack), step):
            elem_width = self._stack[i].element_width(self._offset, i + prefix_elements)
            if elem_width > bit_width:
                bit_width = elem_width
            if i == start:
                vector_type = self._stack[i].type()
                typed &= vector_type.is_typed_vector_element()
            else:
                if vector_type != self._stack[i].type():
                    typed = False
        byte_width = self._align(bit_width)
        fix = typed and 2 <= vec_len <= 4 and vector_type.is_number()
        if keys is not None:
            self._writeStackValue(keys, byte_width)
            self._writeValue(1 << keys.width(), byte_width)
        if not fix:
            self._writeValue(vec_len, byte_width)
        vec_offset = self._offset
        for i in range(start, len(self._stack), step):
            self._writeStackValue(self._stack[i], byte_width)
        if not typed:
            for i in range(start, len(self._stack), step):
                self._writeValue(self._stack[i].stored_packed_type(), 1)
        if keys is not None:
            return _StackValue.valueWithType(vec_offset, ValueType.Map, bit_width)
        if typed:
            v_type = vector_type.to_typed_vector(vec_len if fix else 0)
            return _StackValue.valueWithType(vec_offset, v_type, bit_width)
        return _StackValue.valueWithType(vec_offset, ValueType.Vector, bit_width)


def _pack(buffer, value, width, offset):
    if value is None:
        return struct.pack_into("<b", buffer, offset, 0)
    if isinstance(value, bool):
        return struct.pack_into("<b", buffer, offset, value)
    if isinstance(value, float):
        return struct.pack_into("<d", buffer, offset, value)
    if isinstance(value, int):
        if width == 1:
            f = "<B" if value >= 2 ^ 7 else "<b"
            return struct.pack_into(f, buffer, offset, value)
        if width == 2:
            f = "<H" if value >= 2 ^ 15 else "<h"
            return struct.pack_into(f, buffer, offset, value)
        if width == 4:
            f = "<I" if value >= 2 ^ 31 else "<i"
            return struct.pack_into(f, buffer, offset, value)
        f = "<Q" if value >= 2 ^ 63 else "<q"
        return struct.pack_into(f, buffer, offset, value)

    raise Exception("Unexpected value type")
