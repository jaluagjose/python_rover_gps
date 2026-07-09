#!/usr/bin/env python3

import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class TurnTest(Node):

    def __init__(self):

        super().__init__("turn_test")

        self.pub = self.create_publisher(
            Twist,
            "/cmd_vel",
            10
        )


def main():

    rclpy.init()

    node = TurnTest()

    msg = Twist()

    # turn left
    msg.angular.z = 0.5

    start = time.time()

    while time.time() - start < 3:

        node.pub.publish(msg)

        rclpy.spin_once(node, timeout_sec=0.01)

        time.sleep(0.1)


    node.pub.publish(Twist())

    rclpy.shutdown()


if __name__ == "__main__":
    main()
