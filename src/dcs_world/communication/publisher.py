import time
import zmq

from .serializer import serialize


PUBLISHER_ENDPOINT = "tcp://127.0.0.1:5555"

DEFAULT_HANDSHAKE_TIMEOUT = 10000


class Publisher:

    def __init__(
        self,
        topic: str,
        handshake: bool = False,
        handshake_timeout: int = DEFAULT_HANDSHAKE_TIMEOUT
    ):

        self.topic = topic.encode("utf-8")
        self.handshake = handshake
        self.handshake_timeout = handshake_timeout
        self.handshake_complete = not handshake

        self.context = zmq.Context.instance()

        # XPUB allows the publisher to receive subscription events.
        socket_type = zmq.XPUB if handshake else zmq.PUB

        self.socket = self.context.socket(socket_type)

        self.socket.setsockopt(zmq.LINGER, 0)

        if handshake:
            self.socket.setsockopt(zmq.XPUB_VERBOSE, 1)

        self.socket.connect(PUBLISHER_ENDPOINT)

    def _wait_for_subscription(self):

        if self.handshake_complete:
            return

        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)

        start_time = time.monotonic()

        while True:

            elapsed = (time.monotonic() - start_time) * 1000
            remaining = self.handshake_timeout - elapsed

            if remaining <= 0:
                raise TimeoutError(
                    f"No subscriber found for topic "
                    f"'{self.topic.decode()}' within "
                    f"{self.handshake_timeout} ms."
                )

            events = dict(poller.poll(int(remaining)))

            if self.socket not in events:
                continue

            # XPUB subscription event:
            # b'\x01' + subscription prefix
            # b'\x00' + subscription prefix
            event = self.socket.recv()

            if not event:
                continue

            subscribed = event[0] == 1
            prefix = event[1:]

            if subscribed and self.topic.startswith(prefix):

                self.handshake_complete = True

                print(
                    f"[Publisher] Handshake completed: "
                    f"{self.topic.decode()}"
                )

                return

    def publish(self, message):

        if self.socket is None:
            raise RuntimeError("Publisher is closed.")

        # Wait for a matching subscriber before the first publication.
        if self.handshake:
            self._wait_for_subscription()

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