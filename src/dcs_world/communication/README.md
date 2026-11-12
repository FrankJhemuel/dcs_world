# Communication

The `communication` package provides a lightweight message exchange interface for communication between Python simulation scripts in CoppeliaSim.

Messages are represented using Python dataclasses and serialized into JSON strings. CoppeliaSim scene properties are used to exchange these strings between scripts.

## Package Structure

```text
communication/
├── __init__.py
├── messages.py
└── serializer.py
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

## Serialization

The `serializer` module provides functions to convert between Python messages and JSON strings.

```python
from dcs_world.communication.serializer import serialize, deserialize

# Python message -> JSON string
json_message = serialize(cmd)

# JSON string -> Python message
received_cmd = deserialize(json_message, TwistStamped)
```

To generate formatted JSON:

```python
json_message = serialize(cmd, indent=4)
```

## Communication in CoppeliaSim

Each Python simulation script can publish or receive messages through CoppeliaSim scene properties.

A property is identified by its name and scope. Both scripts must use the same property name and scope.

For this example, we use:

```python
SIGNAL_NAME = "signal.dcs_world.drone_1.cmd_vel"
```

### Publisher

The publisher creates a message, serializes it, and writes the resulting JSON string to a scene property.

```python
from dcs_world.communication.messages import (
    Vector3,
    Twist,
    TwistStamped
)
from dcs_world.communication.serializer import serialize

SIGNAL_NAME = "signal.dcs_world.drone_1.cmd_vel"


def sysCall_init():
    global sim

    sim = require("sim")

    print("[Publisher] Initialized")


def sysCall_actuation():

    msg = TwistStamped(
        timestamp=sim.getSimulationTime(),
        twist=Twist(
            linear=Vector3(x=1.0, y=0.0, z=0.0),
            angular=Vector3(x=0.0, y=0.0, z=0.2)
        )
    )

    data = serialize(msg)

    sim.setStringProperty(
        sim.handle_scene,
        SIGNAL_NAME,
        data
    )
```

### Subscriber

The subscriber reads the scene property, deserializes the JSON string, and reconstructs the original Python message.

```python
from dcs_world.communication.messages import TwistStamped
from dcs_world.communication.serializer import deserialize

SIGNAL_NAME = "signal.dcs_world.drone_1.cmd_vel"


def sysCall_init():
    global sim

    sim = require("sim")

    print("[Subscriber] Initialized")


def sysCall_actuation():

    data = sim.getStringProperty(
        sim.handle_scene,
        SIGNAL_NAME,
        {"noError": True}
    )

    if data is None:
        return

    msg = deserialize(data, TwistStamped)

    print(f"Timestamp: {msg.timestamp}")
    print(f"Linear velocity: {msg.twist.linear}")
    print(f"Angular velocity: {msg.twist.angular}")
```

## Communication Workflow

The message exchange follows this sequence:

1. The publisher creates a Python message.
2. The serializer converts the message into a JSON string.
3. The publisher writes the JSON string to a scene property.
4. The subscriber reads the scene property.
5. The deserializer reconstructs the Python message.
6. The subscriber processes the received message.

## Important Notes

- The publisher and subscriber must use identical property names and scopes.
- Scene properties retain their latest assigned value. Reading a property does not consume or remove it.
- This implementation provides latest-value communication, not a message queue. If a publisher writes multiple messages before a subscriber reads them, only the latest value is available.
- The timestamp uses CoppeliaSim simulation time.
- Serialization and communication are separate operations. The serializer does not depend on CoppeliaSim.