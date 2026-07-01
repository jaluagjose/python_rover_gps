import time
import math

class HeadingEstimator:

	def __init__(self):

		self.heading = 0
		self.last_time = time.time()

	def reset(self, initial_heading = 0):

		self.heading = initial_heading

	def update_turn(self, direction, turn_rate_deg_per_sec, duration):

		#direction is left or right

		delta = turn_rate_deg_per_sec * duration

		if direction == "LEFT":
			self.heading -= delta
		elif direction == "RIGHT":
			self.heading += delta

		self.heading %= 360

		return self.heading

	def get_heading(self):

		return self.heading
