from google.protobuf.message import Message
from google.protobuf.descriptor import FieldDescriptor


__all__ = ["protobuf_to_dict", "TYPE_CALLABLE_MAP", "dict_to_protobuf", "REVERSE_TYPE_CALLABLE_MAP"]


TYPE_CALLABLE_MAP = {
    FieldDescriptor.TYPE_DOUBLE: float,
    FieldDescriptor.TYPE_FLOAT: float,
    FieldDescriptor.TYPE_INT32: int,
    FieldDescriptor.TYPE_INT64: long,
    FieldDescriptor.TYPE_UINT32: int,
    FieldDescriptor.TYPE_UINT64: long,
    FieldDescriptor.TYPE_SINT32: int,
    FieldDescriptor.TYPE_SINT64: long,
    FieldDescriptor.TYPE_FIXED32: int,
    FieldDescriptor.TYPE_FIXED64: long,
    FieldDescriptor.TYPE_SFIXED32: int,
    FieldDescriptor.TYPE_SFIXED64: long,
    FieldDescriptor.TYPE_BOOL: bool,
    FieldDescriptor.TYPE_STRING: unicode,
    FieldDescriptor.TYPE_BYTES: lambda b: b.encode("base64"),
    FieldDescriptor.TYPE_ENUM: int,
}


def repeated(type_callable):
    return lambda value_list: [type_callable(value) for value in value_list]


def enum_label_name(field, value):
    return field.enum_type.values_by_number[int(value)].name


def protobuf_to_dict(pb, type_callable_map=TYPE_CALLABLE_MAP, use_enum_labels=False):
    result_dict = {}
    for field, value in pb.ListFields():
        if field.type == FieldDescriptor.TYPE_MESSAGE:
            # recursively encode protobuf sub-message
            type_callable = lambda pb: protobuf_to_dict(pb,
                type_callable_map=type_callable_map,
                use_enum_labels=use_enum_labels)
        elif field.type in type_callable_map:
            type_callable = type_callable_map[field.type]
        else:
            raise TypeError("Field %s.%s has unrecognised type id %d" % (
                pb.__class__.__name__, field.name, field.type))    
        if use_enum_labels and field.type == FieldDescriptor.TYPE_ENUM:
            type_callable = lambda value: enum_label_name(field, value)
        if field.label == FieldDescriptor.LABEL_REPEATED:
            type_callable = repeated(type_callable)
        result_dict[field.name] = type_callable(value)
    return result_dict

def set_bytes(pb, field, value):
    setattr(pb, field, value.decode('base64'))

REVERSE_TYPE_CALLABLE_MAP = {
    FieldDescriptor.TYPE_DOUBLE: setattr,
    FieldDescriptor.TYPE_FLOAT: setattr,
    FieldDescriptor.TYPE_INT32: setattr,
    FieldDescriptor.TYPE_INT64: setattr,
    FieldDescriptor.TYPE_UINT32: setattr,
    FieldDescriptor.TYPE_UINT64: setattr,
    FieldDescriptor.TYPE_SINT32: setattr,
    FieldDescriptor.TYPE_SINT64: setattr,
    FieldDescriptor.TYPE_FIXED32: setattr,
    FieldDescriptor.TYPE_FIXED64: setattr,
    FieldDescriptor.TYPE_SFIXED32: setattr,
    FieldDescriptor.TYPE_SFIXED64: setattr,
    FieldDescriptor.TYPE_BOOL: setattr,
    FieldDescriptor.TYPE_STRING: setattr,
    FieldDescriptor.TYPE_BYTES: set_bytes,
    FieldDescriptor.TYPE_ENUM: setattr,
}

def dict_to_protobuf(pb, value, type_callable_map=REVERSE_TYPE_CALLABLE_MAP, ignore_missing=False):
    return _dict_to_protobuf(pb(), value, type_callable_map, ignore_missing)

def _dict_to_protobuf(pb, value, type_callable_map, ignore_missing):
    desc = pb.DESCRIPTOR
    
    for k, v in value.items():
        if k not in desc.fields_by_name:
            if ignore_missing:
                 continue
            else:
                raise KeyError("%s does not have a field called %s" % (pb, k))
        field_type = desc.fields_by_name[k].type
        
        if desc.fields_by_name[k].label == FieldDescriptor.LABEL_REPEATED:
            for item in v:
                if field_type == FieldDescriptor.TYPE_MESSAGE:
                    m = getattr(pb, k).add()
                    _dict_to_protobuf(m, item, type_callable_map)
                else:
                    getattr(pb, k).append(item)
            continue
        if field_type == FieldDescriptor.TYPE_MESSAGE:
            _dict_to_protobuf(getattr(pb, k), v, type_callable_map)
            continue

        type_callable_map[field_type](pb, k, v)
    
    return pb
