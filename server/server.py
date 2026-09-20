"""TCP Server module for accepting connections and broadcasting messages."""

import json
import socket
import threading
from pathlib import Path
from time import sleep

from classes.exceptions import InvalidMsgAction, InvalidMsgType
from classes.protocol import format_msg
from server.client import Client


class Server:
    """Class creates a socket that local machines can connect to and send msgs to"""

    def __init__(self, host="0.0.0.0", port=8000):
        self.port = port  # Holds to which PORT socket will be connected to
        self.host = host  # Holds...
        self.__clients_map = {}  #  client_address -> Client
        self.__users_map = {}  # username -> Client
        self.action_map = {
            "chat": {"whisper": self._handle_whisper, "group": self._handle_broadcast},
            "query": {
                "get_usernames": self._handle_get_usernames  # For now it is clients. Once login will be implemeneted. It wil lbe users
            },
            "auth": {"register": self._handle_register},
        }

    @classmethod
    def load_from_config(cls):
        CONFIG_PATH = Path(__file__).parent.parent / "configs" / "server_config.json"

        with open(CONFIG_PATH, "r") as f:
            settings = json.load(f)["server"]

        return cls(**settings)

    def remove_client(self, address):
        self.__clients_map.pop(address, None)

    def remove_user(self, username):
        self.__users_map.pop(username, None)

    def create_server(self, ipv=socket.AF_INET, protocol=socket.SOCK_STREAM):
        """Creates a socket with choosen protcol and binds it to choosen PORT with choosen IP"""
        self.server = socket.socket(ipv, protocol)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))

    def append_clients(self, client):
        """Appends client to server client list"""
        self.__clients_map[client.address] = client

    def get_client(self, address) -> None | Client:
        """Returns client wit that address"""
        return self.__clients_map.get(address)

    def get_user(self, username):
        """Returns client with that username"""
        return self.__users_map.get(username)

    def address_to_username(self, address: str) -> str:
        client = self.get_client(address)

        if client:
            for username, user in self.__users_map.items():
                if client == user:
                    return username
        return ""

    def get_all_clients(self):
        """Returns list of all clients"""
        return list(self.__clients_map.values())

    def get_all_usernames(self):
        """Returns list of all usernames"""
        return list(self.__users_map.keys())

    def get_clients_count(self):
        """Returns total count of client connected to server"""
        return len(self.__clients_map)

    def accept_connection(self) -> Client:
        """Lisitens for connection and if found one accepts it"""
        self.server.listen()
        print("listening...")

        client_socket, (address, port) = self.server.accept()

        client = Client(client_socket, address, port, self)
        print(f"{client.address} has connected!")

        self.append_clients(client)
        return client

    def cleanup(self):
        """Closes up sockets and clients"""
        msg = format_msg(
            msg_type="warning", action="server_close", data="Server closed."
        )
        self.broadcast(msg)
        sleep(4)
        self.server.close()

        for client in list(self.get_all_clients()):
            client.cleanup()

    def broadcast(self, msg):
        """Sends msg to all clients"""
        for client in self.get_all_clients():
            client.send_msg(msg)

    def _handle_broadcast(self, address, msg):
        src = self.address_to_username(address)
        formated_msg = format_msg(
            msg_type="chat", action="group", src=src, data=msg["data"]
        )
        self.broadcast(formated_msg)

    def _handle_get_usernames(self, address, msg):

        print(self.get_all_usernames())
        msg = format_msg(
            msg_type="response", action="get_usernames", data=self.get_all_usernames()
        )
        client = self.get_client(address)
        if client:
            client.send_msg(msg)
        else:
            print(
                f"[WARNING] Client at {address} disconnected before response could be sent."
            )

    def msg_handler(self, address, msg):
        """Takes msg type and action and sends it to correct function"""
        actions = self.action_map.get(msg["msg_type"])

        if not actions:
            raise InvalidMsgType(f"Given msg type from {address} was invalid")

        func = actions.get(msg["action"])

        if not func:
            raise InvalidMsgAction(f"Given msg action from {address} was invalid")

        func(address, msg)

    def _handle_register(self, address, msg):
        username = msg["data"]

        client = self.get_client(address)

        if username not in self.__users_map:
            self.__users_map[username] = client

            msg = format_msg(msg_type="response", action="register", data=True)

        else:
            msg = format_msg(msg_type="response", action="register", data=False)

        if isinstance(client, Client):
            client.send_msg(msg)

    def _handle_whisper(self, address: str, msg):
        """Sends msg to choosen client"""
        username = msg["dst"]
        dst = self.get_user(username)

        msg = format_msg(
            msg_type="chat",
            action="whisper",
            data=msg["data"],
            src=self.address_to_username(address),
        )

        if isinstance(dst, Client):
            dst.send_msg(username)

    def _connection_loop(self):
        """On loop lisitens for connections and recives/send msgs to everyone"""
        self.create_server()

        try:
            while True:
                client = self.accept_connection()  # Adress returns tuple (IP,PORT)

                client.thread = threading.Thread(
                    target=client.recive_msg,
                    name=f"Thread{client.address[0]}:{client.address[1]}",
                )

                self.__clients_map[client.address] = client

                client.thread.daemon = True
                client.thread.start()

        except KeyboardInterrupt:
            print("KEYBAORD INTERRUPT CLOSING PROGRAM...")

        finally:
            self.cleanup()
            print("Program closed.")

    def start(self):
        """Starts server connection. lisitens for clients and connects them"""
        self._connection_loop()


def main():
    Server.load_from_config().start()


if __name__ == "__main__":
    main()
