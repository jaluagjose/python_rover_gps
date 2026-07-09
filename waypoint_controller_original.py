#!/usr/bin/env python3

import math
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix, Imu
from geometry_msgs.msg import Twist
from transforms3d.euler import quat2euler


# ==========================
# CHANGE THIS TO YOUR TARGET
# ==========================

TARGET_LAT = 38.27944067
TARGET_LON = -76.46997533


# ==========================
# PARAMETERS
# ==========================

STOP_DISTANCE = 2.0     # meters
MAX_SPEED = 0.15         # forward speed
STEERING_GAIN = 0.01    # steering sensitivity
MAX_STEERING = 0.4      # steering limit


class WaypointController(Node):

    def __init__(self):
        super().__init__("waypoint_controller")

        self.lat = None
        self.lon = None
        self.heading = None

        self.create_subscription(
            NavSatFix,
            "/fix",
            self.gps_callback,
            10
        )

        self.create_subscription(
            Imu,
            "/imu/data",
            self.imu_callback,
            10
        )

        self.cmd_pub = self.create_publisher(
            Twist,
            "/cmd_vel",
            10
        )

    def gps_callback(self, msg):
        self.lat = msg.latitude
        self.lon = msg.longitude

    def imu_callback(self, msg):
        q = msg.orientation

        roll, pitch, yaw = quat2euler([
            q.w,
            q.x,
            q.y,
            q.z
        ])

        self.heading = (math.degrees(yaw) + 360) % 360

    def drive(self):
        if self.lat is None:
            print("Waiting for GPS...")
            return

        if self.heading is None:
            print("Waiting for IMU...")
            return

        distance = self.distance_to_target(
            self.lat,
            self.lon,
            TARGET_LAT,
            TARGET_LON
        )

        bearing = self.bearing_to_target(
            self.lat,
            self.lon,
            TARGET_LAT,
            TARGET_LON
        )

        error = bearing - self.heading

        if error > 180:
            error -= 360

        if error < -180:
            error += 360

        cmd = Twist()

        print("----------------")
        print(f"Current : {self.lat:.6f}, {self.lon:.6f}")
        print(f"Target  : {TARGET_LAT:.6f}, {TARGET_LON:.6f}")
        print(f"Distance: {distance:.2f} m")
        print(f"Bearing : {bearing:.2f}°")
        print(f"Heading : {self.heading:.2f}°")
        print(f"Error   : {error:.2f}°")

        if distance < STOP_DISTANCE:
            print("TARGET REACHED")
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0

        else:
            cmd.linear.x = MAX_SPEED

            steering = error * STEERING_GAIN
            steering = max(-MAX_STEERING, min(MAX_STEERING, steering))

            cmd.angular.z = steering

            print(f"Speed   : {cmd.linear.x:.2f}")
            print(f"Steering: {cmd.angular.z:.2f}")

        self.cmd_pub.publish(cmd)

    def distance_to_target(self, lat1, lon1, lat2, lon2):
        R = 6371000

        p1 = math.radians(lat1)
        p2 = math.radians(lat2)

        dp = math.radians(lat2 - lat1)
        dl = math.radians(lon2 - lon1)

        a = (
            math.sin(dp / 2) ** 2
            + math.cos(p1)
            * math.cos(p2)
            * math.sin(dl / 2) ** 2
        )

        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def bearing_to_target(self, lat1, lon1, lat2, lon2):
        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)

        dl = math.radians(lon2 - lon1)

        x = math.sin(dl) * math.cos(lat2)

        y = (
            math.cos(lat1)
            * math.sin(lat2)
            - math.sin(lat1)
            * math.cos(lat2)
            * math.cos(dl)
        )

        return (math.degrees(math.atan2(x, y)) + 360) % 360

    def stop(self):
        self.cmd_pub.publish(Twist())


def main():
    rclpy.init()

    node = WaypointController()

    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)
            node.drive()
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Stopping rover...")

    finally:
        node.stop()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
