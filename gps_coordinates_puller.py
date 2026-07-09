#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix


class GPSCoordinatePuller(Node):

    def __init__(self):
        super().__init__("gps_coordinate_puller")

        print("Waiting for GPS fix...")

        self.create_subscription(
            NavSatFix,
            "/fix",
            self.gps_callback,
            10
        )

    def gps_callback(self, msg):

        print("\nGPS Fix Received!")
        print(f"Latitude : {msg.latitude:.8f}")
        print(f"Longitude: {msg.longitude:.8f}")
        print(f"Altitude : {msg.altitude:.2f} m")

        # Stop after the first GPS message
        rclpy.shutdown()


def main():

    rclpy.init()

    node = GPSCoordinatePuller()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()
