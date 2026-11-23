# Communication

The `communication` package provides a lightweight message exchange interface between Python simulation scripts in CoppeliaSim and external Python applications.

Messages are represented using Python dataclasses and serialized into JSON strings. ZeroMQ (ØMQ) is used as the underlying transport layer, implementing a broker-based Publish-Subscribe (PUB/SUB) messaging pattern.

A central ZeroMQ broker routes messages between independent publishers and subscribers. This allows multiple simulation scripts and external applications to communicate without requiring direct connections between them.

## Package Structure

```text
communication/
├── __init__.py
├── messages.py
├── serializer.py
├── endpoint.py
├── publisher.py
├── subscriber.py
└── broker.py
```

## Requirements

- Python 3.12 or later.
- CoppeliaSim with Python simulation script support (when communicating from simulation scripts).
- The `dcs_world` package must be accessible to the Python interpreters running the publishers and subscribers.
- `pyzmq` for ZeroMQ communication.

## Message Definition

Messages are defined as Python dataclasses in `messages.py`.

For example, a stamped velocity command:

```python
from dcs_world.communication.messages import (
    Vector3,
    Twist,
    TwistStamped
)

cmd = TwistStamped(
    timestamp=0.0,
    twist=Twist(
        linear=Vector3(x=1.0, y=0.0, z=0.0),
        angular=Vector3(x=0.0, y=0.0, z=0.2)
    )
)
```

## Communication Architecture

The communication layer uses a central ZeroMQ broker to route messages between publishers and subscribers.

The broker uses two sockets:

- **XSUB:** Receives messages from publishers and forwards subscription requests.
- **XPUB:** Forwards messages to subscribers and receives their subscription requests.

The broker forwards messages without interpreting their contents. Serialization and deserialization are handled independently by the publishers and subscribers.

### Architecture Overview

```text
                  ZeroMQ Broker
              ┌─────────────────────┐
              │                     │
Publisher 1 ──┤                     ├── Subscriber 1
Publisher 2 ──┤    XSUB  →  XPUB    ├── Subscriber 2
Publisher 3 ──┤                     ├── Subscriber 3
              │                     │
              └─────────────────────┘
```

Publishers and subscribers can run in separate processes. They only need to connect to the broker's configured TCP endpoints.

The broker uses the following default endpoints:

| Component | Endpoint | Operation |
|---|---|---|
| Publisher | `tcp://127.0.0.1:5555` | Connect |
| Subscriber | `tcp://127.0.0.1:5556` | Connect |

The broker binds to both endpoints and routes messages and subscription events between them.

### Subscription Handshake

ZeroMQ PUB/SUB communication has a known startup limitation called the **slow-joiner problem**. When a publisher starts transmitting messages, a subscriber may not yet have completed its subscription propagation through the broker. Consequently, initial messages can be lost.

To mitigate this issue, the `Publisher` supports an optional subscription handshake.

When `handshake=True`, the publisher uses an XPUB socket instead of a PUB socket. XPUB allows the publisher to receive subscription events from the broker.

Before transmitting its first message, the publisher waits until it receives a subscription event matching its topic. Once a matching subscription is detected, the handshake is marked as complete and subsequent publications proceed normally.

The handshake sequence is:

1. The subscriber connects to the broker and subscribes to its configured topic.
2. The broker forwards the subscription request to the publisher.
3. The publisher receives the corresponding XPUB subscription event.
4. The publisher verifies that the subscription matches its topic.
5. The publisher completes the handshake and transmits the message.

The handshake is implemented entirely within the publisher and broker using XPUB subscription events. The subscriber does not require any additional handshake logic.

This mechanism mitigates initial message loss caused by subscription propagation delays. However, it does not provide end-to-end message delivery acknowledgment or guarantee that the subscriber has processed the message.

## Broker

The `Broker` component initializes the ZeroMQ proxy responsible for forwarding messages and subscription events between publishers and subscribers.

The broker uses:

- An XSUB socket bound to the publisher endpoint.
- An XPUB socket bound to the subscriber endpoint.
- `zmq.proxy()` to transparently forward messages and subscription events.

The broker must be running before publishers and subscribers establish their connections.

Start the broker using:

```bash
uv run python -m dcs_world.communication.broker
```

Once initialized, the broker remains active and forwards messages until interrupted.

## Publisher

The `Publisher` class handles message serialization and transmits the resulting payload through a ZeroMQ PUB or XPUB socket.

```python
from dcs_world.communication.publisher import Publisher
from dcs_world.communication.messages import (
    Vector3,
    Twist,
    TwistStamped
)


def sysCall_init(self):
    self.publisher = Publisher(
        topic="dcs_world.drone_1.cmd_vel",
        handshake=True
    )


def sysCall_actuation(self):

    msg = TwistStamped(
        timestamp=sim.getSimulationTime(),
        twist=Twist(
            linear=Vector3(x=1.0, y=0.0, z=0.0),
            angular=Vector3(x=0.0, y=0.0, z=0.2)
        )
    )

    self.publisher.publish(msg)
```

The publisher accepts the following parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `topic` | `str` | Required | Topic associated with published messages. |
| `handshake` | `bool` | `False` | Enables the XPUB-based subscription handshake. |
| `handshake_timeout` | `int` | `10000` | Maximum time to wait for a matching subscription, in milliseconds. |

The `publish()` method accepts a Python message object, automatically serializes it, and transmits it through the associated ZeroMQ socket.

When `handshake=False`, the publisher uses a standard PUB socket and publishes messages immediately.

When `handshake=True`, the publisher uses an XPUB socket and waits for a matching subscriber before its first publication. Once the handshake is completed, subsequent publications do not require additional waiting.

If no matching subscription is detected within the configured timeout, a `TimeoutError` is raised.

Each publisher independently creates its own ZeroMQ socket and connects to the broker's publisher endpoint.

Multiple publishers can connect to the same broker endpoint, even when running in separate processes.

## Subscriber

The `Subscriber` class receives messages through a ZeroMQ SUB socket, deserializes them into their corresponding Python dataclass, and invokes a callback when a message is received.

```python
from dcs_world.communication.subscriber import Subscriber
from dcs_world.communication.messages import TwistStamped


def on_cmd_vel(message):
    print(f"Timestamp: {message.timestamp}")
    print(f"Linear velocity: {message.twist.linear}")
    print(f"Angular velocity: {message.twist.angular}")


subscriber = Subscriber(
    topic="dcs_world.drone_1.cmd_vel",
    message_type=TwistStamped,
    callback=on_cmd_vel
)
```

The subscriber accepts the following parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `topic` | `str` | Required | Topic or topic pattern associated with messages to receive. |
| `message_type` | `type` | Required | Dataclass used to reconstruct incoming messages. |
| `callback` | `callable` | `None` | Optional function executed when a message is received. |

The callback receives the deserialized message as its argument.

### Topic Filtering

Subscribers can use wildcard patterns to receive messages from multiple topics.

For example:

```python
subscriber = Subscriber(
    topic="dcs_world.drone_*.status",
    message_type=RobotStatusMessage,
    callback=on_drone_status
)
```

This allows a single subscriber to receive status messages from multiple drones, such as:

```text
dcs_world.drone_1.status
dcs_world.drone_2.status
dcs_world.drone_3.status
```

ZeroMQ subscriptions use prefix matching. The subscriber therefore subscribes to the common prefix preceding the wildcard.

The subscriber additionally applies Python's `fnmatch` pattern matching to filter received topic names.

### Receiving Messages

The `receive()` method checks for incoming messages without blocking execution:

```python
subscriber.receive()
```

The method continuously retrieves available messages using non-blocking socket operations until no more messages are available.

Each received message is:

1. Extracted from the ZeroMQ message frames.
2. Filtered against the subscriber's topic pattern.
3. Deserialized into the specified message dataclass.
4. Passed to the registered callback, if one exists.

If no messages are available, the method immediately returns.

The method can be called periodically from a simulation callback or an external application's execution loop.

For example:

```python
while True:
    subscriber.receive()
```

Unlike implementations that process only one message per call, this implementation drains all currently available messages before returning.

## Communication Workflow

The message exchange follows this sequence:

1. The broker initializes and binds its publisher and subscriber endpoints.
2. Publishers and subscribers connect to their respective broker endpoints.
3. The subscriber establishes its topic subscription.
4. The publisher receives a Python message object.
5. The publisher serializes the message into a JSON string.
6. The serialized payload is encoded into bytes.
7. The publisher transmits the message through its ZeroMQ PUB or XPUB socket, including the associated topic.
8. The broker receives the message through its XSUB socket and forwards it through its XPUB socket.
9. The subscriber receives the message through its ZeroMQ SUB socket.
10. The subscriber decodes and deserializes the payload into the specified message dataclass.
11. The subscriber invokes its registered callback with the reconstructed message.

When the publisher uses `handshake=True`, it first waits for a matching subscription event before transmitting its initial message.

## Execution

The broker, publishers, and subscribers operate independently and can run in separate processes.

A typical execution sequence is:

1. Start the ZeroMQ broker.
2. Start external applications such as MissionControl.
3. Start CoppeliaSim and initialize its simulation scripts.

The broker must be initialized before the other components connect.

For example:

```text
Process 1: ZeroMQ Broker
Process 2: MissionControl
Process 3: CoppeliaSim - Drone 1
Process 4: CoppeliaSim - Drone 2
```

All components communicate through the broker without requiring direct connections between individual publishers and subscribers.

## Important Notes

- Publishers and subscribers must use compatible topic names to communicate.
- Topic names are included in transmitted messages and are used for subscriber filtering.
- Publishers connect to the broker's publisher endpoint.
- Subscribers connect to the broker's subscriber endpoint.
- The broker binds to the configured TCP endpoints and must be running before communication begins.
- Multiple publishers can connect to the same broker endpoint, including publishers running in separate processes.
- Multiple subscribers can connect to the same broker endpoint and independently receive matching messages.
- The broker forwards messages and subscription events without interpreting message contents.
- The implementation uses TCP over localhost by default. The endpoints can be configured to support communication across different machines.
- ZeroMQ PUB/SUB provides asynchronous communication but does not guarantee message delivery.
- Messages may be lost if subscribers are not connected or their subscriptions have not propagated when messages are published.
- The optional publisher handshake mitigates the slow-joiner problem by waiting for a matching subscription event before the first publication.
- The handshake confirms subscription propagation to the publisher; it does not guarantee that the subscriber has received or processed a message.
- The PUB/SUB pattern does not provide persistent message storage, message replay, or delivery acknowledgment.
- The subscriber's `receive()` method is non-blocking and processes all currently available messages per call.
- ZeroMQ topic subscriptions use prefix matching. The subscriber additionally supports wildcard filtering through Python's `fnmatch`.
- Publishers and subscribers manage their socket resources internally.
- Serialization and communication are separate responsibilities. The serializer does not depend on CoppeliaSim.
- Message timestamps are part of the message definition. Their reference depends on how the timestamp is generated by the message producer.