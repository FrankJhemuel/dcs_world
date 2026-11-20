import zmq

from .serializer import serialize
from .endpoint import endpoint_for_topic


class Publisher:

    def __init__(self, topic: str):

        self.topic = topic.encode("utf-8")
        self.endpoint = endpoint_for_topic(topic)

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.PUB)

        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.bind(self.endpoint)

    def publish(self, message):

        if self.socket is None:
            raise RuntimeError("Publisher is closed.")

        payload = serialize(message).encode("utf-8")

        self.socket.send_multipart([
            self.topic,
            payload
        ])

    def close(self):

        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def __del__(self):
        self.close()