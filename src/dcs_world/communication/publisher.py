import zmq

from .serializer import serialize


PUBLISHER_ENDPOINT = "tcp://127.0.0.1:5555"


class Publisher:

    def __init__(self, topic: str):
        self.topic = topic.encode("utf-8")

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.PUB)

        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.connect(PUBLISHER_ENDPOINT)

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