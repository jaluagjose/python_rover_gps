import time
import math

class IMU:

	def __init__(self):

		#placeholder
		self.heading = 0

		print("[IMU] Initialized (placeholder driver:")

	def read_heading(self):

		#Replace this later with real sensor code

		return self.heading

	def update_fake(self):

		#Only for testing
		self.heading += 2
		self.heading %= 360
