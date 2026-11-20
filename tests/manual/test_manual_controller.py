import time
import threading
import sys
import termios
import tty

from pynput import keyboard

from dcs_world.communication import Publisher
from dcs_world.geometry import Twist


TOPIC = "drone_1.cmd_vel"
FREQUENCY = 10.0

LINEAR_SPEED = 0.1
YAW_SPEED = 0.3


class ManualController:

    def __init__(self):
        self.publisher = Publisher(topic=TOPIC)

        self.pressed_keys = set()
        self.lock = threading.Lock()
        self.running = True

    def on_press(self, key):
        if key == keyboard.Key.esc:
            self.running = False
            return False

        try:
            char = key.char.lower()
        except AttributeError:
            return

        if char == "q":
            self.running = False
            return False

        with self.lock:
            self.pressed_keys.add(char)

    def on_release(self, key):
        try:
            char = key.char.lower()
        except AttributeError:
            return

        with self.lock:
            self.pressed_keys.discard(char)

    def get_velocity(self):
        with self.lock:
            keys = self.pressed_keys.copy()

        vx = 0.0
        vy = 0.0
        wz = 0.0

        # Linear velocity
        if "w" in keys:
            vx += LINEAR_SPEED
        if "s" in keys:
            vx -= LINEAR_SPEED

        if "a" in keys:
            vy += LINEAR_SPEED
        if "d" in keys:
            vy -= LINEAR_SPEED

        # Angular velocity (yaw)
        if "e" in keys:
            wz += YAW_SPEED
        if "r" in keys:
            wz -= YAW_SPEED

        return Twist(
            linear=[vx, vy, 0.0],
            angular=[0.0, 0.0, wz]
        )

    def run(self):
        listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        print("\n=== Drone Manual Controller ===")
        print("W/S : Forward / Backward")
        print("A/D : Left / Right")
        print("E/R : Rotate yaw")
        print("Q/ESC : Exit")
        print("\nHold keys to move. Release to stop.\n")

        try:
            tty.setcbreak(fd)
            listener.start()

            period = 1.0 / FREQUENCY

            while self.running:
                loop_start = time.perf_counter()

                self.publisher.publish(self.get_velocity())

                elapsed = time.perf_counter() - loop_start
                remaining = period - elapsed

                if remaining > 0:
                    time.sleep(remaining)

        except KeyboardInterrupt:
            pass

        finally:
            self.running = False
            listener.stop()

            self.publisher.publish(
                Twist(
                    linear=[0.0, 0.0, 0.0],
                    angular=[0.0, 0.0, 0.0]
                )
            )

            self.publisher.close()

            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

            print("\nManual controller stopped.")

def main():
    ManualController().run()


if __name__ == "__main__":
    main()