import socket

HOST="0.0.0.0"
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print("-" * 50)
print("Rover Mission Server")
print("-" * 50)
print(f"Listening on port {PORT}...")
print()

client, address = server.accept()

print(f"Connected to {address}")
print()

while True:

	data = client.recv(1024)

	if not data:
		print("Client disconnected.")
		break

	message = data.decode().strip()

	print(f"Received: {message}")

	try:

		latitude, longitude = message.split(",")

		latitude = float(latitude)

		longitude = float(longitude)

		print()
		print("Mission Received")
		print("---------------------")
		print(f"Latitude : {latitude}")
		print(f"Longitude: {longitude}")
		print()

	except Exception:

		print("ERROR: Invalid GPS format")
		print(":Expected:")
		print("39.12345, -76.54321")
		print()
