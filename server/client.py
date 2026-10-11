"""Client connection hadnler for socket communication."""

import json
import socket
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
        self.username = None
        self.key = (address, port)
        self.server = server
        self.thread: threading.Thread | None = None

    def cleanup(self):
        """Removes itself from everywhere"""

        print(self.key)
        print(self.username)

        print(self.server.get_client(self.key))
        print(self.server.get_user(self.username))

        self.server.remove_client(self.key)

        if self.username:
            self.server.remove_user(self.username)

        try:
            self.__client_socket.shutdown(socket.SHUT_RDWR)  # RDWR means READ/WRITE
        except OSError:
            pass
        finally:
            self.__client_socket.close()

    def msg_handler(self, address, msg):
        self.server.msg_handler(address, msg)

    def send_msg(self, data: str):
        data += "\n"  # With this msg must end to know whole msg has been sent.
        self.__client_socket.sendall(data.encode())

    def recive_msg(self):
        """Lisitens for msg from it's connected socket"""
        reader = self.__client_socket.makefile("r", encoding="utf-8")

        try:
            while True:
                raw_data = reader.readline()

                if not raw_data:
                    raise ConnectionResetError

                data = json.loads(raw_data)
                print(data)

                self.msg_handler(self, data)

        except OSError, ConnectionResetError, BrokenPipeError:
            print(f"{self.address} got disconnected!")

        finally:
            self.cleanup()
