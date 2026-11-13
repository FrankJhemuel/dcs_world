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


    def wait_for_robot(self, robot_id: str, timeout: float = 30.0) -> dict:
        """Wait for a robot's initialization information."""
        
        property_name = f"signal.dcs_world.{robot_id}.init"
        
        start_time = time.monotonic()

        while time.monotonic() - start_time < timeout:

            data = self.sim.getStringProperty(
                self.sim.handle_scene,
                property_name,
                {"noError": True}
            )

            if data is not None:
                return json.loads(data)

            time.sleep(0.1)

        raise TimeoutError(
            f"Robot '{robot_id}' initialization timed out."
        )