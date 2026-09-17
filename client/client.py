"""Client.py is used to connect with server.py and send msgs."""

import socket
import threading
import json
from classes.message import format_msg
from classes.exceptions import InvalidMsgType, InvalidMsgAction

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
        self.action_map = {
                "response": {
                    "get_usernames": self._handle_response
                },
                "chat": {
                    "whisper": self._handle_whisper,
                    "chat": self._handle_chat
                }
        }


        self.__temp_response = None
        self.__response_ready = threading.Event()


    @classmethod
    def from_config(cls):
        CONFIG_PATH = (
            Path(__file__).resolve().parent.parent
            / "config"
            / "server_config.json"
        )

        with open(CONFIG_PATH) as f:
            server_config = json.load(f)["client"]

        return cls(**server_config)

    def connect_host(self):
        self.socket.connect((self.HOST, self.PORT))

    def cleanup(self):
        self.socket.close()
        del self
        sys.exit(0)


    def get_usernames(self):
        msg = format_msg(msg_type="query", msg_action="get_usernames")

        self._send_to_server(msg)

        self.__response_ready.wait()

        response, self.__temp_response = self.__temp_response, None

        return response

    def send_whisper(self, data):
        msg = format_msg(msg_type = "chat", action="whisper", src=self.


    def _handle_whisper(self, msg):
        print(f"{msg["src"] -> msg["data"])

    def _handle_response(self, msg):
        self.__temp_response = msg
        self.__response_ready.set()


    def msg_handler(self, msg):

        actions = self.action_map.get(msg["msg_type"])

        if not actions:
            raise InvalidMsgType("Given msg type from host was invalid!!")

        func = actions.get(msg["action"])

        if not func:
            raise InvalidMsgAction("Given msg action from host was invalid!!")

        func(msg)



    def recive_msg(self):

        bytes = 1024
        try:
            while True:
                raw_data = self.socket.recv(bytes)
 
                if not raw_data:
                    raise ConnectionResetError


                msg = raw_data.decode()


                self.msg_handler(msg)
 

        except (ConnectionResetError, BrokenPipeError, socket.error):
            print("Connection Error from host side!")

        except (json.JSONDecodeError, TypeError):
            print("Invalid msg. Could not format msg to JSON.")


        finally:
            print("Host lost")
            self.cleanup()



    def _send_to_server(self, msg):
        self.socket.sendall(msg.encode())


