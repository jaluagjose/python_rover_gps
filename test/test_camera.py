#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


class CameraTest(Node):

	def __init__(self):
		super().__init__("camera_test")

		self.bridge = CvBridge()
		self.count = 0

		self.create_subscription(
			Image,
			"/camera/color/image_raw",
			self.camera_callback,
			10
		)

		print("Listening to /camera/color/image_raw...")

	def camera_callback(self, msg):
		try:
			frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")

			filename = f"ros_camera_test_{self.count:02d}.jpg"

			cv2.imwrite(filename, frame)

			print(f"Saved {filename}")

			self.count += 1

			if self.count >= 10:
				rclpy.shutdown()

		except Exception as e:
			print(f"Camera callback error: {e}")


def main():
	rclpy.init()
	node = CameraTest()
	rclpy.spin(node)


if __name__ == "__main__":
	main()