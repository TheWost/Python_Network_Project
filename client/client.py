"""Client.py is used to connect with server.py and send msgs."""

import json
import socket
import sys
import threading
from pathlib import Path
from time import sleep

from classes.exceptions import InvalidMsgAction, InvalidMsgType, ServerDisconnection
from classes.protocol import format_msg


class Client:
    """ARGS:
    address: str
    socket.

    Holds values esseintal for client to recive and send packets."""

    def __init__(self, port, host, IPV=socket.AF_INET, PROTOCOL=socket.SOCK_STREAM):
        self.socket = socket.socket(IPV, PROTOCOL)
        self.HOST = host
        self.PORT = port
        self.thread: threading.Thread | None = None
        self.disconnected = threading.Event()
        self.action_map = {
            "response": {
                "get_usernames": self._handle_response,
                "register": self._handle_response,
            },
            "chat": {"whisper": self._handle_whisper, "chat": self._handle_chat},
            "warning": {"server_close": self._hadnle_server_close},
        }

        self.__temp_response = None
        self.__response_ready = threading.Event()

    @classmethod
    def load_from_config(cls):
        CONFIG_PATH = (
            Path(__file__).resolve().parent.parent / "configs" / "server_config.json"
        )

        with open(CONFIG_PATH) as f:
            server_config = json.load(f)["client"]

        return cls(**server_config)

    def connect_host(self):
        self.socket.connect((self.HOST, self.PORT))

    def cleanup(self):
        self.disconnected.set()
        self.socket.close()
        sys.exit(0)

    def _send_and_wait(self, msg):
        self._send_to_server(msg)

        self.__response_ready.wait()

        response, self.__temp_response = self.__temp_response, None

        self.__response_ready.clear()

        return response

    def send_register(self, username):
        msg = format_msg(msg_type="auth", action="register", data=username)

        response = self._send_and_wait(msg)

        return response

    def get_usernames(self):
        msg = format_msg(msg_type="query", action="get_usernames")

        response = self._send_and_wait(msg)

        return response["data"]

    def broadcast(self, data):
        msg = format_msg(msg_type="chat", action="group", data=data)

        self._send_to_server(msg)

    def send_whisper(self, data, dst):
        msg = format_msg(msg_type="chat", action="whisper", dst=dst, data=data)

        self._send_to_server(msg)

    def _hadnle_server_close(self, msg):
        try:
            raise ServerDisconnection(
                f"Server has disconnected. Reason: {msg['reason']} {msg['data']}"
            )
        finally:
            self.cleanup()

    def _handle_chat(self):
        return

    def _handle_whisper(self, msg):
        print(f"{msg['src']} -> {msg['data']}")

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
            while not self.disconnected.is_set():
                raw_data = self.socket.recv(bytes)

                if not raw_data:
                    raise ConnectionResetError

                msg = raw_data.decode()

                formated_msg = json.loads(msg)

                self.msg_handler(formated_msg)

        except OSError, ConnectionResetError, BrokenPipeError:
            print("Connection Error from host side!")

        except json.JSONDecodeError, TypeError:
            print("Invalid msg. Could not format msg to JSON.")

        finally:
            print("Host lost")
            self.cleanup()

    def _send_to_server(self, msg):
        self.socket.sendall(msg.encode())

    def start(self):
        self.connect_host()
        self.thread = threading.Thread(target=self.recive_msg)
        self.thread.start()


def main():
    """TESTINGS CONNECTION"""
    client = Client.load_from_config()
    client.connect_host()
    client.thread = threading.Thread(target=client.recive_msg)
    client.thread.start()
    while True:
        user = client.send_register("w123uftime2")
        print(user)
        users = client.get_usernames()
        print(users)
        sleep(20)


if __name__ == "__main__":
    main()
