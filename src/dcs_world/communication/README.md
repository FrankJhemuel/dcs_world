# Communication

The `communication` package provides a lightweight message exchange interface for communication between Python simulation scripts in CoppeliaSim.

Messages are represented using Python dataclasses and serialized into JSON strings. CoppeliaSim scene properties are used to exchange these strings between scripts.

## Package Structure

```text
communication/
├── __init__.py
├── messages.py
├── serializer.py
├── publisher.py
└── subscriber.py
```

## Requirements

- CoppeliaSim with Python simulation script support.
- The `dcs_world` package must be accessible to the Python interpreter used by CoppeliaSim.

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

The `Publisher` and `Subscriber` classes provide a simplified interface for exchanging messages through CoppeliaSim scene properties.

Each communication endpoint is associated with a topic. The topic identifies the scene property used for message exchange.

The `.signal.` prefix is automatically added to the provided topic name. Therefore, publisher and subscriber instances must use the same topic.

### Publisher

The `Publisher` class handles message serialization and writes the resulting JSON string to a CoppeliaSim scene property.

```python
from dcs_world.communication.publisher import Publisher
from dcs_world.communication.messages import (
    Vector3,
    Twist,
    TwistStamped
)


def sysCall_init():
    global sim, publisher

    sim = require("sim")

    publisher = Publisher(
        sim=sim,
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

    publisher.publish(msg)
```

The publisher requires:

- `sim`: The CoppeliaSim simulation API.
- `topic`: The topic name used to identify the scene property.

The `publish()` method accepts a Python message object and automatically serializes it before writing it to the scene property.

### Subscriber

The `Subscriber` class reads messages from a CoppeliaSim scene property, deserializes them into their corresponding Python dataclass, and invokes a callback when a new message is received.

```python
from dcs_world.communication.subscriber import Subscriber
from dcs_world.communication.messages import TwistStamped


def on_cmd_vel(message):
    print(f"Timestamp: {message.timestamp}")
    print(f"Linear velocity: {message.twist.linear}")
    print(f"Angular velocity: {message.twist.angular}")


def sysCall_init():
    global sim, subscriber

    sim = require("sim")

    subscriber = Subscriber(
        sim=sim,
        topic="dcs_world.drone_1.cmd_vel",
        message_type=TwistStamped,
        callback=on_cmd_vel
    )


def sysCall_sensing():
    subscriber.receive()
```

The subscriber requires:

- `sim`: The CoppeliaSim simulation API.
- `topic`: The topic name used to identify the scene property.
- `message_type`: The dataclass used to reconstruct incoming messages.
- `callback`: An optional function executed when a new message is received.

The callback receives the deserialized message as its argument.

A callback can also be registered or replaced after initialization using `subscribe()`:

```python
subscriber.subscribe(on_cmd_vel)
```

The `receive()` method must be called periodically, typically from a CoppeliaSim simulation callback such as `sysCall_sensing()`.

## Communication Workflow

The message exchange follows this sequence:

1. The publisher receives a Python message object.
2. The publisher serializes the message into a JSON string.
3. The publisher writes the JSON string to the corresponding scene property.
4. The subscriber periodically checks the scene property for new data.
5. The subscriber deserializes the JSON string into the specified message dataclass.
6. The subscriber invokes its registered callback with the reconstructed message.

## Important Notes

- The publisher and subscriber must use identical topic names.
- The `.signal.` prefix is automatically added to topic names.
- The `sim` API is injected into the publisher and subscriber during initialization.
- Scene properties retain their latest assigned value. Reading a property does not consume or remove it.
- The implementation provides latest-value communication, not a message queue. If a publisher writes multiple messages before a subscriber reads them, only the latest value is available.
- The subscriber detects new messages by comparing the received serialized data with the previously received data. Consequently, identical consecutive messages are not processed twice.
- The timestamp uses CoppeliaSim simulation time.
- Serialization and communication are separate responsibilities. The serializer does not depend on CoppeliaSim.
- Subscribers must be polled periodically for callbacks to be executed.