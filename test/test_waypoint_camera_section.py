
#!/usr/bin/env python3

import os
import sys
import time

import cv2
import rclpy
from geometry_msgs.msg import Twist


PROJECT_DIR = "/home/jetson/robot_autonomy/rover_mission"
VIDEO_DIR = os.path.join(PROJECT_DIR, "videos")

sys.path.insert(0, PROJECT_DIR)

from waypoint_controller import NetworkWaypointController


CAMERA_WAIT_SECONDS = 10.0
IMU_WAIT_SECONDS = 10.0
MAX_SCAN_SECONDS = 60.0

VIDEO_FPS = 20.0

SCAN_SPEED = 0.10
SCAN_STEERING = 0.40


def normalize_heading_change(current_heading, previous_heading):
	change = current_heading - previous_heading

	if change > 180:
		change -= 360

	elif change < -180:
		change += 360

	return change


def main():
	os.makedirs(VIDEO_DIR, exist_ok=True)

	rclpy.init()

	node = NetworkWaypointController()
	video_writer = None
	video_path = None

	try:
		print("----------------------------------------")
		print("Waypoint camera and movement test")
		print("----------------------------------------")
		print("WARNING: The rover will move in a circle.")
		print("Use a large, clear testing area.")
		print("Press Ctrl+C for an emergency stop.")
		print("----------------------------------------")

		# Wait for the waypoint controller's camera callback
		print("Waiting for color camera frame...")

		wait_start = time.time()

		while rclpy.ok() and node.latest_frame is None:
			rclpy.spin_once(node, timeout_sec=0.1)

			if time.time() - wait_start >= CAMERA_WAIT_SECONDS:
				print("ERROR: No color camera frame received.")
				print("Make sure waypoint_controller.py subscribes to:")
				print("/camera/color/image_raw")
				return

		print("Camera frame received.")

		# Wait for the waypoint controller's IMU callback
		print("Waiting for IMU heading...")

		wait_start = time.time()

		while rclpy.ok() and node.heading is None:
			rclpy.spin_once(node, timeout_sec=0.1)

			if time.time() - wait_start >= IMU_WAIT_SECONDS:
				print("ERROR: No IMU heading received.")
				print("Make sure /imu/data is publishing.")
				return

		print(f"Initial heading: {node.heading:.2f} degrees")

		frame = node.latest_frame
		height, width = frame.shape[:2]

		timestamp = time.strftime("%Y%m%d_%H%M%S")

		video_path = os.path.join(
			VIDEO_DIR,
			f"waypoint_scan_test_{timestamp}.mp4"
		)

		fourcc = cv2.VideoWriter_fourcc(*"mp4v")

		video_writer = cv2.VideoWriter(
			video_path,
			fourcc,
			VIDEO_FPS,
			(width, height)
		)

		if not video_writer.isOpened():
			print("ERROR: VideoWriter failed to open.")
			print(f"Attempted path: {video_path}")
			return

		print("----------------------------------------")
		print("VideoWriter opened successfully.")
		print(f"Saving video to: {video_path}")
		print("Starting rover movement...")
		print("----------------------------------------")

		previous_heading = node.heading
		total_rotation = 0.0
		frames_written = 0

		scan_start_time = time.time()
		frame_delay = 1.0 / VIDEO_FPS

		while rclpy.ok() and total_rotation < 360.0:
			loop_start = time.time()

			rclpy.spin_once(node, timeout_sec=0.01)

			# Write the newest frame from waypoint_controller.py
			if node.latest_frame is not None:
				current_frame = node.latest_frame

				if (
					current_frame.shape[1] != width
					or current_frame.shape[0] != height
				):
					current_frame = cv2.resize(
						current_frame,
						(width, height)
					)

				video_writer.write(current_frame)
				frames_written += 1

			# Track total heading change
			if node.heading is not None:
				change = normalize_heading_change(
					node.heading,
					previous_heading
				)

				total_rotation += abs(change)
				previous_heading = node.heading

			# Ackermann rover must move forward to steer
			cmd = Twist()
			cmd.linear.x = SCAN_SPEED
			cmd.angular.z = SCAN_STEERING

			node.cmd_pub.publish(cmd)

			print(
				f"\rTurned: {total_rotation:.1f}/360.0 degrees | "
				f"Frames: {frames_written}",
				end="",
				flush=True
			)

			if time.time() - scan_start_time >= MAX_SCAN_SECONDS:
				print()
				print("SAFETY TIMEOUT: Scan exceeded 60 seconds.")
				break

			elapsed = time.time() - loop_start
			sleep_time = frame_delay - elapsed

			if sleep_time > 0:
				time.sleep(sleep_time)

		print()

		node.stop()

		video_writer.release()
		video_writer = None

		print("----------------------------------------")
		print("Rover stopped.")
		print(f"Total rotation: {total_rotation:.2f} degrees")
		print(f"Frames written: {frames_written}")

		if os.path.exists(video_path):
			file_size = os.path.getsize(video_path)

			print("Video saved successfully.")
			print(f"Video path: {video_path}")
			print(f"Video size: {file_size} bytes")

			if file_size == 0:
				print("WARNING: The file exists but is empty.")

		else:
			print("ERROR: The video file was not created.")

		print("----------------------------------------")

	except KeyboardInterrupt:
		print("\nEmergency stop requested.")

	except Exception as error:
		print(f"\nTest error: {error}")

	finally:
		node.stop()

		if video_writer is not None:
			video_writer.release()

		node.destroy_node()

		if rclpy.ok():
			rclpy.shutdown()

		print("Cleanup complete. Rover stopped.")


if __name__ == "__main__":
	main()
