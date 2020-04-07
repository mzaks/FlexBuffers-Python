import unittest

from flexbuffers.flx_builder import FlxBuilder


class MyTestCase(unittest.TestCase):
    def test_build_single_value(self):
        self._build_single(None, bytes([0, 0, 1]))
        self._build_single(True, bytes([1, 104, 1]))
        self._build_single(False, bytes([0, 104, 1]))
        self._build_single(1, bytes([1, 4, 1]))
        self._build_single(230, bytes([230, 0, 5, 2]))
        self._build_single(1025, bytes([1, 4, 5, 2]))
        self._build_single(-1025, bytes([255, 251, 5, 2]))
        self._build_single(0.1, bytes([154, 153, 153, 153, 153, 153, 185, 63, 15, 8]))

    def test_build_single_string(self):
        self._build_single_string("Maxim", bytes([5, 77, 97, 120, 105, 109, 0, 6, 20, 1]))
        self._build_single_string("hello 😱",
                                  bytes([10, 104, 101, 108, 108, 111, 32, 240, 159, 152, 177, 0, 11, 20, 1]))

    def test_vector(self):
        self.assertEqual(FlxBuilder.fromValue([1, 2]), bytes([1, 2, 2, 64, 1]))
        self.assertEqual(FlxBuilder.fromValue([-1, 256]), bytes([255, 255, 0, 1, 4, 65, 1]))
        self.assertEqual(FlxBuilder.fromValue([-45, 256000]), bytes([211, 255, 255, 255, 0, 232, 3, 0, 8, 66, 1]))
        # self.assertEqual(FlxBuilder.fromValue([-45, 9223372036854775807]), bytes([211, 255, 255, 255, 0, 232, 3, 0, 8, 66, 1]))
        self.assertEqual(FlxBuilder.fromValue([1.1, -256.0]),
                         bytes([154, 153, 153, 153, 153, 153, 241, 63, 0, 0, 0, 0, 0, 0, 112, 192, 16, 75, 1]))
        self.assertEqual(FlxBuilder.fromValue([1, 2, 4]), bytes([1, 2, 4, 3, 76, 1]))
        self.assertEqual(FlxBuilder.fromValue([-1, 256, 4]), bytes([255, 255, 0, 1, 4, 0, 6, 77, 1]))
        self.assertEqual(FlxBuilder.fromValue([-1, 256, 4]), bytes([255, 255, 0, 1, 4, 0, 6, 77, 1]))
        # self.assertEqual(FlxBuilder.fromValue([-45, 256000, 4]), bytes([
        #     211, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 127, 4, 0, 0, 0, 0, 0, 0, 0, 24, 79, 1
        # ]))

        self.assertEqual(FlxBuilder.fromValue([[61], 64]), bytes([1, 61, 2, 2, 64, 44, 4, 4, 40, 1]))
        self.assertEqual(FlxBuilder.fromValue(["foo", "bar", "baz"]),
                         bytes([3, 102, 111, 111, 0, 3, 98, 97, 114, 0, 3, 98, 97, 122, 0, 3, 15, 11, 7, 3, 60, 1]))
        self.assertEqual(FlxBuilder.fromValue(["foo", "bar", "baz", "foo", "bar", "baz"]), bytes(
            [3, 102, 111, 111, 0, 3, 98, 97, 114, 0, 3, 98, 97, 122, 0, 6, 15, 11, 7, 18, 14, 10, 6, 60, 1]))
        self.assertEqual(FlxBuilder.fromValue([True, False, True]), bytes([3, 1, 0, 1, 3, 144, 1]))
        self.assertEqual(FlxBuilder.fromValue(["foo", 1, -5, 1.3, True]),
                         bytes([3, 102, 111, 111, 0, 0, 0, 0,
                                5, 0, 0, 0, 0, 0, 0, 0,
                                15, 0, 0, 0, 0, 0, 0, 0,
                                1, 0, 0, 0, 0, 0, 0, 0,
                                251, 255, 255, 255, 255, 255, 255, 255,
                                205, 204, 204, 204, 204, 204, 244, 63,
                                1, 0, 0, 0, 0, 0, 0, 0,
                                20, 4, 4, 15, 104, 45, 43, 1]))

    def test_map(self):
        self.assertEqual(FlxBuilder.fromValue({"a": 12}), bytes([97, 0, 1, 3, 1, 1, 1, 12, 4, 2, 36, 1]))
        self.assertEqual(FlxBuilder.fromValue({"a": 12, "": 45}),
                         bytes([0, 97, 0, 2, 4, 4, 2, 1, 2, 45, 12, 4, 4, 4, 36, 1]))

    def test_blob(self):
        self.assertEqual(FlxBuilder.fromValue(bytes([1, 2, 3])), bytes([3, 1, 2, 3, 3, 100, 1]))

    def test_vector_of_dicts_with_same_keys(self):
        self.assertEqual(FlxBuilder.fromValue([{"something": 12}, {"something": 45}]),
                         bytes([115, 111, 109, 101, 116, 104, 105, 110, 103, 0,
                                1, 11, 1, 1, 1, 12, 4, 6, 1, 1, 45, 4, 2, 8, 4, 36, 36, 4, 40, 1]))

    def _build_single(self, value, data):
        fbb = FlxBuilder(1)
        fbb._add(value)
        data1 = fbb._finish()
        self.assertEqual(data1, data)

    def _build_single_string(self, value, data):
        fbb = FlxBuilder(1)
        fbb._addString(value)
        data1 = fbb._finish()
        self.assertEqual(data1, data)


if __name__ == '__main__':
    unittest.main()
