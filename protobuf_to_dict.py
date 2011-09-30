from google.protobuf.descriptor import FieldDescriptor

__all__ = ['protobuf_to_dict']

TYPE_CALLABLE_MAP = {
    FieldDescriptor.TYPE_BOOL: bool,
    FieldDescriptor.TYPE_BYTES: lambda b: b.encode('string_escape'),
    FieldDescriptor.TYPE_DOUBLE: float,
    FieldDescriptor.TYPE_ENUM: int,
    FieldDescriptor.TYPE_FIXED32: float,
    FieldDescriptor.TYPE_FIXED64: float,
    FieldDescriptor.TYPE_FLOAT: float,
    FieldDescriptor.TYPE_INT32: int,
    FieldDescriptor.TYPE_INT64: long,
    FieldDescriptor.TYPE_MESSAGE: protobuf_to_dict, # recursion, bitches.
    FieldDescriptor.TYPE_SFIXED32: float,
    FieldDescriptor.TYPE_SFIXED64: float,
    FieldDescriptor.TYPE_SINT32: int,
    FieldDescriptor.TYPE_SINT64: long,
    FieldDescriptor.TYPE_STRING: unicode,
    FieldDescriptor.TYPE_UINT32: int,
    FieldDescriptor.TYPE_UINT64: long,
}

def repeated(type_callable):
    return lambda value_list: [type_callable(value) for value in value_list]

def protobuf_to_dict(pb):
    items = []
    for field, value in protobuf.ListFields():
        if field.type not in TYPE_CALLABLE_MAP:
            raise TypeError("Field %s.%s has unrecognised type id %d" % (
                pb.__class__.__name__, field.name, field.type))
        type_callable = TYPE_CALLABLE_MAP[field.type]
        if field.label == FieldDescriptor.LABEL_REPEATED:
            type_callable = repeated(type_callable)
        items.append((field.name, type_callable(value)))
    return dict(items)
