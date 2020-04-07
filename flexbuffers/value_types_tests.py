import unittest
from .value_types import (ValueType, BitWidth)


class MyTestCase(unittest.TestCase):
    def test_value_types_inline(self):
        self.assertTrue(ValueType.Bool.is_inline())
        self.assertTrue(ValueType.Int.is_inline())
        self.assertTrue(ValueType.UInt.is_inline())
        self.assertTrue(ValueType.Float.is_inline())
        self.assertTrue(ValueType.Null.is_inline())
        self.assertFalse(ValueType.String.is_inline())

    def test_value_types_vector_element(self):
        self.assertTrue(ValueType.Bool.is_typed_vector_element())
        self.assertTrue(ValueType.Int.is_typed_vector_element())
        self.assertTrue(ValueType.UInt.is_typed_vector_element())
        self.assertTrue(ValueType.Float.is_typed_vector_element())
        self.assertTrue(ValueType.Key.is_typed_vector_element())
        self.assertTrue(ValueType.String.is_typed_vector_element())

        self.assertFalse(ValueType.Null.is_typed_vector_element())
        self.assertFalse(ValueType.Blob.is_typed_vector_element())

    def test_value_types_typed_vector(self):
        self.assertTrue(ValueType.VectorInt.is_typed_vector())
        self.assertTrue(ValueType.VectorUInt.is_typed_vector())
        self.assertTrue(ValueType.VectorFloat.is_typed_vector())
        self.assertTrue(ValueType.VectorBool.is_typed_vector())
        self.assertTrue(ValueType.VectorKey.is_typed_vector())
        self.assertTrue(ValueType.VectorString_DEPRECATED.is_typed_vector())

        self.assertFalse(ValueType.Vector.is_typed_vector())
        self.assertFalse(ValueType.Map.is_typed_vector())
        self.assertFalse(ValueType.Bool.is_typed_vector())
        self.assertFalse(ValueType.VectorInt2.is_typed_vector())

    def test_value_types_fixed_typed_vector(self):
        self.assertTrue(ValueType.VectorInt2.is_fixed_typed_vector())
        self.assertTrue(ValueType.VectorUInt2.is_fixed_typed_vector())
        self.assertTrue(ValueType.VectorFloat2.is_fixed_typed_vector())
        self.assertTrue(ValueType.VectorInt3.is_fixed_typed_vector())
        self.assertTrue(ValueType.VectorUInt3.is_fixed_typed_vector())
        self.assertTrue(ValueType.VectorFloat3.is_fixed_typed_vector())
        self.assertTrue(ValueType.VectorInt4.is_fixed_typed_vector())
        self.assertTrue(ValueType.VectorUInt4.is_fixed_typed_vector())
        self.assertTrue(ValueType.VectorFloat4.is_fixed_typed_vector())

        self.assertFalse(ValueType.VectorInt.is_fixed_typed_vector())

    def test_value_to_typed_vector(self):
        self.assertEqual(ValueType.Int.to_typed_vector(0), ValueType.VectorInt)
        self.assertEqual(ValueType.UInt.to_typed_vector(0), ValueType.VectorUInt)
        self.assertEqual(ValueType.Bool.to_typed_vector(0), ValueType.VectorBool)
        self.assertEqual(ValueType.Float.to_typed_vector(0), ValueType.VectorFloat)
        self.assertEqual(ValueType.Key.to_typed_vector(0), ValueType.VectorKey)
        self.assertEqual(ValueType.String.to_typed_vector(0), ValueType.VectorString_DEPRECATED)

        self.assertEqual(ValueType.Int.to_typed_vector(2), ValueType.VectorInt2)
        self.assertEqual(ValueType.UInt.to_typed_vector(2), ValueType.VectorUInt2)
        self.assertEqual(ValueType.Float.to_typed_vector(2), ValueType.VectorFloat2)

        self.assertEqual(ValueType.Int.to_typed_vector(3), ValueType.VectorInt3)
        self.assertEqual(ValueType.UInt.to_typed_vector(3), ValueType.VectorUInt3)
        self.assertEqual(ValueType.Float.to_typed_vector(3), ValueType.VectorFloat3)

        self.assertEqual(ValueType.Int.to_typed_vector(4), ValueType.VectorInt4)
        self.assertEqual(ValueType.UInt.to_typed_vector(4), ValueType.VectorUInt4)
        self.assertEqual(ValueType.Float.to_typed_vector(4), ValueType.VectorFloat4)

    def test_value_typed_vector_element_type(self):
        self.assertEqual(ValueType.VectorInt.typed_vector_element_type(), ValueType.Int)
        self.assertEqual(ValueType.VectorUInt.typed_vector_element_type(), ValueType.UInt)
        self.assertEqual(ValueType.VectorFloat.typed_vector_element_type(), ValueType.Float)
        self.assertEqual(ValueType.VectorString_DEPRECATED.typed_vector_element_type(), ValueType.String)
        self.assertEqual(ValueType.VectorKey.typed_vector_element_type(), ValueType.Key)
        self.assertEqual(ValueType.VectorBool.typed_vector_element_type(), ValueType.Bool)

    def test_value_fixed_typed_vector_element_type(self):
        self.assertEqual(ValueType.VectorInt2.fixed_typed_vector_element_type(), ValueType.Int)
        self.assertEqual(ValueType.VectorUInt2.fixed_typed_vector_element_type(), ValueType.UInt)
        self.assertEqual(ValueType.VectorFloat2.fixed_typed_vector_element_type(), ValueType.Float)

        self.assertEqual(ValueType.VectorInt3.fixed_typed_vector_element_type(), ValueType.Int)
        self.assertEqual(ValueType.VectorUInt3.fixed_typed_vector_element_type(), ValueType.UInt)
        self.assertEqual(ValueType.VectorFloat3.fixed_typed_vector_element_type(), ValueType.Float)

        self.assertEqual(ValueType.VectorInt4.fixed_typed_vector_element_type(), ValueType.Int)
        self.assertEqual(ValueType.VectorUInt4.fixed_typed_vector_element_type(), ValueType.UInt)
        self.assertEqual(ValueType.VectorFloat4.fixed_typed_vector_element_type(), ValueType.Float)

    def test_value_fixed_typed_vector_element_size(self):
        self.assertEqual(ValueType.VectorInt2.fixed_typed_vector_element_size(), 2)
        self.assertEqual(ValueType.VectorUInt2.fixed_typed_vector_element_size(), 2)
        self.assertEqual(ValueType.VectorFloat2.fixed_typed_vector_element_size(), 2)

        self.assertEqual(ValueType.VectorInt3.fixed_typed_vector_element_size(), 3)
        self.assertEqual(ValueType.VectorUInt3.fixed_typed_vector_element_size(), 3)
        self.assertEqual(ValueType.VectorFloat3.fixed_typed_vector_element_size(), 3)

        self.assertEqual(ValueType.VectorInt4.fixed_typed_vector_element_size(), 4)
        self.assertEqual(ValueType.VectorUInt4.fixed_typed_vector_element_size(), 4)
        self.assertEqual(ValueType.VectorFloat4.fixed_typed_vector_element_size(), 4)

    def test_value_packed_type(self):
        self.assertEqual(ValueType.Null.packed_type(BitWidth.Width8), 0)
        self.assertEqual(ValueType.Null.packed_type(BitWidth.Width16), 1)
        self.assertEqual(ValueType.Null.packed_type(BitWidth.Width32), 2)
        self.assertEqual(ValueType.Null.packed_type(BitWidth.Width64), 3)
        self.assertEqual(ValueType.Int.packed_type(BitWidth.Width8), 4)
        self.assertEqual(ValueType.Int.packed_type(BitWidth.Width16), 5)
        self.assertEqual(ValueType.Int.packed_type(BitWidth.Width32), 6)
        self.assertEqual(ValueType.Int.packed_type(BitWidth.Width64), 7)

    def test_bit_width(self):
        self.assertEqual(BitWidth.width(0), BitWidth.Width8)
        self.assertEqual(BitWidth.width(-20), BitWidth.Width8)
        self.assertEqual(BitWidth.width(127), BitWidth.Width8)
        self.assertEqual(BitWidth.width(128), BitWidth.Width16)
        self.assertEqual(BitWidth.width(128123), BitWidth.Width32)
        self.assertEqual(BitWidth.width(12812324534), BitWidth.Width64)
        self.assertEqual(BitWidth.width(-127), BitWidth.Width8)
        self.assertEqual(BitWidth.width(-128), BitWidth.Width16)
        self.assertEqual(BitWidth.width(-12812324534), BitWidth.Width64)
        self.assertEqual(BitWidth.width(-0.1), BitWidth.Width64)
        self.assertEqual(BitWidth.width(0.25), BitWidth.Width64)

    def test_padding_size(self):
        self.assertEqual(BitWidth.padding_size(10, 8), 6)
        self.assertEqual(BitWidth.padding_size(10, 4), 2)
        self.assertEqual(BitWidth.padding_size(15, 4), 1)
        self.assertEqual(BitWidth.padding_size(15, 2), 1)
        self.assertEqual(BitWidth.padding_size(15, 1), 0)
        self.assertEqual(BitWidth.padding_size(16, 8), 0)
        self.assertEqual(BitWidth.padding_size(17, 8), 7)


if __name__ == '__main__':
    unittest.main()
