from .serializer import serialize


class Publisher:
    def __init__(self, sim, topic: str):
        self.sim = sim
        self.topic = "signal." + topic

    def publish(self, message):
        data = serialize(message)

        self.sim.setStringProperty(
            self.sim.handle_scene,
            self.topic,
            data
        )