import zmq

from .serializer import deserialize
from .endpoint import endpoint_for_topic


class Subscriber:

    def __init__(self, topic: str, message_type, callback=None):

        self.topic = topic.encode("utf-8")
        self.message_type = message_type
        self.callback = callback

        self.endpoint = endpoint_for_topic(topic)

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.SUB)

        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.setsockopt(zmq.SUBSCRIBE, self.topic)

        self.socket.connect(self.endpoint)

    def receive(self):

        try:
            topic, payload = self.socket.recv_multipart(flags=zmq.NOBLOCK)

        except zmq.Again:
            return  

        if topic != self.topic:
            return

        message = deserialize(
            payload.decode("utf-8"),
            self.message_type
        )

        if self.callback is not None:
            self.callback(message)

    def close(self):
        self.socket.close()