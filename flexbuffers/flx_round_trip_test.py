import json
import unittest

from flexbuffers.flx_builder import FlxBuilder
from flexbuffers.flx_value import FlxValue


class Person:
    def __init__(self, name):
        self.name = name
        self.age = 38
        self.weight = 73.1


class MyTestCase(unittest.TestCase):
    def test_dict(self):
        obj = {
            "age": 38,
            "weight": 73.1,
            "flags": [True, False, True, True],
            "name": "Maxim",
            "address": {
                "city": "Bla",
                "zip": 12345,
                "countryCode": "XX"
            }
        }
        buffer = FlxBuilder.fromValue(obj)
        flx = FlxValue.from_bytes(buffer)
        self.assertEqual(flx.age.value(), 38)
        self.assertEqual(flx.weight.value(), 73.1)
        self.assertEqual(len(flx.flags), 4)
        self.assertEqual(flx.flags[0].value(), True)
        self.assertEqual(flx.flags[1].value(), False)
        self.assertEqual(flx.flags[2].value(), True)
        self.assertEqual(flx.flags[3].value(), True)
        self.assertEqual(flx.name.value(), "Maxim")
        self.assertEqual(flx.address.city.value(), "Bla")
        self.assertEqual(flx.address.zip.value(), 12345)
        self.assertEqual(flx.address.countryCode.value(), "XX")

    def test_class(self):
        person = Person("Max")
        buffer = FlxBuilder.fromValue(person)
        flx = FlxValue.from_bytes(buffer)
        self.assertEqual(flx.age.value(), 38)
        self.assertEqual(flx.weight.value(), 73.1)
        self.assertEqual(flx.name.value(), "Max")

    def test_json(self):
        p_string = '''{
            "age": 38,
            "weight": 73.1,
            "flags": [true, false, true, true],
            "name": "Maxim",
            "address": {
                "city": "Bla",
                "zip": 12345,
                "countryCode": "XX"
            }
        }'''
        p_json = json.loads(p_string)
        buffer = FlxBuilder.fromValue(p_json)
        flx = FlxValue.from_bytes(buffer)
        self.assertEqual(flx.age.value(), 38)
        self.assertEqual(flx.weight.value(), 73.1)
        self.assertEqual(len(flx.flags), 4)
        self.assertEqual(flx.flags[0].value(), True)
        self.assertEqual(flx.flags[1].value(), False)
        self.assertEqual(flx.flags[2].value(), True)
        self.assertEqual(flx.flags[3].value(), True)
        self.assertEqual(flx.name.value(), "Maxim")
        self.assertEqual(flx.address.city.value(), "Bla")
        self.assertEqual(flx.address.zip.value(), 12345)
        self.assertEqual(flx.address.countryCode.value(), "XX")

    def test_vector_with_same_key_map(self):
        buffer = FlxBuilder.fromValue([{"something": 12}, {"something": 45}])
        flx = FlxValue.from_bytes(buffer)
        self.assertEqual(len(flx), 2)
        self.assertEqual(flx[0].something.num(), 12)
        self.assertEqual(flx[1].something.num(), 45)

if __name__ == '__main__':
    unittest.main()
