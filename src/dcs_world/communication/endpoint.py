import zlib

_BASE_PORT = 20000
_PORT_RANGE = 40000


def endpoint_for_topic(topic: str) -> str:
    topic_hash = zlib.crc32(topic.encode("utf-8"))
    port = _BASE_PORT + (topic_hash % _PORT_RANGE)

    return f"tcp://127.0.0.1:{port}"