"""Program used to connect with server.py for testing reasons"""

import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

DESTINATION_ADRESS = "127.0.0.1" # 127.0.0.1 meaning this same computer.
PORT = 5000

client.connect((DESTINATION_ADRESS,PORT))






