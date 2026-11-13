import json
import time

from coppeliasim_zmqremoteapi_client import RemoteAPIClient

class CoppeliaClient:
    """Manage communication with a CoppeliaSim instance."""

    def __init__(self, host: str = "localhost", port: int = 23000):
        self.client = RemoteAPIClient(host=host, port=port)
        self.sim = self.client.require("sim")

    def start_simulation(self) -> None:
        self.sim.startSimulation()

    def stop_simulation(self) -> None:
        self.sim.stopSimulation()

    def get_object_handle(self, path: str) -> int:
        return self.sim.getObject(path)

    def get_object_position(self, handle: int) -> list[float]:
        return self.sim.getObjectPosition(handle, self.sim.handle_world)

    def set_object_position(
        self,
        handle: int,
        position: list[float]
    ) -> None:
        self.sim.setObjectPosition(
            handle,
            self.sim.handle_world,
            position
        )
        
    def disconnect(self):
        """Close the connection to CoppeliaSim."""
        self.client.close()