import serial
import pynmea2
import time

class GPSReader:

	def __init__(self, port="/dev/ttyUSB1", baudrate=9600):

		self.port = port
		self.baudrate = baudrate

		self.ser = serial.Serial(
			port=self.port,
			baudrate=self.baudrate,
			timeout=1
		)

		self.lat = None
		self.lon = None

		print(f"[GPS] Connected on {self.port}")

	def read_loop(self):

		while True:

			try:
				line = self.ser.readline().decode('ascii', errors='ignore')

				if line.startswith('$GPGGA') or line.startswith('$GPRMC'):

					msg = pynmea2.parse(line)

					if hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):

						self.lat = msg.latitude
						self.lon = msg.longitude

						print(f"[GPS] Lat: {self.lat} | Lon: {self.lon}")

			except Exception as e:
				print("[GPS ERROR]", e)

			time.sleep(0.2)


	def get_position(self):

		return self.lat, self.lon

