# IMPORANT NOTE:
# This code dosen't have exit program. It will run forever untill program will get KeyInterupted/Closed. Threads won't close automaticly, python and linux will close them after a 1 min after closing program.

#TODO
# Add Try/except/finally. Inside finally when code gets closed terminate all theards
# When user gets disconnected/leaves add code that will detect that and remove him from chat

#FUTURE
# Fix terminal issue with typing
# Add whisper/private chat
# Log chat like discord does ;)
# Add command usage (os.system())




import threading
import socket
import json

class Client:
    """ARGS:
        socket: socket
        address: str
        server: Server

        Holds values esseintal for client to recive and send packets."""
    def __init__(self,client_socket,address, server):
        self.client_socket = client_socket
        self.address = address
        self.thread = None
        self.server = server
 
    def cleanup(self):
        """Removes itself from everywhere and deletes itself"""
        self.server.clients.pop(self.address, 0)
        self.client_socket.close()
        del self

    def recive_msg(self):
        """Lisitens for msg from it's connected socket"""
        bytes = 1024
        try:
            while True:
                raw_data = self.client_socket.recv(bytes)

                if not raw_data:
                    raise ConnectionResetError                

                data = raw_data.decode()
                self.server.send_to_all_clients(self.address,data)

        except (ConnectionResetError, BrokenPipeError, socket.error):
            print(f"{self.address} got disconnected!")
        finally:
            self.cleanup()



class Server:
    """Class creates a socket that local machines can connect to and send msgs to"""
    def __init__(self,host="0.0.0.0", port=8000):
        self.port = port # Holds to which PORT socket will be connected to
        self.host = host # Holds...
        self.clients = dict() # Holds key:client_address value:client_socket
        self.server = None

    def create_server(self,ipv=socket.AF_INET, protocol=socket.SOCK_STREAM):
        """Creates a socket with choosen protcol and binds it to choosen PORT with choosen IP"""
        self.server = socket.socket(ipv,protocol)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))

    def accept_connection(self):
        """Lisitens for connection and if found one accepts it and returns client information"""
        
        self.server.listen()
        print("Lisiting...")

        client = Client(*self.server.accept(),self)

        print(f"{client.address[0]} has connected!")

        return client






    def cleanup(self):
        """Closes up sockets and clients"""
        self.server.close()
        for client in self.clients.values():
            client.cleanup()


    def send_to_all_clients(self,address,data):
        """Sends msg to all clients"""
        print(f"({address}) -> {data}")
        for client in self.clients.values():
            client.client_socket.sendall(f"({address}) -> {data}".encode())


    def connection_loop(self):
        """On loop lisitens for connections and recives/send msgs to everyone"""
        self.create_server()

        try:
            while True:

                client = self.accept_connection() # Adress returns tuple (IP,PORT)

                client.thread = threading.Thread(
                        target=client.recive_msg,
                        name=f"Thread{client.address[0]}:{client.address[1]}")

                self.clients[client.address] = client

                client.thread.daemon = True
                client.thread.start()
        except KeyboardInterrupt:
            print("KEYBAORD INTERRUPT CLOSING PROGRAM...")
        
        finally:
            self.cleanup()
            print("Program closed.")


def main():
    """Runs program"""
    with open("server_config.json", encoding="utf-8") as f:
        server_config = json.load(f)["server"]

    Server(**server_config).connection_loop()



if __name__ == "__main__":
    main()
