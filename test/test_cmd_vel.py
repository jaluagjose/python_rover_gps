#!/usr/bin/env python3

import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class CmdVelTest(Node):

    def __init__(self):

        super().__init__("cmd_vel_test")

        self.publisher = self.create_publisher(
            Twist,
            "/cmd_vel",
            10
        )


    def send_forward(self):

        msg = Twist()

        # forward velocity
        msg.linear.x = 0.2

        # no turning
        msg.angular.z = 0.0

        self.publisher.publish(msg)


    def stop(self):

        msg = Twist()

        msg.linear.x = 0.0
        msg.angular.z = 0.0

        self.publisher.publish(msg)



def main():

    rclpy.init()

    node = CmdVelTest()

    print("Moving forward for 5 seconds")

    start = time.time()

    try:

        while time.time() - start < 5:

            node.send_forward()

            rclpy.spin_once(
                node,
                timeout_sec=0.01
            )

            # publish at 10Hz
            time.sleep(0.1)


    except KeyboardInterrupt:
        pass


    finally:

        node.stop()

        rclpy.shutdown()


if __name__ == "__main__":
    main()
