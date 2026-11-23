import json

from dataclasses import fields, is_dataclass
from enum import Enum
from typing import get_args, get_origin, get_type_hints


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


def _construct_value(value, expected_type):
    """Recursively reconstruct a value according to its expected type."""

    if value is None:
        return None

    origin = get_origin(expected_type)
    args = get_args(expected_type)

    # Handle lists, e.g. list[Pose].
    if origin is list:
        item_type = args[0]
        return [
            _construct_value(item, item_type)
            for item in value
        ]

    # Handle dictionaries, if their value type is specified.
    if origin is dict:
        key_type, value_type = args
        return {
            key: _construct_value(item, value_type)
            for key, item in value.items()
        }

    # Handle nested dataclasses.
    if is_dataclass(expected_type):
        return _construct_message(value, expected_type)

    # Handle enums.
    if isinstance(expected_type, type) and issubclass(expected_type, Enum):
        return expected_type[value.upper()]

    return value


def _construct_message(values: dict, message_type):
    """Recursively construct a dataclass from a dictionary."""

    type_hints = get_type_hints(message_type)

    kwargs = {}

    for field in fields(message_type):
        if field.name not in values:
            continue

        field_type = type_hints[field.name]

        kwargs[field.name] = _construct_value(
            values[field.name],
            field_type,
        )

    return message_type(**kwargs)