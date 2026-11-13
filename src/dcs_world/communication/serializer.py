import json

from dataclasses import asdict, fields, is_dataclass
from enum import Enum
from typing import get_type_hints


def _serialize_value(value):
    """Recursively convert values into JSON-compatible objects."""

    if isinstance(value, Enum):
        return value.name

    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _serialize_value(getattr(value, field.name))
            for field in fields(value)
        }

    if isinstance(value, list):
        return [_serialize_value(item) for item in value]

    if isinstance(value, dict):
        return {
            key: _serialize_value(item)
            for key, item in value.items()
        }

    return value


def serialize(message, indent: int | None = None) -> str:
    """Convert a dataclass message into a JSON string."""

    if not is_dataclass(message) or isinstance(message, type):
        raise TypeError("message must be a dataclass instance")

    return json.dumps(_serialize_value(message), indent=indent)


def deserialize(data: str, message_type):
    """Convert a JSON string into a dataclass message."""

    values = json.loads(data)

    if not is_dataclass(message_type):
        raise TypeError("message_type must be a dataclass")

    return _construct_message(values, message_type)


def _construct_message(values: dict, message_type):
    """Recursively construct a dataclass from a dictionary."""

    type_hints = get_type_hints(message_type)

    for field in fields(message_type):
        field_type = type_hints[field.name]

        if field.name not in values:
            continue

        if is_dataclass(field_type):
            values[field.name] = _construct_message(
                values[field.name],
                field_type
            )

        elif isinstance(field_type, type) and issubclass(field_type, Enum):
            values[field.name] = field_type[values[field.name]]

    return message_type(**values)