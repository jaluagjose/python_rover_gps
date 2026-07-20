import socket
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix

from navigation import Navigator
from motors import Motors


# ----------------------------
# ROS GPS Subscriber
# ----------------------------
class GPS(Node):

    def __init__(self):

        super().__init__('gps_node')

        self.lat = None
        self.lon = None

        self.create_subscription(
            NavSatFix,
            '/fix',
            self.callback,
            10
        )

    def callback(self, msg):

        self.lat = msg.latitude
        self.lon = msg.longitude

    def get(self):

        return self.lat, self.lon


# ----------------------------
# Receive target from laptop
# ----------------------------
def get_target():

    server = socket.socket()
    server.bind(("0.0.0.0", 5000))
    server.listen(1)

    print("[NETWORK] Waiting for target GPS...")

    client, addr = server.accept()

    data = client.recv(1024).decode().strip()
    lat, lon = data.split(",")

    print(f"[NETWORK] Received target from {addr}")

    return float(lat), float(lon)


# ----------------------------
# MAIN AUTONOMOUS LOOP
# ----------------------------
def main():

    rclpy.init()

    gps = GPS()
    nav = Navigator()
    motors = Motors()

    target_lat, target_lon = get_target()

    print("[MISSION] Target locked!")
    print(target_lat, target_lon)

    TARGET_RADIUS = 2.0

    try:

        while rclpy.ok():

            rclpy.spin_once(gps, timeout_sec=0.1)

            current = gps.get()

            if current[0] is None:
                print("[MISSION] Waiting for GPS lock...")
                continue

            lat, lon = current

            distance = nav.get_distance(lat, lon, target_lat, target_lon)
            bearing = nav.get_bearing(lat, lon, target_lat, target_lon)

            print("--------------------------------")
            print(f"Distance: {distance:.2f} m")
            print(f"Bearing : {bearing:.2f}")

            if distance < TARGET_RADIUS:

                print("[MISSION] Target reached!")

                motors.stop()

                break

            # SIMPLE TEST BEHAVIOR (no steering yet)
            motors.forward()

            time.sleep(0.5)

    except KeyboardInterrupt:

        print("Stopping...")

    finally:

        motors.stop()
        rclpy.shutdown()


if __name__ == "__main__":

    main()
