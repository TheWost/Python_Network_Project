"""TCP Server module for accepting connections and broadcasting messages."""
import threading
import socket
from server.client import Client
from classes.exceptions import InvalidMsgType, InvalidMsgAction


class Server:
    """Class creates a socket that local machines can connect to and send msgs to"""
    def __init__(self,host="0.0.0.0", port=8000):
        self.port = port # Holds to which PORT socket will be connected to
        self.host = host # Holds...
        self.__clients = dict() # Holds key:client_address value:client_socket
        self.__users = dict()     # username -> Client
        self.server = None
        self.action_map = {
                "chat": {
                    "whisper": self.whisper,
                    "group": self.broadcast
                },
                "query" : {
                    "get_usersnames": self.get_all_clients # For now it is clients. Once login will be implemeneted. It wil lbe users
                },
                "auth" : {
                    "register": self.register
            }
        }



    def create_server(self,ipv=socket.AF_INET, protocol=socket.SOCK_STREAM):
        """Creates a socket with choosen protcol and binds it to choosen PORT with choosen IP"""
        self.server = socket.socket(ipv,protocol)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))



    def append_clients(self,client):
        """Appends client to server client list"""
        self.__clients[client.address] = client

    def get_client(self, address):
        """Returns client wit that address"""
        return self.__clients[address]

    def get_all_clients(self):
        """Returns list of all clients"""
        return self.__clients.values()

    def get_clients_count(self):
        """Returns total count of client connected to server"""
        return len(self.__clients)

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
        for client in self.get_all_clients():
            client.cleanup()


    def send_to_all_clients(self,src,data):
        """Sends msg to all clients"""
        print(f"({src}) -> {data}")

        for client in self.get_all_clients():
            client.send_msg(f"({src}) -> {data}".encode())


    def msg_handler(self, address, msg):
        """Takes msg type and action and sends it to correct function"""
        actions = self.action_map.get(msg["msg_type"])

        if not actions:
            raise InvalidMsgType(f"Given msg type from {address} was invalid")

        func = actions.get(msg["action"])

        if not func:
            raise InvalidMsgAction(f"Given msg action from {address} was invalid")

        func(address, msg)

    def register(self,address, msg):
        self.__username[self.get_client(address)] = msg["data"] # Here data will be actually username


    def whisper(self,address, msg):
        """Sends msg to choosen client"""

        self.get_client().send_msg(f"{src} -> {data}")



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
            break

        finally:
            self.cleanup()
            print("Program closed.")

