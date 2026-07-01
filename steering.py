class Steering:

	def __init__(self):

		self.TURN_THRESHOLD = 10 # degrees

	def compute_action(self, current_heading, target_bearing):

		# compute shortest angle difference (-180 to + 180)
		error = target_bearing - current_heading

		if error > 180:
			error -= 360
		elif error < -180:
			error += 360

		print(f"[STEERING] Heading error: {error:.2f}")

		#Decision Logic
		if abs(error) < self.TURN_THRESHOLD:
			return "FORWARD"

		elif error > 0:
			return "RIGHT"

		else:
			return "LEFT"
