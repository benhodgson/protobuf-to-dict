import unittest
from tests.sample_pb2 import MessageOfTypes, extDouble, extString, NestedExtension
from protobuf_to_dict import protobuf_to_dict, dict_to_protobuf
import base64
import nose.tools
import json


class Test(unittest.TestCase):
    def test_basics(self):
        m = self.populate_MessageOfTypes()
        d = protobuf_to_dict(m)
        self.compare(m, d, ['nestedRepeated'])

        m2 = dict_to_protobuf(MessageOfTypes, d)
        assert m == m2

    def test_use_enum_labels(self):
        m = self.populate_MessageOfTypes()
        d = protobuf_to_dict(m, use_enum_labels=True)
        self.compare(m, d, ['enm', 'enmRepeated', 'nestedRepeated'])
        assert d['enm'] == 'C'
        assert d['enmRepeated'] == ['A', 'C']

        m2 = dict_to_protobuf(MessageOfTypes, d)
        assert m == m2

        d['enm'] = 'MEOW'
        with nose.tools.assert_raises(KeyError):
            dict_to_protobuf(MessageOfTypes, d)

        d['enm'] = 'A'
        d['enmRepeated'] = ['B']
        dict_to_protobuf(MessageOfTypes, d)

        d['enmRepeated'] = ['CAT']
        with nose.tools.assert_raises(KeyError):
            dict_to_protobuf(MessageOfTypes, d)

    def test_repeated_enum(self):
        m = self.populate_MessageOfTypes()
        d = protobuf_to_dict(m, use_enum_labels=True)
        self.compare(m, d, ['enm', 'enmRepeated', 'nestedRepeated'])
        assert d['enmRepeated'] == ['A', 'C']

        m2 = dict_to_protobuf(MessageOfTypes, d)
        assert m == m2

        d['enmRepeated'] = ['MEOW']
        with nose.tools.assert_raises(KeyError):
            dict_to_protobuf(MessageOfTypes, d)

    def test_nested_repeated(self):
        m = self.populate_MessageOfTypes()
        m.nestedRepeated.extend([MessageOfTypes.NestedType(req=str(i)) for i in range(10)])

        d = protobuf_to_dict(m)
        self.compare(m, d, exclude=['nestedRepeated'])
        assert d['nestedRepeated'] == [{'req': str(i)} for i in range(10)]

        m2 = dict_to_protobuf(MessageOfTypes, d)
        assert m == m2

    def test_reverse(self):
        m = self.populate_MessageOfTypes()
        m2 = dict_to_protobuf(MessageOfTypes, protobuf_to_dict(m))
        assert m == m2
        m2.dubl = 0
        assert m2 != m

    def test_incomplete(self):
        m = self.populate_MessageOfTypes()
        d = protobuf_to_dict(m)
        d.pop('dubl')
        m2 = dict_to_protobuf(MessageOfTypes, d)
        assert m2.dubl == 0
        assert m != m2

    def test_pass_instance(self):
        m = self.populate_MessageOfTypes()
        d = protobuf_to_dict(m)
        d['dubl'] = 1
        m2 = dict_to_protobuf(m, d)
        assert m is m2
        assert m.dubl == 1

    def test_strict(self):
        m = self.populate_MessageOfTypes()
        d = protobuf_to_dict(m)
        d['meow'] = 1
        with nose.tools.assert_raises(KeyError):
            m2 = dict_to_protobuf(MessageOfTypes, d)
        m2 = dict_to_protobuf(MessageOfTypes, d, strict=False)
        assert m == m2

    def populate_MessageOfTypes(self):
        m = MessageOfTypes()
        m.dubl = 1.7e+308
        m.flot = 3.4e+038
        m.i32 = 2 ** 31 - 1 # 2147483647 #
        m.i64 = 2 ** 63 - 1 #0x7FFFFFFFFFFFFFFF
        m.ui32 = 2 ** 32 - 1
        m.ui64 = 2 ** 64 - 1
        m.si32 = -1 * m.i32
        m.si64 = -1 * m.i64
        m.f32 = m.i32
        m.f64 = m.i64
        m.sf32 = m.si32
        m.sf64 = m.si64
        m.bol = True
        m.strng = "string"
        m.byts = b'\n\x14\x1e'
        assert len(m.byts) == 3, len(m.byts)
        m.nested.req = "req"
        m.enm = MessageOfTypes.C #@UndefinedVariable
        m.enmRepeated.extend([MessageOfTypes.A, MessageOfTypes.C])
        m.range.extend(range(10))
        return m

    def compare(self, m, d, exclude=None):
        i = 0
        exclude = ['byts', 'nested'] + (exclude or [])
        for i, field in enumerate(MessageOfTypes.DESCRIPTOR.fields): #@UndefinedVariable
            if field.name not in exclude:
                assert field.name in d, field.name
                assert d[field.name] == getattr(m, field.name), (field.name, d[field.name])
        assert i > 0
        assert m.byts == base64.b64decode(d['byts'])
        assert d['nested'] == {'req': m.nested.req}

    def test_extensions(self):
        m = MessageOfTypes()

        primitives = {extDouble: 123.4, extString: "string", NestedExtension.extInt: 4}

        for key, value in primitives.items():
            m.Extensions[key] = value
        m.Extensions[NestedExtension.extNested].req = "nested"

        # Confirm compatibility with JSON serialization
        res = json.loads(json.dumps(protobuf_to_dict(m)))
        assert '___X' in res
        exts = res['___X']
        assert set(exts.keys()) == set([str(f.number) for f, _ in m.ListFields() if f.is_extension])
        for key, value in primitives.items():
            assert exts[str(key.number)] == value
        assert exts[str(NestedExtension.extNested.number)]['req'] == 'nested'

        deser = dict_to_protobuf(MessageOfTypes, res)
        assert deser
        for key, value in primitives.items():
            assert deser.Extensions[key] == m.Extensions[key]
        assert deser.Extensions[NestedExtension.extNested].req == m.Extensions[NestedExtension.extNested].req
