import unittest
from .flx_value import (FlxValue)


class MyTestCase(unittest.TestCase):
    def test_null_buffer(self):
        buffer = bytes([0, 0, 1])
        flx = FlxValue.from_bytes(buffer)
        self.assertTrue(flx.is_null())
        self.assertEqual(len(flx), 0)

    def test_bool_buffer(self):
        self.assertEqual(FlxValue.from_bytes(bytes([1, 104, 1])).value(), True)
        self.assertEqual(FlxValue.from_bytes(bytes([0, 104, 1])).value(), False)
        self.assertEqual(len(FlxValue.from_bytes(bytes([0, 104, 1]))), 1)

    def test_numbers(self):
        self.assertEqual(FlxValue.from_bytes(bytes([25, 4, 1])).value(), 25)
        self.assertEqual(FlxValue.from_bytes(bytes([231, 4, 1])).value(), -25)
        self.assertEqual(FlxValue.from_bytes(bytes([230, 8, 1])).value(), 230)
        self.assertEqual(FlxValue.from_bytes(bytes([230, 0, 5, 2])).value(), 230)
        self.assertEqual(FlxValue.from_bytes(bytes([1, 4, 5, 2])).value(), 1025)
        self.assertEqual(FlxValue.from_bytes(bytes([255, 251, 5, 2])).value(), -1025)
        self.assertEqual(FlxValue.from_bytes(bytes([1, 4, 9, 2])).value(), 1025)
        self.assertEqual(FlxValue.from_bytes(bytes([255, 255, 255, 127, 6, 4])).value(), 2147483647)
        self.assertEqual(FlxValue.from_bytes(bytes([0, 0, 0, 128, 6, 4])).value(), -2147483648)
        self.assertEqual(FlxValue.from_bytes(bytes([0, 0, 144, 64, 14, 4])).value(), 4.5)
        self.assertAlmostEqual(FlxValue.from_bytes(bytes([205, 204, 204, 61, 14, 4])).value(), .1)
        self.assertEqual(FlxValue.from_bytes(bytes([255, 255, 255, 255, 0, 0, 0, 0, 7, 8])).value(), 4294967295)
        self.assertEqual(FlxValue.from_bytes(
            bytes([255, 255, 255, 255, 255, 255, 255, 127, 7, 8])).value(), 9223372036854775807)
        self.assertEqual(FlxValue.from_bytes(
            bytes([0, 0, 0, 0, 0, 0, 0, 128, 7, 8])).value(), -9223372036854775808)
        self.assertEqual(FlxValue.from_bytes(
            bytes([255, 255, 255, 255, 255, 255, 255, 255, 11, 8])).value(), 18446744073709551615)
        self.assertAlmostEqual(FlxValue.from_bytes(bytes([154, 153, 153, 153, 153, 153, 185, 63, 15, 8])).value(), .1)

    def test_string(self):
        self.assertEqual(FlxValue.from_bytes(bytes([5, 77, 97, 120, 105, 109, 0, 6, 20, 1])).value(), "Maxim")
        self.assertEqual(len(FlxValue.from_bytes(bytes([5, 77, 97, 120, 105, 109, 0, 6, 20, 1]))), 5)
        self.assertEqual(FlxValue.from_bytes(
            bytes([10, 104, 101, 108, 108, 111, 32, 240, 159, 152, 177, 0, 11, 20, 1])).value(), "hello 😱")
        self.assertEqual(len(FlxValue.from_bytes(
            bytes([10, 104, 101, 108, 108, 111, 32, 240, 159, 152, 177, 0, 11, 20, 1]))), 10)

    def test_blob(self):
            self.assertEqual(FlxValue.from_bytes(bytes([3, 1, 2, 3, 3, 100, 1])).value(), bytes([1, 2, 3]))

    def test_number_vector(self):
        self._checkVector(bytes([3, 1, 2, 3, 3, 44, 1]), [1, 2, 3])
        self._checkVector(bytes([3, 255, 2, 3, 3, 44, 1]), [-1, 2, 3])
        self._checkVector(bytes([3, 255, 2, 3, 3, 44, 1]), [-1, 2, 3])
        self._checkVector(bytes([3, 0, 1, 0, 43, 2, 3, 0, 6, 45, 1]), [1, 555, 3])
        self._checkVector(bytes([3, 0, 0, 0, 1, 0, 0, 0, 204, 216, 0, 0, 3, 0, 0, 0, 12, 46, 1]), [1, 55500, 3])
        self._checkVector(bytes(
            [3, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 172, 128, 94, 239, 12, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 24,
             47, 1]), [1, 55555555500, 3])
        self._checkVector(bytes([3, 0, 0, 0, 0, 0, 192, 63, 0, 0, 32, 64, 0, 0, 96, 64, 12, 54, 1]), [1.5, 2.5, 3.5])
        self._checkVector(bytes(
            [3, 0, 0, 0, 0, 0, 0, 0, 154, 153, 153, 153, 153, 153, 241, 63, 154, 153, 153, 153, 153, 153, 1, 64, 102,
             102, 102, 102, 102, 102, 10, 64, 24, 55, 1]), [1.1, 2.2, 3.3])

    def test_bool_vector(self):
        self._checkVector(bytes([3, 1, 0, 1, 3, 144, 1]), [True, False, True])

    def test_string_vector(self):
        self._checkVector(bytes([3, 102, 111, 111, 0, 3, 98, 97, 114, 0, 3, 98, 97, 122, 0, 3, 15, 11, 7, 3, 60, 1]),
                          ["foo", "bar", "baz"])
        self._checkVector(
            bytes([3, 102, 111, 111, 0, 3, 98, 97, 114, 0, 3, 98, 97, 122, 0, 6, 15, 11, 7, 18, 14, 10, 6, 60, 1]),
            ["foo", "bar", "baz", "foo", "bar", "baz"])

    def test_mixed_vector(self):
        self._checkVector(bytes([
            3, 102, 111, 111, 0, 0, 0, 0,
            5, 0, 0, 0, 0, 0, 0, 0,
            15, 0, 0, 0, 0, 0, 0, 0,
            1, 0, 0, 0, 0, 0, 0, 0,
            251, 255, 255, 255, 255, 255, 255, 255,
            205, 204, 204, 204, 204, 204, 244, 63,
            1, 0, 0, 0, 0, 0, 0, 0,
            20, 4, 4, 15, 104, 45, 43, 1
        ]), ["foo", 1, -5, 1.3, True])

        flx = FlxValue.from_bytes(bytes([1, 61, 2, 2, 64, 44, 4, 4, 40, 1]))  # [[61], 64]
        self.assertEqual(len(flx), 2)
        self.assertEqual(len(flx[0]), 1)
        self.assertEqual(len(flx[1]), 1)
        self.assertEqual(flx[0][0].value(), 61)
        self.assertEqual(flx[1].value(), 64)

    def test_fixed_typed_vector(self):
        self._checkVector(bytes([1, 2, 2, 64, 1]), [1, 2])
        self._checkVector(bytes([255, 255, 0, 1, 4, 65, 1]), [-1, 256])
        self._checkVector(bytes([211, 255, 255, 255, 0, 232, 3, 0, 8, 66, 1]), [-45, 256000])
        self._checkVector(
            bytes([211, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 127, 16, 67, 1]),
            [-45, 9223372036854775807])

        self._checkVector(bytes([1, 2, 2, 68, 1]), [1, 2])
        self._checkVector(bytes([1, 0, 0, 1, 4, 69, 1]), [1, 256])
        self._checkVector(bytes([45, 0, 0, 0, 0, 232, 3, 0, 8, 70, 1]), [45, 256000])
        self._checkVector(bytes([45, 0, 0, 0, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 255, 255, 16, 71, 1]),
                          [45, 18446744073709551615])

        self._checkVector(bytes([205, 204, 140, 63, 0, 0, 0, 192, 8, 74, 1]), [1.1, -2])
        self._checkVector(bytes([154, 153, 153, 153, 153, 153, 241, 63, 0, 0, 0, 0, 0, 0, 112, 192, 16, 75, 1]),
                          [1.1, -256])

        self._checkVector(bytes([1, 2, 4, 3, 76, 1]), [1, 2, 4])
        self._checkVector(bytes([255, 255, 0, 1, 4, 0, 6, 77, 1]), [-1, 256, 4])
        self._checkVector(bytes([
            211, 255, 255, 255,
            0, 232, 3, 0,
            4, 0, 0, 0,
            12, 78, 1
        ]), [-45, 256000, 4])
        self._checkVector(bytes([
            211, 255, 255, 255, 255, 255, 255, 255,
            255, 255, 255, 255, 255, 255, 255, 127,
            4, 0, 0, 0, 0, 0, 0, 0,
            24, 79, 1
        ]), [-45, 9223372036854775807, 4])

        self._checkVector(bytes([1, 2, 4, 9, 4, 88, 1]), [1, 2, 4, 9])
        self._checkVector(bytes([255, 255, 0, 1, 4, 0, 9, 0, 8, 89, 1]), [-1, 256, 4, 9])
        self._checkVector(bytes([
            211, 255, 255, 255,
            0, 232, 3, 0,
            4, 0, 0, 0,
            9, 0, 0, 0,
            16, 90, 1
        ]), [-45, 256000, 4, 9])
        self._checkVector(bytes([
            211, 255, 255, 255, 255, 255, 255, 255,
            255, 255, 255, 255, 255, 255, 255, 127,
            4, 0, 0, 0, 0, 0, 0, 0,
            9, 0, 0, 0, 0, 0, 0, 0,
            32, 91, 1
        ]), [-45, 9223372036854775807, 4, 9])

        self._checkVector(bytes([1, 2, 4, 3, 80, 1]), [1, 2, 4])
        self._checkVector(bytes([1, 0, 0, 1, 4, 0, 6, 81, 1]), [1, 256, 4])
        self._checkVector(bytes([
            45, 0, 0, 0,
            0, 232, 3, 0,
            4, 0, 0, 0,
            12, 82, 1
        ]), [45, 256000, 4])
        self._checkVector(bytes([
            45, 0, 0, 0, 0, 0, 0, 0,
            255, 255, 255, 255, 255, 255, 255, 127,
            4, 0, 0, 0, 0, 0, 0, 0,
            24, 83, 1
        ]), [45, 9223372036854775807, 4])

        self._checkVector(bytes([1, 2, 4, 9, 4, 92, 1]), [1, 2, 4, 9])
        self._checkVector(bytes([1, 0, 0, 1, 4, 0, 9, 0, 8, 93, 1]), [1, 256, 4, 9])
        self._checkVector(bytes([
            45, 0, 0, 0,
            0, 232, 3, 0,
            4, 0, 0, 0,
            9, 0, 0, 0,
            16, 94, 1
        ]), [45, 256000, 4, 9])
        self._checkVector(bytes([
            45, 0, 0, 0, 0, 0, 0, 0,
            255, 255, 255, 255, 255, 255, 255, 127,
            4, 0, 0, 0, 0, 0, 0, 0,
            9, 0, 0, 0, 0, 0, 0, 0,
            32, 95, 1
        ]), [45, 9223372036854775807, 4, 9])

        self._checkVector(bytes([
            205, 204, 140, 63,
            0, 0, 0, 64,
            0, 0, 128, 64,
            12, 86, 1
        ]), [1.1, 2, 4])
        self._checkVector(bytes([
            154, 153, 153, 153, 153, 153, 241, 63,
            0, 0, 0, 0, 0, 0, 112, 64,
            0, 0, 0, 0, 0, 0, 16, 64,
            24, 87, 1
        ]), [1.1, 256, 4])

        self._checkVector(bytes([
            205, 204, 140, 63,
            0, 0, 0, 64,
            0, 0, 128, 64,
            0, 0, 16, 65,
            16, 98, 1
        ]), [1.1, 2, 4, 9])
        self._checkVector(bytes([
            154, 153, 153, 153, 153, 153, 241, 63,
            0, 0, 0, 0, 0, 0, 112, 64,
            0, 0, 0, 0, 0, 0, 16, 64,
            0, 0, 0, 0, 0, 0, 34, 64,
            32, 99, 1
        ]), [1.1, 256, 4, 9])

    def test_single_value_map(self):
        flx = FlxValue.from_bytes(bytes([97, 0, 1, 3, 1, 1, 1, 12, 4, 2, 36, 1]))  # {"a": 12}
        self.assertEqual(len(flx), 1)
        self.assertEqual(flx["a"].value(), 12)

    def test_two_value_map(self):
        flx = FlxValue.from_bytes(bytes([0, 97, 0, 2, 4, 4, 2, 1, 2, 45, 12, 4, 4, 4, 36, 1]))  # {"a": 12, "":45}
        self.assertEqual(len(flx), 2)
        self.assertEqual(flx["a"].value(), 12)
        self.assertEqual(flx[""].value(), 45)

    def test_complex_map(self):
        flx = self._complex_map()
        # {
        #     "age": 35,
        #     "flags": [True, False, True, True],
        #     "weight": 72.5,
        #     "name": "Maxim",
        #     "address": {
        #         "city": "Bla",
        #         "zip": "12345",
        #         "countryCode": "XX",
        #     }
        # }
        self.assertEqual(len(flx), 5)
        self.assertEqual(flx["age"].value(), 35)
        self.assertEqual(flx["weight"].value(), 72.5)
        self.assertEqual(flx["name"].value(), "Maxim")
        self.assertEqual(len(flx["flags"]), 4)
        self.assertEqual(flx["flags"][0].value(), True)
        self.assertEqual(flx["flags"][1].value(), False)
        self.assertEqual(flx["flags"][2].value(), True)
        self.assertEqual(flx["flags"][3].value(), True)

        self.assertEqual(len(flx["address"]), 3)
        self.assertEqual(flx["address"]["city"].value(), "Bla")
        self.assertEqual(flx["address"]["zip"].value(), "12345")
        self.assertEqual(flx["address"]["countryCode"].value(), "XX")

        self.assertEqual(flx["address"]["country"], None)
        self.assertEqual(flx[1], None)
        self.assertEqual(flx["flags"][4], None)

        self.assertEqual(flx.age.value(), 35)
        self.assertEqual(flx.weight.value(), 72.5)
        self.assertEqual(flx.name.value(), "Maxim")

        self.assertEqual(len(flx.flags), 4)
        self.assertEqual(flx.flags[0].value(), True)
        self.assertEqual(flx.flags[1].value(), False)
        self.assertEqual(flx.flags[2].value(), True)
        self.assertEqual(flx.flags[3].value(), True)
        self.assertEqual(flx.address.city.value(), "Bla")
        self.assertEqual(flx.address.zip.value(), "12345")
        self.assertEqual(flx.address.countryCode.value(), "XX")

    def test_iterator(self):
        for v in FlxValue.from_bytes(bytes([25, 4, 1])):
            self.assertEqual(v, 25)

        x, y, z, w = map(lambda v1: v1.value(), FlxValue.from_bytes(bytes([1, 2, 4, 9, 4, 92, 1])))
        self.assertEqual(x, 1)
        self.assertEqual(y, 2)
        self.assertEqual(z, 4)
        self.assertEqual(w, 9)

        index = 0
        for k, v in FlxValue.from_bytes(bytes([0, 97, 0, 2, 4, 4, 2, 1, 2, 45, 12, 4, 4, 4, 36, 1])):  # {"a": 12, "":45}
            if index == 0:
                self.assertEqual(k.value(), "")
                self.assertEqual(v.value(), 45)
            elif index == 1:
                self.assertEqual(k.value(), "a")
                self.assertEqual(v.value(), 12)
            else:
                self.fail("unexpected index")
            index = index + 1

    def test_to_object(self):
        object = self._complex_map().to_object()
        self.assertEqual(object["age"], 35)
        self.assertEqual(object["weight"], 72.5)
        self.assertEqual(object["name"], "Maxim")
        self.assertEqual(len(object["flags"]), 4)
        self.assertEqual(object["flags"][0], True)
        self.assertEqual(object["flags"][1], False)
        self.assertEqual(object["flags"][2], True)
        self.assertEqual(object["flags"][3], True)

        self.assertEqual(len(object["address"]), 3)
        self.assertEqual(object["address"]["city"], "Bla")
        self.assertEqual(object["address"]["zip"], "12345")
        self.assertEqual(object["address"]["countryCode"], "XX")

    def test_value_to_string(self):
        self.assertEqual(FlxValue.from_bytes(bytes([25, 4, 1])).json(), "25")
        self.assertEqual(FlxValue.from_bytes(bytes([0, 0, 144, 64, 14, 4])).json(), "4.5")
        self.assertEqual(FlxValue.from_bytes(bytes([0, 0, 1])).json(), "null")
        self.assertEqual(FlxValue.from_bytes(bytes([1, 104, 1])).json(), "true")
        self.assertEqual(FlxValue.from_bytes(bytes([0, 104, 1])).json(), "false")
        self.assertEqual(FlxValue.from_bytes(bytes([
            10, 104, 101, 108, 108, 111, 32, 240, 159, 152, 177, 0, 11, 20, 1
        ])).json(), '"hello 😱"')
        self.assertEqual(FlxValue.from_bytes(bytes([1, 2, 4, 9, 4, 92, 1])).json(), "[1,2,4,9]")
        self.assertEqual(FlxValue.from_bytes(bytes([
            0, 97, 0, 2, 4, 4, 2, 1, 2, 45, 12, 4, 4, 4, 36, 1
        ])).json(), '{"":45,"a":12}')
        self.assertEqual(self._complex_map().json(), '{"address":{"city":"Bla","countryCode":"XX","zip":"12345"},"age":35,"flags":[true,false,true,true],"name":"Maxim","weight":72.5}')

    def _checkVector(self, _bytes, values):
        flx = FlxValue.from_bytes(_bytes)
        self.assertEqual(len(flx), len(values))
        for i, value in enumerate(values):
            self.assertAlmostEqual(flx[i].value(), value)

    @staticmethod
    def _complex_map():
        return FlxValue.from_bytes(bytes([
            97, 100, 100, 114, 101, 115, 115, 0,
            99, 105, 116, 121, 0, 3, 66, 108, 97, 0,
            99, 111, 117, 110, 116, 114, 121, 67, 111, 100, 101, 0,
            2, 88, 88, 0,
            122, 105, 112, 0,
            5, 49, 50, 51, 52, 53, 0,
            3, 38, 29, 14, 3, 1, 3, 38, 22, 15, 20, 20, 20,
            97, 103, 101, 0,
            102, 108, 97, 103, 115, 0,
            4, 1, 0, 1, 1,
            110, 97, 109, 101, 0,
            5, 77, 97, 120, 105, 109, 0,
            119, 101, 105, 103, 104, 116, 0,
            5, 93, 36, 33, 23, 12, 0, 0, 7, 0, 0, 0, 1, 0, 0, 0, 5, 0, 0, 0, 60, 0, 0, 0, 35, 0, 0, 0, 51, 0, 0, 0, 45,
            0, 0, 0, 0, 0, 145, 66, 36, 4, 144, 20, 14, 25, 38, 1
        ]))


if __name__ == '__main__':
    unittest.main()
