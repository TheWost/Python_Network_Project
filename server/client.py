"""Client connection hadnler for socket communication."""

import json
import threading


class Client:
    """ARGS:
    socket: socket
    address: str
    server: Server

    Holds values esseintal for client to recive and send packets."""

    def __init__(self, client_socket, address, server):
        self.__client_socket = client_socket
        self.address = address
        self.server = server
        self.thread: threading.Thread | None = None

    def cleanup(self):
        """Removes itself from everywhere and deletes itself"""
        self.server.clients.pop(self.address, 0)
        self.__client_socket.close()
        del self

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

        except (OSError, ConnectionResetError, BrokenPipeError):
            print(f"{self.address} got disconnected!")
        finally:
            self.cleanup()
