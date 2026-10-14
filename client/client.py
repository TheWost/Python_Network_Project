"""Client.py is used to connect with server.py and send msgs."""

import json
import socket
import sys
import threading
from pathlib import Path
from time import sleep

from classes.exceptions import InvalidMsgAction, InvalidMsgType
from classes.protocol import format_msg


class Client:
    """ARGS:
    address: str
    socket.

    Holds values esseintal for client to recive and send packets."""

    def __init__(self, port, host, IPV=socket.AF_INET, PROTOCOL=socket.SOCK_STREAM):
        """Initializes a Client instance.

        Args:
            port (int): The server port to connect to.
            host (str): The server hostname or IP address.
            IPV (int, optional): Address family. Defaults to ``socket.AF_INET``.
            PROTOCOL (int, optional): Socket type. Defaults to ``socket.SOCK_STREAM``.
        """
        self.socket = socket.socket(IPV, PROTOCOL)
        self.HOST = host
        self.PORT = port
        self.thread: threading.Thread | None = None

        self.disconnected = threading.Event()

        self.chat_history = []

        self.on_message = None

        self.action_map = {
            "response": {
                "get_usernames": self._handle_response,
                "register": self._handle_response,
                "logout": self._handle_response,
            },
            "chat": {"whisper": self._handle_whisper, "group": self._handle_chat},
            "warning": {
                "server_close": self._hadnle_server_close,
                "not_registered": self._handle_warning,
            },
        }

        self.__temp_response = None
        self.__response_ready = threading.Event()

    @classmethod
    def load_from_config(cls) -> Client:
        """Creates a Client from the project's server configuration file.

        Reads ``configs/server_config.json`` relative to the project root and
        instantiates ``cls`` using the values under the ``"client"`` key.

        Returns:
            Client: A new client instance configured from the JSON file.
        """
        CONFIG_PATH = (
            Path(__file__).resolve().parent.parent / "configs" / "server_config.json"
        )

        with open(CONFIG_PATH) as f:
            server_config = json.load(f)["client"]

        return cls(**server_config)

    def connect_host(self):
        """Connects the client socket to the configured host and port.

        Raises:
            OSError: If the connection attempt fails.
        """
        try:
            self.socket.connect((self.HOST, self.PORT))
        except OSError as e:
            print(f"Connection failed: {e}", file=sys.stderr)
            raise

    def cleanup(self):
        """Marks the client as disconnected and closes the underlying socket.

        The socket shutdown is attempted gracefully; any ``OSError`` raised
        during shutdown is ignored, and the socket is always closed.
        """
        self.disconnected.set()
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        finally:
            self.socket.close()

    def _send_and_wait(self, msg) -> dict | None:
        """Sends a message and blocks until the matching response arrives.

        Args:
            msg (str): The formatted message to send to the server.

        Returns:
            dict: The response message received from the server.
        """
        self._send_to_server(msg)

        self.__response_ready.wait()

        response, self.__temp_response = self.__temp_response, None

        self.__response_ready.clear()

        return response

    def send_logout(self):
        formated_msg = format_msg(msg_type="auth", action="logout")

        response = self._send_and_wait(formated_msg)

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
        return f"Server has disconnected. Reason: {msg['reason']} {msg['data']}"

    def _handle_warning(self, msg):
        return

    def _handle_chat(self, msg):
        self.chat_history.append(msg)

        if callable(self.on_message):
            self.on_message(msg)

    def _handle_whisper(self, msg):
        self.chat_history.append(msg)

        if callable(self.on_message):
            self.on_message(msg)

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
        reader = self.socket.makefile("r", encoding="utf-8")

        try:
            while not self.disconnected.is_set():
                raw_data = reader.readline()

                if not raw_data:
                    raise ConnectionResetError

                formated_msg = json.loads(raw_data)
                self.msg_handler(formated_msg)

        except OSError, ConnectionResetError, BrokenPipeError:
            print("Connection Error from host side!", file=sys.stderr)

        except json.JSONDecodeError, TypeError:
            print("Invalid msg. Could not format msg to JSON.", file=sys.stderr)

        finally:
            print("Leaving reciving msg thread", file=sys.stderr)
            self.cleanup()

    def _send_to_server(self, msg: str):
        msg += "\n"  # Msg must end with \n to know whole msg has been sent
        try:
            self.socket.sendall(msg.encode())
        except OSError:
            print(
                "Host disconnected. If you are inside input please type /exit",
                file=sys.stderr,
            )

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
