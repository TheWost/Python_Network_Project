"""Client.py is used to connect with server.py and send msgs."""

import socket
import threading
import json
from classes.message import format_msg

import sys
from pathlib import Path


class Client:
    """ARGS:
        address: str
        socket.

        Holds values esseintal for client to recive and send packets."""
    def __init__(self, port, host, IPV=socket.AF_INET, PROTOCOL=socket.SOCK_STREAM):
        self.socket = socket.socket(IPV,PROTOCOL)
        self.HOST = host
        self.PORT = port
        self.thread = None


        self.__temp_response = None
        self.__response_ready = threading.Event()


    @classmetho
    def from_config(cls):
        CONFIG_PATH = (
            Path(__file__).resolve().parent.parent
            / "config"
            / "server_config.json"
        )

        with open(CONFIG_PATH) as f:
            server_config = json.load(f)["client"]

        return cls(**server_config)d

    def connect_host(self):
        self.socket.connect((self.HOST, self.PORT))
    def cleanup(self):
        self.socket.close()
        del self
        sys.exit(0)


    def get_users(self):
        msg = format_msg(msg_type="query", msg_action="get_users")

        self.send_to_server(msg)

        self.__response_ready.wait()

        response, self.__temp_response = self.__temp_response, None

        return response


    def __response_msg(self, msg):
        self.__temp_response = msg
        self.__response_ready.set()


    def msg_handler(self, msg):
        

    def recive_msg(self):

        bytes = 1024
        try:
            while True:
                raw_data = self.socket.recv(bytes)
 
                if not raw_data:
                    raise ConnectionResetError

                data = raw_data.decode()
                print(f"\r{data}\n> ", end="", flush=True)
 

        except (ConnectionResetError, BrokenPipeError, socket.error):
            print("Connection Error from host side!")

        finally:
            print("Host lost")
            self.cleanup()



    def send_to_server(self, msg):
        self.socket.sendall(msg.encode())


