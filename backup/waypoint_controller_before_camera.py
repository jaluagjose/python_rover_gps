#!/usr/bin/env python3

import math
import time
import socket
import threading

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix, Imu
from geometry_msgs.msg import Twist
from transforms3d.euler import quat2euler


HOST = "0.0.0.0"
PORT = 5000

STOP_DISTANCE = 2.0
MAX_SPEED = 0.15
STEERING_GAIN = 0.01
MAX_STEERING = 0.40

STATE_WAITING = "WAITING_FOR_TARGET"
STATE_NAVIGATING = "NAVIGATING_TO_TARGET"
STATE_TARGET_REACHED = "TARGET_REACHED"
STATE_RETURNING = "RETURNING_HOME"
STATE_HOME_REACHED = "HOME_REACHED"


class NetworkWaypointController(Node):

	def __init__(self):
		super().__init__("network_waypoint_controller")

		self.state = STATE_WAITING

		self.lat = None
		self.lon = None
		self.heading = None

		self.target_lat = None
		self.target_lon = None

		self.home_lat = None
		self.home_lon = None

		self.last_distance = None
		self.bad_distance_count = 0

		self.printed_waiting_target = False
		self.printed_waiting_gps = False
		self.printed_waiting_imu = False

		self.create_subscription(NavSatFix, "/fix", self.gps_callback, 10)
		self.create_subscription(Imu, "/imu/data", self.imu_callback, 10)

		self.cmd_pub = self.create_publisher(Twist, "/cmd_vel", 10)

		thread = threading.Thread(target=self.network_server, daemon=True)
		thread.start()

	def gps_callback(self, msg):
		self.lat = msg.latitude
		self.lon = msg.longitude

		#Adds function to determine what is "home" coordinates
		if self.home_lat is None and self.home_lon is None:
			if not math.isnan(self.lat) and not math.isnan(self.lon):
				self.home_lat = self.lat
				self.home_lon = self.lon
				print("Home GPS saved:")
				print(f"Home lat: {self.home_lat}")
				print(f"Home lon: {self.home_lon}")

	def imu_callback(self, msg):
		q = msg.orientation

		roll, pitch, yaw = quat2euler([
			q.w,
			q.x,
			q.y,
			q.z
		])

		self.heading = (math.degrees(yaw) + 360) % 360

	def network_server(self):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server.bind((HOST, PORT))
		server.listen(1)

		print("----------------------------------------")
		print(f"Waiting for target GPS on port {PORT}...")
		print("----------------------------------------")

		while True:
			client, addr = server.accept()
			data = client.recv(1024).decode().strip()

			try:
				lat, lon = data.split(",")

				self.target_lat = float(lat)
				self.target_lon = float(lon)

				self.last_distance = None
				self.bad_distance_count = 0

				self.printed_waiting_target = False
				self.printed_waiting_gps = False
				self.printed_waiting_imu = False

				self.state = STATE_NAVIGATING

				print("----------------------------------------")
				print(f"Connected by {addr}")
				print("New target received:")
				print(f"Target lat: {self.target_lat}")
				print(f"Target lon: {self.target_lon}")
				print(f"State: {STATE_NAVIGATING}")

			except Exception:
				print("Invalid target format.")
				print("Expected format: 38.279480,-76.470100")

			client.close()

	def stop(self):
		self.cmd_pub.publish(Twist())

	def loop(self):
		if self.state == STATE_WAITING:
			self.waiting_for_target_state()

		elif self.state == STATE_NAVIGATING:
			self.navigating_state("TARGET")
		
		elif self.state == STATE_RETURNING:
			self.navigating_state("HOME")
		
		elif self.state == STATE_HOME_REACHED:
			self.home_reached_state()

		elif self.state == STATE_TARGET_REACHED:
			self.target_reached_state()

	def waiting_for_target_state(self):
		self.stop()

		if not self.printed_waiting_target:
			print(f"State: " + STATE_WAITING)
			print("Waiting for target from laptop...")
			self.printed_waiting_target = True

	def target_reached_state(self):
		self.stop()

		print(f"State: {STATE_TARGET_REACHED}")
		print("Target Reached.")

		self.last_distance = None
		self.bad_distance_count = 0

		print(f"State: {STATE_RETURNING}")
		print("Returning home...")

		self.state = STATE_RETURNING

	def home_reached_state(self):
		self.stop()

		print(f"State: " + STATE_HOME_REACHED)
		print("Mission complete. Waiting for next target.")

		self.state = STATE_WAITING

		self.target_lat = None
		self.target_lon = None
		
		self.last_distance = None
		self.bad_distance_count = 0

		self.printed_waiting_target = False
		self.printed_waiting_gps = False
		self.printed_waiting_imu = False

	def navigating_state(self, destination):
		if destination == "TARGET":
			dest_lat = self.target_lat
			dest_lon = self.target_lon

			if dest_lat is None or dest_lon is None:
				self.state = STATE_WAITING
				self.printed_waiting_target = False
				self.printed_waiting_gps = False
				self.printed_waiting_imu = False

				return
			
			
		else: 
			dest_lat = self.home_lat
			dest_lon = self.home_lon

			if dest_lat is None or dest_lon is None:
				print("Home GPS not saved yet. Stopping.")
				self.stop()
				return

		if self.lat is None or self.lon is None:
			if not self.printed_waiting_gps:
				print("Waiting for GPS...")
				self.printed_waiting_gps = True

			self.stop()
			return

		if math.isnan(self.lat) or math.isnan(self.lon):
			if not self.printed_waiting_gps:
				print("GPS invalid. Waiting for GPS fix...")
				self.printed_waiting_gps = True

			self.stop()
			return

		if self.heading is None:
			if not self.printed_waiting_imu:
				print("Waiting for IMU...")
				self.printed_waiting_imu = True

			self.stop()
			return
		
		self.printed_waiting_gps = False
		self.printed_waiting_imu = False

		distance = self.distance_to_target(
			self.lat,
			self.lon,
			dest_lat,
			dest_lon
		)

		bearing = self.bearing_to_target(
			self.lat,
			self.lon,
			dest_lat,
			dest_lon
		)

		if math.isnan(distance) or math.isnan(bearing):
			print("Navigation invalid. Stopping.")
			self.stop()
			return

		if self.last_distance is not None:
			if distance > self.last_distance + 0.5:
				self.bad_distance_count += 1
			else:
				self.bad_distance_count = 0

		self.last_distance = distance

		if self.bad_distance_count >= 5:
			print("Distance getting worse. Stopping.")
			self.stop()

			self.state = STATE_WAITING

			self.target_lat = None
			self.target_lon = None

			self.last_distance = None
			self.bad_distance_count = 0

			self.printed_waiting_target = False
			self.printed_waiting_gps = False
			self.printed_waiting_imu = False

			return

		error = bearing - self.heading

		if error > 180:
			error -= 360

		if error < -180:
			error += 360

		print("----------------------------------------")
		print(f"State   : {self.state}")
		print(f"Current : {self.lat:.6f}, {self.lon:.6f}")
		print(f"Target  : {dest_lat:.6f}, {dest_lon:.6f}")
		print(f"Distance: {distance:.2f} m")
		print(f"Bearing : {bearing:.2f}°")
		print(f"Heading : {self.heading:.2f}°")
		print(f"Error   : {error:.2f}°")

		if distance <= STOP_DISTANCE:
			self.stop()

			if destination == "TARGET":
				print("TARGET REACHED")
				self.state = STATE_TARGET_REACHED
			else:
				print("HOME REACHED")
				self.state = STATE_HOME_REACHED


			return

		steering = error * STEERING_GAIN
		steering = max(-MAX_STEERING, min(MAX_STEERING, steering))

		cmd = Twist()
		cmd.linear.x = MAX_SPEED
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

		return R * 2 * math.atan2(
			math.sqrt(a),
			math.sqrt(1 - a)
		)

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


def main():
	rclpy.init()

	node = NetworkWaypointController()

	try:
		while rclpy.ok():
			rclpy.spin_once(node, timeout_sec=0.1)
			node.loop()
			time.sleep(0.1)

	except KeyboardInterrupt:
		print("\nStopping rover...")

	finally:
		node.stop()
		rclpy.shutdown()


if __name__ == "__main__":
	main()
