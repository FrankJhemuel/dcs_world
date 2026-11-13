from .serializer import deserialize


class Subscriber:
    def __init__(self, sim, topic: str, message_type, callback=None):
        self.sim = sim
        self.topic = "signal." + topic
        self.message_type = message_type
        self.callback = callback
        self.last_message = None

    def subscribe(self, callback):
        self.callback = callback

    def receive(self):
        data = self.sim.getStringProperty(
            self.sim.handle_scene,
            self.topic,
            {"noError": True}
        )

        if data is None or data == self.last_message:
            return

        self.last_message = data

        message = deserialize(data, self.message_type)

        if self.callback is not None:
            self.callback(message)