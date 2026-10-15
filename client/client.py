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

    def _send_and_wait(self, msg: str) -> dict:
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

        if not isinstance(response, dict):
            raise TypeError(f"Exprected dict, got {type(response).__name__}")
        return response

    def send_logout(self) -> dict:
        """Sends a logout request to the server and waits for the response.

        Returns:
            dict: The server's response to the logout request.
        """
        formated_msg = format_msg(msg_type="auth", action="logout")

        response = self._send_and_wait(formated_msg)

        return response

    def send_register(self, username: str) -> dict:
        """Registers the given username with the server.

        Args:
            username (str): The username to register.

        Returns:
            dict: The server's response to the registration request.
        """
        msg = format_msg(msg_type="auth", action="register", data=username)

        response = self._send_and_wait(msg)

        return response

    def get_usernames(self) -> list:
        """Requests the list of currently registered usernames.

        Returns:
            list: The ``data`` field of the server's response.
        """
        msg = format_msg(msg_type="query", action="get_usernames")

        response = self._send_and_wait(msg)

        return response["data"]

    def broadcast(self, data: str):
        """Sends a group chat message to the server (fire-and-forget).

        Args:
            data (str): The message body to broadcast.
        """
        msg = format_msg(msg_type="chat", action="group", data=data)

        self._send_to_server(msg)

    def send_whisper(self, data: str, dst: str):
        """Sends a private (whisper) message to a specific user.

        Args:
            data (str): The message body to send.
            dst (str): The destination username.
        """
        msg = format_msg(msg_type="chat", action="whisper", dst=dst, data=data)

        self._send_to_server(msg)

    def _hadnle_server_close(self, msg: dict) -> str:
        """Handles a server-close warning message.

        Args:
            msg (dict): The warning message; expected to contain ``reason`` and ``data``.

        Returns:
            str: A human-readable description of the server shutdown.
        """
        return f"Server has disconnected. Reason: {msg['reason']} {msg['data']}"

    def _handle_warning(self, msg: dict):
        """Handles generic warning messages.

        Currently a no-op placeholder.

        Args:
            msg (dict): The warning message.
        """
        return

    def _handle_chat(self, msg: dict):
        """Handles an incoming group chat message.

        Appends the message to ``chat_history`` and invokes ``on_message`` if set.

        Args:
            msg (dict): The chat message.
        """
        self.chat_history.append(msg)

        if callable(self.on_message):
            self.on_message(msg)

    def _handle_whisper(self, msg: dict):
        """Handles an incoming whisper (private) message.

        Appends the message to ``chat_history`` and invokes ``on_message`` if set.

        Args:
            msg (dict): The whisper message.
        """
        self.chat_history.append(msg)

        if callable(self.on_message):
            self.on_message(msg)

    def _handle_response(self, msg: dict):
        """Handles a server response by storing it and unblocking waiters.

        Args:
            msg (dict): The response message.
        """
        self.__temp_response = msg
        self.__response_ready.set()

    def msg_handler(self, msg: dict):
        """Dispatches an incoming message to the appropriate handler.

        Args:
            msg (dict): The decoded message. Must contain ``msg_type`` and ``action``.

        Raises:
            InvalidMsgType: If ``msg['msg_type']`` is not present in ``action_map``.
            InvalidMsgAction: If ``msg['action']`` is not valid for the given type.
        """
        actions = self.action_map.get(msg["msg_type"])

        if not actions:
            raise InvalidMsgType("Given msg type from host was invalid!!")

        func = actions.get(msg["action"])

        if not func:
            raise InvalidMsgAction("Given msg action from host was invalid!!")

        func(msg)

    def recive_msg(self):
        """Receives and processes messages from the server until disconnect.

        Runs in a loop reading newline-delimited JSON messages from the socket
        and dispatching them via ``msg_handler``. Handles connection-related
        errors and always calls ``cleanup`` on exit.
        """
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
        """Sends a newline-terminated message to the server.

        Args:
            msg (str): The message to send. A trailing ``\\n`` is appended.
        """
        msg += "\n"  # Msg must end with \n to know whole msg has been sent
        try:
            self.socket.sendall(msg.encode())
        except OSError:
            print(
                "Host disconnected. If you are inside input please type /exit",
                file=sys.stderr,
            )

    def start(self):
        """Connects to the server and starts the background receive thread."""
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
