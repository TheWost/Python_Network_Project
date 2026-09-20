"""Client connection hadnler for socket communication."""

import json
import threading


class Client:
    """ARGS:
    socket: socket
    address: str
    server: Server

    Holds values esseintal for client to recive and send packets."""

    def __init__(self, client_socket, address, port, server):
        self.__client_socket = client_socket
        self.address = address
        self.port = port
        self.server = server
        self.thread: threading.Thread | None = None

    def cleanup(self):
        """Removes itself from everywhere"""
        username = self.server.address_to_username(self.address)

        self.server.remove_client(self.address)

        if username:
            self.server.remove_user(username)

        self.__client_socket.close()

    def msg_handler(self, address, msg):
        self.server.msg_handler(address, msg)

    def send_msg(self, data):
        self.__client_socket.sendall(data.encode())

    def recive_msg(self):
        """Lisitens for msg from it's connected socket"""
        bytes = 1024
        try:
            while True:
                raw_data = self.__client_socket.recv(bytes)

                if not raw_data:
                    raise ConnectionResetError

                data = raw_data.decode()
                data = json.loads(data)
                self.msg_handler(self.address, data)

        except OSError, ConnectionResetError, BrokenPipeError:
            print(f"{self.address} got disconnected!")
        finally:
            self.cleanup()
