# Communication

The `communication` package provides a lightweight message exchange interface for communication between Python simulation scripts in CoppeliaSim and external Python applications.

Messages are represented using Python dataclasses and serialized into JSON strings. ZeroMQ (ØMQ) is used as the underlying transport layer, implementing a brokerless Publish-Subscribe (PUB/SUB) messaging pattern.

## Package Structure

```text
communication/
├── __init__.py
├── messages.py
├── serializer.py
├── endpoint.py
├── publisher.py
└── subscriber.py
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

## Communication

The `Publisher` and `Subscriber` classes provide a simplified interface for exchanging messages through ZeroMQ sockets.

Communication is organized around topics. Each message is associated with a topic that identifies the type or destination of the information being exchanged.

Publishers send messages through PUB sockets, while subscribers receive messages through SUB sockets.

The communication layer automatically determines the TCP endpoint associated with a topic. Port configuration is handled internally and does not need to be specified when creating publishers or subscribers.

### Publisher

The `Publisher` class handles message serialization and transmits the resulting payload through a ZeroMQ PUB socket.

```python
from dcs_world.communication.publisher import Publisher
from dcs_world.communication.messages import (
    Vector3,
    Twist,
    TwistStamped
)


def sysCall_init():
    self.publisher = Publisher(
        topic="dcs_world.drone_1.cmd_vel"
    )


def sysCall_actuation():

    msg = TwistStamped(
        timestamp=sim.getSimulationTime(),
        twist=Twist(
            linear=Vector3(x=1.0, y=0.0, z=0.0),
            angular=Vector3(x=0.0, y=0.0, z=0.2)
        )
    )

    self.publisher.publish(msg)
```

The publisher requires:

- `topic`: The topic associated with the published messages.

The `publish()` method accepts a Python message object, automatically serializes it, and transmits it through the associated ZeroMQ socket.

Each publisher independently binds to the endpoint associated with its topic.

### Subscriber

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

The subscriber requires:

- `topic`: The topic associated with the messages to receive.
- `message_type`: The dataclass used to reconstruct incoming messages.
- `callback`: An optional function executed when a message is received.

The callback receives the deserialized message as its argument.

A callback can also be registered or replaced after initialization using `subscribe()`:

```python
subscriber.subscribe(on_cmd_vel)
```

The `receive()` method checks for incoming messages without blocking execution:

```python
subscriber.receive()
```

If a message is available, it is processed and passed to the registered callback. Otherwise, the method immediately returns.

The method can be called periodically from a simulation callback or an external application's execution loop.

## Communication Workflow

The message exchange follows this sequence:

1. The publisher receives a Python message object.
2. The publisher serializes the message into a JSON string.
3. The serialized payload is encoded into bytes.
4. The publisher transmits the payload through its ZeroMQ PUB socket, associated with the specified topic.
5. The subscriber receives the message through its ZeroMQ SUB socket.
6. The subscriber decodes and deserializes the payload into the specified message dataclass.
7. The subscriber invokes its registered callback with the reconstructed message.

## Important Notes

- Publishers and subscribers must use identical topic names to communicate.
- TCP endpoints and ports are determined internally based on the topic name.
- Each publisher binds to its own endpoint. Multiple publishers must use different topics to avoid endpoint conflicts.
- Multiple subscribers can connect to the same publisher endpoint.
- The implementation is brokerless. Publishers and subscribers communicate directly without requiring an intermediate message broker.
- The implementation uses TCP over localhost by default.
- ZeroMQ PUB/SUB provides asynchronous communication but does not guarantee message delivery. Messages may be lost if subscribers are not connected or ready when messages are published.
- The PUB/SUB pattern does not provide persistent message storage or message replay.
- The subscriber's `receive()` method is non-blocking and processes at most one message per call.
- ZeroMQ topic subscriptions use prefix matching. The subscriber additionally checks the received topic for an exact match.
- Publishers and subscribers manage their socket resources internally.
- Serialization and communication are separate responsibilities. The serializer does not depend on CoppeliaSim.
- Message timestamps are part of the message definition. Their reference depends on how the timestamp is generated by the message producer.