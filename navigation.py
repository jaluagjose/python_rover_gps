import math

class Navigator:

	def __init__(self):

		self.EARTH_RADIUS = 6371000

	#Distance between 2 GPS points
	def get_distance(self, lat1, lon1, lat2, lon2):

		lat1 = math.radians(lat1)
		lat2 = math.radians(lat2)
		lon1 = math.radians(lon1)
		lon2 = math.radians(lon2)

		dlat = lat2 - lat1
		dlon = lon2 - lon1

		a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
		c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

		distance = self.EARTH_RADIUS * c

		return distance

	# Bearing (directional angle)
	def get_bearing(self, lat1, lon1, lat2, lon2):

		lat1 = math.radians(lat1)
		lat2 = math.radians(lat2)
		dlon = math.radians(lon2 - lon1)

		x = math.sin(dlon) * math.cos(lat2)
		y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

		bearing = math.atan2(x, y)

		bearing = math.degrees(bearing)

		# convert to 0-360
		bearing = (bearing + 360) % 360

		return bearing
