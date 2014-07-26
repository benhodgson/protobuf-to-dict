# protobuf-to-dict

protobuf-to-dict is a small Python library for creating dicts from protocol
buffers. It is intended to be used as an intermediate step before
serialization (e.g. to JSON).

## Installation

Use `pip install protobuf-to-dict` or `python setup.py install`.

## Example

Given the `google.protobuf.message.Message` subclass `MyMessage`:

```python
>>> from protobuf_to_dict import protobuf_to_dict
>>> my_message = MyMessage()
>>> # pb_my_message is a protobuf string
>>> my_message.ParseFromString(pb_my_message)
>>> protobuf_to_dict(my_message)
{'message': 'Hello'}
```

## Caveats

This library grew out of the desire to serialize a protobuf-encoded message to
[JSON](http://json.org/). As JSON has no built-in binary type (all strings in
JSON are Unicode strings), any field whose type is
`FieldDescriptor.TYPE_BYTES` is, by default, converted to a base64-encoded
string.

If you want to override this behaviour, you may do so by passing
`protobuf_to_dict` a dictionary of protobuf types to callables via the
`type_callable_map` kwarg:

```python
>>> from copy import copy
>>> from google.protobuf.descriptor import FieldDescriptor
>>> from protobuf_to_dict import protobuf_to_dict, TYPE_CALLABLE_MAP
>>>
>>> type_callable_map = copy(TYPE_CALLABLE_MAP)
>>> # convert TYPE_BYTES to a Python bytestring
>>> type_callable_map[FieldDescriptor.TYPE_BYTES] = str
>>>
>>> # my_message is a google.protobuf.message.Message instance
>>> protobuf_to_dict(my_message, type_callable_map=type_callable_map)
```

By default, the integer representation is used for enum values. To use their
string labels instead, pass `use_enum_labels=True` into `protobuf_to_dict`:

```python
>>> protobuf_to_dict(my_message, use_enum_labels=True)
```

## Unit testing

Tests are under `src/tests/`.

```sh
$ python setup.py nosetests
```

To regenerate `src/tests/sample_pb2.py`:

```sh
$ protoc --python_out=src -Isrc src/tests/sample.proto 
```

## Authors

protobuf-to-dict is written and maintained by
[Ben Hodgson](http://benhodgson.com/), with significant contributions from
[Nino Walker](https://github.com/ninowalker),
[Jonathan Klaassen](https://github.com/jaklaassen), and
[Tristram Gräbener](http://blog.tristramg.eu/).


## (Un)license

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute
this software, either in source code form or as a compiled binary, for any
purpose, commercial or non-commercial, and by any means.

In jurisdictions that recognize copyright laws, the author or authors of this
software dedicate any and all copyright interest in the software to the public
domain. We make this dedication for the benefit of the public at large and to
the detriment of our heirs and successors. We intend this dedication to be an
overt act of relinquishment in perpetuity of all present and future rights to
this software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>
