from Rosmaster_Lib import Rosmaster
import time

bot = Rosmaster()
bot.create_receive_threading()

print("[INFO] Sniffing raw Rosmaster data...")

while True:

    try:
        # Try accessing internal buffer (common hidden attribute patterns)
        if hasattr(bot, "recv_data"):

            print("recv_data:", bot.recv_data)

        elif hasattr(bot, "data"):

            print("data:", bot.data)

        elif hasattr(bot, "uart_data"):

            print("uart_data:", bot.uart_data)

        else:
            print("[INFO] No exposed buffer fields found")

    except Exception as e:
        print("[ERROR]", e)

    time.sleep(0.2)
