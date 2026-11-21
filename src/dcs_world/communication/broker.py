import zmq


PUBLISHER_ENDPOINT = "tcp://127.0.0.1:5555"
SUBSCRIBER_ENDPOINT = "tcp://127.0.0.1:5556"


def main():
    context = zmq.Context()

    # Receives messages from publishers.
    frontend = context.socket(zmq.XSUB)
    frontend.setsockopt(zmq.LINGER, 0)
    frontend.bind(PUBLISHER_ENDPOINT)

    # Forwards messages to subscribers.
    backend = context.socket(zmq.XPUB)
    backend.setsockopt(zmq.LINGER, 0)
    backend.bind(SUBSCRIBER_ENDPOINT)

    print("[Broker] Initialized.")
    print(f"[Broker] Publisher endpoint: {PUBLISHER_ENDPOINT}")
    print(f"[Broker] Subscriber endpoint: {SUBSCRIBER_ENDPOINT}")

    try:
        zmq.proxy(frontend, backend)

    except KeyboardInterrupt:
        print("[Broker] Stopping...")

    finally:
        frontend.close()
        backend.close()
        context.term()


if __name__ == "__main__":
    main()