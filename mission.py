import time

from gps import GPSReader
from navigation import Navigator
from steering import Steering
from motors import Motors
from imu import IMU

class MissionController:

	def __init__(self, target_lat, target_lon):

		self.gps = GPSReader("/dev/ttyUSB1", 9600)
		self.nav = Navigator()
		self.steer = Steering()
		self.motors = Motors()

		self.target_lat = target_lat
		self.target_lon = target_lon

		self.TARGET_RADIUS = 2.0 # meters

		self.imu = IMU()

	def run(self):

		print("[MISSION] Starting autonomy loop...")

		while True:

			current_lat, current_lon = self.gps.get_position()

			if current_lat is None:
				print("[MISSION] Waiting for GPS lock...")
				time.sleep(1)
				continue

			# Step 1: compute navigation
			distance = self.nav.get_distance(
				current_lat, current_lon,
				self.target_lat, self.target_lon
			)

			bearing = self.nav.get_bearing(
				current_lat, current_lon,
				self.target_lat, self.target_lon
			)

			print(f"[MISSION] Distance: {distance:.2f} m | Bearing: {bearing:.2f}")

			# Step 2: arrival check
			if distance < self.TARGET_RADIUS:
				print("[MISSION] Target reached!")
				self.motors.stop()
				break

			# Step 3: CURRENT HEADING
			current_heading = self.motors.heading_estimator.get_heading() #replace later with IMU

			# Step 4: steering decision
			action = self.steer.compute_action(current_heading, bearing)

			# Step 5: REAL MOTOR CONTROL
			if action == "FORWARD":
				self.motors.forward()

			elif action == "LEFT":
				self.motors.left()

			elif action == "RIGHT":
				self.motors.right()

			time.sleep(0.5)
