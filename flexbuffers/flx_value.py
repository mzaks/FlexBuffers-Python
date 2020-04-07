import struct
import base64
import json
from .value_types import ValueType


class FlxValue:
    def __init__(self, buffer, offset, parent_width, packed_type):
        self._buffer = buffer
        self._offset = offset
        self._parent_width = parent_width
        self._byte_width = 1 << (packed_type & 3)
        self._value_type = ValueType(packed_type >> 2)
        self._len = None

    @staticmethod
    def from_bytes(buffer):
        if len(buffer) < 3:
            raise Exception("Buffer needs to be bigger than 2 bytes")
        byte_width = buffer[-1]
        packed_type = buffer[-2]
        offset = len(buffer) - byte_width - 2
        return FlxValue(buffer, offset, byte_width, packed_type)

    def is_null(self):
        return self._value_type == ValueType.Null

    def value(self):
        if self._value_type == ValueType.Int:
            return self._read_int(self._offset, self._parent_width)
        if self._value_type == ValueType.IndirectInt:
            indirect_offset = self._compute_indirect()
            return self._read_int(indirect_offset, self._byte_width)
        if self._value_type == ValueType.UInt:
            return self._read_uint(self._offset, self._parent_width)
        if self._value_type == ValueType.IndirectUInt:
            indirect_offset = self._compute_indirect()
            return self._read_uint(indirect_offset, self._byte_width)
        if self._value_type == ValueType.Float:
            return self._read_float(self._offset, self._parent_width)
        if self._value_type == ValueType.IndirectFloat:
            indirect_offset = self._compute_indirect()
            return self._read_float(indirect_offset, self._byte_width)
        if self._value_type == ValueType.Bool:
            return self._read_int(self._offset, self._parent_width) != 0
        if self._value_type == ValueType.String:
            size = len(self)
            indirect_offset = self._compute_indirect()
            return self._buffer[indirect_offset:indirect_offset + size].decode("utf-8")
        if self._value_type == ValueType.Key:
            indirect_offset = self._compute_indirect()
            size = len(self)
            return self._buffer[indirect_offset:indirect_offset + size].decode("utf-8")
        if self._value_type == ValueType.Blob:
            indirect_offset = self._compute_indirect()
            size = self._read_int(indirect_offset - self._byte_width, self._byte_width)
            return self._buffer[indirect_offset:indirect_offset + size]

        return None

    def str(self):
        if self._value_type == ValueType.String:
            indirect_offset = self._compute_indirect()
            size = self._read_int(indirect_offset - self._byte_width, self._byte_width)
            size_width = self._byte_width
            while self._buffer[indirect_offset + size] != 0:
                size_width = size_width << 1
                size = self._read_int(indirect_offset - size_width, size_width)
            indirect_offset = self._compute_indirect()
            return self._buffer[indirect_offset:indirect_offset + size].decode("utf-8")
        return None

    def num(self):
        if self._value_type == ValueType.Int:
            return self._read_int(self._offset, self._parent_width)
        if self._value_type == ValueType.IndirectInt:
            indirect_offset = self._compute_indirect()
            return self._read_int(indirect_offset, self._byte_width)
        if self._value_type == ValueType.UInt:
            return self._read_uint(self._offset, self._parent_width)
        if self._value_type == ValueType.IndirectUInt:
            indirect_offset = self._compute_indirect()
            return self._read_uint(indirect_offset, self._byte_width)
        if self._value_type == ValueType.Float:
            return self._read_float(self._offset, self._parent_width)
        if self._value_type == ValueType.IndirectFloat:
            indirect_offset = self._compute_indirect()
            return self._read_float(indirect_offset, self._byte_width)

    def key(self):
        if self._value_type == ValueType.Key:
            indirect_offset = self._compute_indirect()
            size = 0
            while self._buffer[indirect_offset + size] != 0:
                size = size + 1
            return self._buffer[indirect_offset:indirect_offset + size].decode("utf-8")

    def __len__(self):
        if self._len is not None:
            return self._len
        # is_fixed_typed_vector need to be before the more generic is_a_vector check
        if self._value_type.is_fixed_typed_vector():
            self._len = self._value_type.fixed_typed_vector_element_size()
            return self._len
        if self._value_type == ValueType.Blob or self._value_type.is_a_vector() or self._value_type == ValueType.Map:
            indirect_offset = self._compute_indirect()
            self._len = self._read_int(indirect_offset - self._byte_width, self._byte_width)
            return self._len
        if self._value_type == ValueType.Null:
            self._len = 0
            return 0
        if self._value_type == ValueType.String:
            indirect_offset = self._compute_indirect()
            size = self._read_int(indirect_offset - self._byte_width, self._byte_width)
            size_width = self._byte_width
            while self._buffer[indirect_offset + size] != 0:
                size_width = size_width << 1
                size = self._read_int(indirect_offset - size_width, size_width)
            self._len = size
            return size
        if self._value_type == ValueType.Key:
            indirect_offset = self._compute_indirect()
            size = 0
            while self._buffer[indirect_offset + size] != 0:
                size = size + 1
            self._len = size
            return size
        self._len = 1
        return 1

    def __getitem__(self, item):
        if isinstance(item, int):
            length = len(self)
            if self._value_type.is_a_vector() and length > item:
                indirect_offset = self._compute_indirect()
                elem_offset = indirect_offset + (item * self._byte_width)
                if self._value_type.is_typed_vector():
                    flx = FlxValue(self._buffer, elem_offset, self._byte_width, 0)
                    flx._byte_width = 1
                    flx._value_type = ValueType(self._value_type.typed_vector_element_type())
                    return flx
                if self._value_type.is_fixed_typed_vector():
                    flx = FlxValue(self._buffer, elem_offset, self._byte_width, 0)
                    flx._byte_width = 1
                    flx._value_type = ValueType(self._value_type.fixed_typed_vector_element_type())
                    return flx
                packed_type = self._buffer[indirect_offset + length * self._byte_width + item]
                return FlxValue(self._buffer, elem_offset, self._byte_width, packed_type)
        if isinstance(item, str):
            index = self.key_index(item)
            if index is None:
                return None
            return self._get_value_for_index(index)

    def __getattr__(self, item):
        return self[item]

    def __iter__(self):
        if self._value_type.is_a_vector():
            for i in range(len(self)):
                yield self[i]
            return
        if self._value_type == ValueType.Map:
            for i in range(len(self)):
                yield self._get_key_for_index(i), self._get_value_for_index(i)
            return
        yield self.value()

    def json(self):
        result = ''
        if self._value_type == ValueType.Map:
            last_element_index = len(self) - 1
            result += '{'
            for i, v in enumerate(self):
                result += v[0].json() + ":" + v[1].json()
                if i < last_element_index:
                    result += ","
            result += '}'
        elif self._value_type.is_a_vector():
            last_element_index = len(self) - 1
            result += '['
            for i, v in enumerate(self):
                result += v.json()
                if i < last_element_index:
                    result += ","
            result += ']'
        elif self._value_type == ValueType.Key or self._value_type == ValueType.String:
            result += json.dumps(self.value(), ensure_ascii=False)
        elif self._value_type == ValueType.Bool:
            if self.value():
                result += "true"
            else:
                result += "false"
        elif self.is_null():
            result += "null"
        elif self._value_type == ValueType.Blob:
            result += '"' + base64.b64encode(self.value()) + '"'
        else:
            result += str(self.value())
        return result

    def to_object(self):
        if self._value_type == ValueType.Map:
            result = {}
            for k, v in self:
                result[k.value()] = v.to_object()
            return result
        elif self._value_type.is_a_vector():
            result = []
            for v in self:
                result.append(v.to_object())
            return result
        return self.value()

    def key_index(self, key):
        if self._value_type is not ValueType.Map:
            return None
        utf8_key = bytes(key, 'utf-8')
        low = 0
        high = len(self) - 1
        while low <= high:
            mid = (high + low) >> 1
            dif = self._dif_keys(mid, utf8_key)
            if dif == 0:
                return mid
            if dif < 0:
                high = mid - 1
            else:
                low = mid + 1
        return None

    def _dif_keys(self, index, key):
        key2 = self._get_key_for_index(index)
        indirect_offset = key2._compute_indirect()
        key_len = len(key)
        for i in range(key_len):
            dif = key[i] - self._buffer[indirect_offset + i]
            if dif != 0:
                return dif

        if key2._buffer[indirect_offset + key_len] == 0:
            return 0
        return -1

    def _get_key_for_index(self, index):
        if self._value_type != ValueType.Map:
            return None
        offset = self._compute_indirect()
        keys_offset = offset - self._byte_width * 3
        indirect_offset = keys_offset - self._read_int(keys_offset, self._byte_width)
        byte_width = self._read_int(keys_offset + self._byte_width, self._byte_width)
        elem_offset = indirect_offset + index * byte_width
        flx = FlxValue(self._buffer, elem_offset, byte_width, 0)
        flx._byte_width = byte_width
        flx._value_type = ValueType.Key
        return flx

    def _get_value_for_index(self, index):
        if self._value_type != ValueType.Map:
            return None
        indirect_offset = self._compute_indirect()
        elem_offset = indirect_offset + (index * self._byte_width)
        packed_type = self._buffer[indirect_offset + len(self) * self._byte_width + index]
        return FlxValue(self._buffer, elem_offset, self._byte_width, packed_type)

    def _read_int(self, offset, width):
        self._validate_offset(offset, width)
        if width == 1:
            return struct.unpack_from("<b", self._buffer, offset)[0]
        if width == 2:
            return struct.unpack_from("<h", self._buffer, offset)[0]
        if width == 4:
            return struct.unpack_from("<i", self._buffer, offset)[0]
        return struct.unpack_from("<q", self._buffer, offset)[0]

    def _read_uint(self, offset, width):
        self._validate_offset(offset, width)
        if width == 1:
            return struct.unpack_from("<B", self._buffer, offset)[0]
        if width == 2:
            return struct.unpack_from("<H", self._buffer, offset)[0]
        if width == 4:
            return struct.unpack_from("<I", self._buffer, offset)[0]
        return struct.unpack_from("<Q", self._buffer, offset)[0]

    def _read_float(self, offset, width):
        self._validate_offset(offset, width)
        if width != 4 and width != 8:
            raise Exception("Bad width " + width)
        if width == 4:
            return struct.unpack_from("<f", self._buffer, offset)[0]
        return struct.unpack_from("<d", self._buffer, offset)[0]

    def _compute_indirect(self):
        step = self._read_int(self._offset, self._parent_width)
        return self._offset - step

    def _validate_offset(self, offset, width):
        if self._offset < 0 or len(self._buffer) <= (offset + width) or (offset & (width - 1)) != 0:
            raise Exception("Bad offset")
