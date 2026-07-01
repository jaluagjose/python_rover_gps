import time
from Rosmaster_Lib import Rosmaster

class Motors:

	def __init__(self):

		self.bot = Rosmaster()
		self.bot.create_receive_threading()

		self.FORWARD_SPEED = 0.2
		self.TURN_SPEED = 0.3
		self.STEER_ANGLE = 0.5

	def forward(self):
		self.bot.set_car_motion(self.FORWARD_SPEED, 0, 0)

	def left(self):
		self.bot.set_car_motion(0, self.TURN_SPEED, 0)

	def right(self):
		self.bot.set_car_motion(0, -self.TURN_SPEED, 0)

	def stop(self):
		self.bot.set_car_motion(0, 0, 0)
