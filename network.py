import socket

HOST = "0.0.0.0"
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))

server.listen(1)

print("Waiting for mission...")

client, address = server.accept()

print("Connected by:", address)

while True:

	data = client.recv(1024)

	if not data:
		break

	print("Received:", data.decode())
