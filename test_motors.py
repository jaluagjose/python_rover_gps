from motors import MotorController
import time

bot = MotorController()

print("Forward")
bot.forward()
time.sleep(2)

print("Stop")
bot.stop()
time.sleep(1)

print("Left turn")
bot.turn_left()
time.sleep(1)

print("Stop")
bot.stop()
