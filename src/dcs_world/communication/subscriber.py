import zmq
import fnmatch

from .serializer import deserialize


SUBSCRIBER_ENDPOINT = "tcp://127.0.0.1:5556"


class Subscriber:

    def __init__(
        self,
        topic: str,
        message_type,
        callback=None
    ):

        self.topic = topic
        self.message_type = message_type
        self.callback = callback

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.SUB)

        self.socket.setsockopt(zmq.LINGER, 0)

        # Subscribe to the common prefix before the wildcard.
        prefix = topic.split("*")[0]

        self.socket.setsockopt(
            zmq.SUBSCRIBE,
            prefix.encode("utf-8")
        )

        self.socket.connect(SUBSCRIBER_ENDPOINT)

    def receive(self):

        while True:

            try:
                frames = self.socket.recv_multipart(
                    flags=zmq.NOBLOCK
                )

            except zmq.Again:
                break

            topic, payload = frames

            topic = topic.decode("utf-8")

            if not fnmatch.fnmatchcase(topic, self.topic):
                continue

            message = deserialize(
                payload,
                self.message_type
            )

            if self.callback is not None:
                self.callback(message)

    def close(self):

        if self.socket is not None:
            self.socket.close()
            self.socket = None