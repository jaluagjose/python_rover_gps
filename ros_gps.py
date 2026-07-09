import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix

class GPSSubscriber(Node):

	def __init__(self):

		super().__init__('gps_subscriber')

		self.lat = None
		self.lon = None

		self.create_subscription(
			NavSatFix,
			'/fix',
			self.callback,
			10
		)

		self.get_logger().info("Subscribed to /fix")

	def callback(self, msg):

		self.lat = msg.latitude
		self.lon = msg.longitude

	def get_position(self):

		return self.lat, self.lon
