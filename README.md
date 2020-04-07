# FlexBuffers-Python
This is a collection of Python classes to read and write [FlexBuffers](https://google.github.io/flatbuffers/flexbuffers.html)

---
⚠️ This library is designed to be convinient way for Python developers to read and write FlexBuffers. It is not optimized for performance!
---

# Usage
## Building a FlexBuffer
`FlxBuilder` class lets you serialise a python object into a FlexBuffer by using the `fromValue` static method:
```
FlxBuilder.fromValue({"a": 12})
```

This expression will return a `bytes` object. which contains the FlexBuffer of the passed map.
For more examples please have a look at [Builder Unit Tests](https://github.com/mzaks/FlexBuffers-Python/blob/master/flexbuffers/flx_builder_tests.py) and [Roundtrip Tests](https://github.com/mzaks/FlexBuffers-Python/blob/master/flexbuffers/flx_round_trip_test.py)

As this implementation is not designed to be performance critical. I decided to keep all deduplication strategies on by default. The deduplication strategies include:
- String deduplication
- Key deduplication
- Keys Vector deduplication

## Reading a FlexBuffer
`FlxValue` class lets you access the data inside of the FlexBuffer. Please use the static `from_bytes` method to instantiate a `FlxValue` object by passing it a `bytes` object:
```
flx = FlxValue.from_bytes(buffer)
```

If the buffer was representing just a single value, you can access this value by calling the `value()` method. In case that the buffer was representing a Vector or a Map you can use the `[]` operator to access the inner `FlxValue` and than use the `value()` method to exctract the actual value. e.g.:
```
flx["age"].value()
flx["address"]["city"].value()
```

The `FlxValue` class also implements `__itter__` method ands so can be itterated upon. For even more convinience there is a `to_object` method which does deep traversal and converts the buffer into a fully materialised Python object. This is however is not desirable if you need to access only a few values out of the buffer.

And last but not least, there is a `json()` method which let's you convert the FlexBuffer into minified JSON. This option is specifically interesting, when you need to debug.

Please have a look at [FlexValue Unit Tests](https://github.com/mzaks/FlexBuffers-Python/blob/master/flexbuffers/flx_value_tests.py) and [Roundtrip Tests](https://github.com/mzaks/FlexBuffers-Python/blob/master/flexbuffers/flx_round_trip_test.py) to see more examples.
