from steering import Steering

steer = Steering()

current_heading = 45 # where rover is facing
target_bearing = 90 # direction to target GPS

action = steer.compute_action(current_heading, target_bearing)

print("Action:", action)
