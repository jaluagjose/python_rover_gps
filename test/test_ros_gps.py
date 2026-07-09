import rclpy 
from ros_gps import GPSSubscriber

rclpy.init()

gps = GPSSubscriber()

while rclpy.ok():

	rclpy.spin_once(gps, timeout_sec=0.5)
	print("Lat:", gps.lat, "Lon:", gps.lon)
