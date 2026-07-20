#!/usr/bin/env python3

import sys
import time
import rclpy

sys.path.append("/home/jetson/robot_autonomy/rover_mission")

from waypoint_controller import NetworkWaypointController, STATE_SCANNING


def main():
	rclpy.init()

	node = NetworkWaypointController()

	print("----------------------------------------")
	print("Testing camera section from waypoint_controller.py")
	print("----------------------------------------")

	# Wait for camera frames and IMU heading
	start = time.time()

	while rclpy.ok() and time.time() - start < 5:
		rclpy.spin_once(node, timeout_sec=0.1)

	print("Forcing SCANNING_360 state...")

	node.start_scan()
	node.state = STATE_SCANNING

	start = time.time()

	while rclpy.ok() and time.time() - start < 20:
		rclpy.spin_once(node, timeout_sec=0.1)
		node.scanning_state()
		time.sleep(0.1)

	print("Stopping test...")

	node.stop()

	if node.video_writer is not None:
		node.video_writer.release()
		node.video_writer = None

	rclpy.shutdown()


if __name__ == "__main__":
	main()