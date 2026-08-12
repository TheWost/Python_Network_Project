import socket

# IPV4 and TCP/UDP protocol
# IPV4 = socket.AF_INET
# TCP = socket.SOCK_STREAM
server = socket.socket(socket.AF_INET, SOCK_STREAM)

# 5000 - port they will send on
# "0.0.0.0" - everyone from same WIFI who will send on 5000 port

ADRES = "0.0.0.0"
PORT = 5000

server.bind((ADRES,PORT))

# lisiterns for another device
server.lisiten()


#TODO make a animation out of this -> "\, -, /, | "
print("Waiting for connection...")

# Program pauses here untill someone connects.
# We create new socket for that client.
client_socket, client_adress = server.accept()


print(f"Connection sucesfull! {client_adress} has connected!") 


