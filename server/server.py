"""TCP Server module for accepting connections and broadcasting messages."""
import threading
import socket
from client import Client

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



    def append_clients(self,client):
        self.clients[client.address] = client


    def accept_connection(self):
        """Lisitens for connection and if found one accepts it"""
 
        self.server.listen()
        print("listening...")

        client = Client(*self.server.accept(),self)

        print(f"{client.address[0]} has connected!")


        self.append_clients(client)


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


    def get_clients_count(self):
        return len(self.clients)


    def connection_loop(self):
        """On loop lisitens for connections and recives/send msgs to everyone"""
        self.create_server()

        try:
            while True:

                connection = threading.Thread(
                        target=self.accept_connection,
                        name=f"Connection for client number {self.get_clients_count()}"
                        )

                connection.daemon = True
                connection.start()

        except KeyboardInterrupt:
            print("KEYBAORD INTERRUPT CLOSING PROGRAM...")
            break

        finally:
            self.cleanup()
            print("Program closed.")

