"""Client connection hadnler for socket communication."""

import socket

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
