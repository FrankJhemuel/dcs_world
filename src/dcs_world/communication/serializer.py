import json
from dataclasses import asdict, fields, is_dataclass


def serialize(message, indent: int | None = None) -> str:
    """Convert a dataclass message into a JSON string."""
    return json.dumps(asdict(message), indent=indent)


def deserialize(data: str, message_type):
    """Convert a JSON string into a dataclass message."""

    values = json.loads(data)

    if not is_dataclass(message_type):
        raise TypeError("message_type must be a dataclass")

    return _construct_message(values, message_type)


def _construct_message(values: dict, message_type):
    """Recursively construct a dataclass from a dictionary."""

    from typing import get_type_hints

    type_hints = get_type_hints(message_type)

    for field in fields(message_type):
        field_type = type_hints[field.name]

        if field.name in values and is_dataclass(field_type):
            values[field.name] = _construct_message(
                values[field.name],
                field_type
            )

    return message_type(**values)