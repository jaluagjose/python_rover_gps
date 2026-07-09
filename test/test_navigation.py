from navigation import Navigator

nav = Navigator()

#Current position
current_lat = 39.12300
current_lon = -76.54300

#Target position
target_lat = 39.12350
target_lon = -76.54250

distance = nav.get_distance(current_lat, current_lon, target_lat, target_lon)
bearing = nav.get_bearing(current_lat, current_lon, target_lat, target_lon)

print("Distance:",  distance, "meters")
print("Bearing:", bearing, "degrees")
