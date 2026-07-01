from mission import MissionController

target_lat = 39.12345
target_lon = -76.54321

mission = MissionController(target_lat, target_lon)
mission.run()
