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
    """Class creates a socket that local machines can connect to and send msgs to.

    Attributes:
        port (int): The port the server socket binds to.
        host (str): The host/interface the server socket binds to.
        echo_msgs (bool): Whether broadcast messages are echoed back to the sender.
        action_map (dict): Mapping of ``msg_type`` -> ``action`` -> handler method.
        server (socket.socket): The listening socket, created by ``create_server``.
        __clients_map (dict): Maps client key (address) -> :class:`Client`.
        __users_map (dict): Maps username -> :class:`Client`.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Initializes a Server instance.

        Args:
            host (str, optional): Host/interface to bind to. Defaults to ``"0.0.0.0"``.
            port (int, optional): Port to bind to. Defaults to ``8000``.
        """
        self.port = port  # Holds to which PORT socket will be connected to
        self.host = host  # Holds...
        self.__clients_map = {}  #  client_address -> Client
        self.__users_map = {}  # username -> Client
        self.echo_msgs = True
        self.action_map = {
            "chat": {"whisper": self._handle_whisper, "group": self._handle_broadcast},
            "query": {
                "get_usernames": self._handle_get_usernames  # For now it is clients. Once login will be implemeneted. It wil lbe users
            },
            "auth": {"register": self._handle_register, "logout": self._handle_logout},
            "remote": {"send_into_file": self._handle_send_into_file},
        }

    @classmethod
    def load_from_config(cls) -> Server:
        """Creates a Server from the project's server configuration file.

        Reads ``configs/server_config.json`` relative to the project root and
        instantiates ``cls`` using the values under the ``"server"`` key.

        Returns:
            Server: A new server instance configured from the JSON file.
        """
        CONFIG_PATH = Path(__file__).parent.parent / "configs" / "server_config.json"

        with open(CONFIG_PATH, "r") as f:
            settings = json.load(f)["server"]

        return cls(**settings)

    def remove_client(self, key: str) -> Client | int:
        """Removes a user from the users map.

        Args:
            username (str): The username to remove.

        Returns:
            Client | int: The removed :class:`Client`, or ``0`` if not found.
        """
        return self.__clients_map.pop(key, 0)

    def remove_user(self, username: str) -> Client | int:
        """Removes a user from the users map.

        Args:
            username (str): The username to remove.

        Returns:
            Client | int: The removed :class:`Client`, or ``0`` if not found.
        """
        return self.__users_map.pop(username, 0)

    def create_server(
        self, ipv: int = socket.AF_INET, protocol: int = socket.SOCK_STREAM
    ) -> None:
        """Creates a socket with choosen protcol and binds it to choosen PORT with choosen IP.

        Args:
            ipv (int, optional): Address family. Defaults to ``socket.AF_INET``.
            protocol (int, optional): Socket type. Defaults to ``socket.SOCK_STREAM``.
        """
        self.server = socket.socket(ipv, protocol)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))

    def append_clients(self, client: Client):
        """Appends client to server client list.

        Args:
            client (Client): The client to register in the clients map.
        """
        self.__clients_map[client.key] = client

    def get_client(self, key: str) -> None | Client:
        """Returns client wit that address.

        Args:
            key: The client key (address) to look up.

        Returns:
            Client | None: The matching client, or ``None`` if not found.
        """
        return self.__clients_map.get(key)

    def get_user(self, username) -> Client | None:
        """Returns client with that username.

        Args:
            username (str): The username to look up.

        Returns:
            Client | None: The matching client, or ``None`` if not found.
        """
        return self.__users_map.get(username)

    def address_to_username(self, address: str) -> str:
        """Resolves a client address to its registered username.

        Args:
            address (str): The client key (address) to resolve.

        Returns:
            str: The matching username, or an empty string if none is found.
        """
        client = self.get_client(address)

        if client:
            for username, user in self.__users_map.items():
                if client == user:
                    return username
        return ""

    def get_all_clients(self) -> list[Client]:
        """Returns list of all clients objects from clients map.

        Returns:
            list[Client]: All currently connected clients.
        """
        return list(self.__clients_map.values())

    def get_all_keys(self) -> list[str]:
        """Returns list of all addresses.

        Returns:
            list: All client keys (addresses) currently registered.
        """
        return list(self.__clients_map.keys())

    def get_all_usernames(self) -> list[str]:
        """Returns list of all usernames.

        Returns:
            list[str]: All currently registered usernames.
        """
        return list(self.__users_map.keys())

    def get_all_users(self) -> list:
        """Returns list of all clients objects from users map.

        Returns:
            list[Client]: All clients that currently have a username.
        """
        return list(self.__users_map.values())

    def get_clients_count(self) -> int:
        """Returns total count of client connected to server.

        Returns:
            int: The number of connected clients.
        """
        return len(self.__clients_map)

    def accept_connection(self) -> Client:
        """Lisitens for connection and if found one accepts it.

        Returns:
            Client: The newly accepted client, already added to the clients map.
        """
        self.server.listen()
        print("listening...")

        client_socket, (address, port) = self.server.accept()

        client = Client(client_socket, address, port, self)
        print(f"{client.key} has connected!")

        self.append_clients(client)
        return client

    def cleanup(self, reason: str = "No reason") -> None:
        """Closes up sockets and clients.

        Args:
            reason (str, optional): Human-readable reason for shutdown.
                Defaults to ``"No reason"``.
        """
        sleep(1)
        self.server.close()

        for client in self.get_all_clients():
            client.cleanup()

    def _send_not_registerted_warning(self, client: Client) -> None:
        """Sends a "not registered" warning to the given client.

        Args:
            client (Client): The client to warn.
        """
        formated_msg = format_msg(
            msg_type="warning", action="not_registered", reason="Registration required"
        )
        client.send_msg(formated_msg)

    def broadcast(self, msg: str, not_including: set[Client] | None = None) -> None:
        """Sends msg to all clients.

        Args:
            msg (str): The formatted message to broadcast.
            not_including (set[Client] | None, optional): Clients to exclude from
                the broadcast when ``echo_msgs`` is ``False``. Defaults to ``None``.
        """
        for client in self.get_all_clients():
            if self.echo_msgs or not not_including:
                client.send_msg(msg)

                continue

            else:
                if client not in not_including:
                    client.send_msg(msg)

    def _handle_broadcast(self, client: Client, msg: dict) -> None:
        """Handles a group chat message from a client and broadcasts it.

        Args:
            client (Client): The sending client.
            msg (dict): The incoming chat message.
        """
        src = client.username if client.username else client.address

        formated_msg = format_msg(
            msg_type="chat", action="group", src=src, data=msg["data"]
        )

        self.broadcast(formated_msg, not_including={client})

    def _handle_get_usernames(self, client: Client, msg: dict) -> None:
        """Handles a request for the list of registered usernames.

        Args:
            client (Client): The requesting client.
            msg (dict): The incoming query message.
        """
        respond_msg = format_msg(
            msg_type="response", action="get_usernames", data=self.get_all_usernames()
        )

        client.send_msg(respond_msg)

    def _handle_register(self, client: Client, msg: dict) -> None:
        """Handles a registration request from a client.

        Args:
            client (Client): The requesting client.
            msg (dict): The incoming auth message; ``data`` holds the username.
        """
        username = msg["data"].strip()

        if client.username:
            return

        if username not in self.__users_map and username:
            self.__users_map[username] = client
            client.username = username

            formated_msg = format_msg(msg_type="response", action="register", data=True)

        else:
            formated_msg = format_msg(
                msg_type="response", action="register", data=False
            )

        client.send_msg(formated_msg)

    def _handle_logout(self, client: Client, msg: dict) -> None:
        """Handles a logout request from a client.

        Args:
            client (Client): The requesting client.
            msg (dict): The incoming auth message.
        """
        if not client.username:
            formated_msg = format_msg(msg_type="response", action="logout", data=False)

            client.send_msg(formated_msg)

            return

        self.remove_user(client.username)
        client.username = None

        formated_msg = format_msg(msg_type="response", action="logout", data=True)

        client.send_msg(formated_msg)

    def _handle_whisper(self, client: Client, msg: dict) -> None:
        """Sends msg to choosen client and echos it back to sender.

        Args:
            client (Client): The sending client.
            msg (dict): The incoming whisper message; ``dst`` is the target username.
        """
        username = msg["dst"]
        dst = self.get_user(username)

        assert client.username is not None, (
            "For debbugin: Someone who was not logged in sent whisper"
        )

        formated_msg = format_msg(
            msg_type="chat",
            action="whisper",
            data=msg["data"],
            src=client.username,
            dst=username,
        )

        if isinstance(dst, Client):
            dst.send_msg(formated_msg)

        # Echoing back
        if username == client.username or not self.echo_msgs or not dst:
            return

        client.send_msg(formated_msg)

    def _handle_send_into_file(self, client: Client, msg: dict):

        print(type(msg))

        for key, value in msg.items():
            print(key, value)

        print(msg["filename"])
        new_file_name = f"{client.username}_{msg['filename']}"

        src = client.username if client.username else ""

        formated_msg = format_msg(
            msg_type="remote",
            action="send_into_file",
            dst=msg["dst"],
            filename=new_file_name,
            data=msg["data"],
            src=src,
        )

        user = self.get_user(msg["dst"])

        if isinstance(user, Client):
            user.send_msg(formated_msg)

    def msg_handler(self, client: Client, msg: dict) -> None:
        """Takes msg type and action and sends it to correct function.

        Args:
            client (Client): The client that sent the message.
            msg (dict): The decoded message, containing ``msg_type`` and ``action``.

        Raises:
            InvalidMsgType: If ``msg['msg_type']`` is not present in ``action_map``.
            InvalidMsgAction: If ``msg['action']`` is not valid for the given type.
        """
        if msg["msg_type"] == "chat" and not client.username:
            self._send_not_registerted_warning(client)
            return

        actions = self.action_map.get(msg["msg_type"])

        if not actions:
            raise InvalidMsgType(f"Given msg type from {client} was invalid")

        func = actions.get(msg["action"])

        if not func:
            raise InvalidMsgAction(f"Given msg action from {client} was invalid")

        func(client, msg)

    def _connection_loop(self) -> None:
        """On loop lisitens for connections and recives/send msgs to everyone.

        Creates the server socket and repeatedly accepts new clients, spawning a
        daemon thread per client to receive its messages. Exits on
        ``KeyboardInterrupt`` and always prints a shutdown message.
        """
        self.create_server()

        try:
            while True:
                client = self.accept_connection()  # Adress returns tuple (IP,PORT)

                client.thread = threading.Thread(
                    target=client.recive_msg,
                    name=f"Thread{client.address}:{client.port}",
                )

                client.thread.daemon = True
                client.thread.start()

        except KeyboardInterrupt:
            print("KEYBAORD INTERRUPT CLOSING PROGRAM...")
            self.cleanup(reason="Host did close the server.")

        finally:
            print("Program closed.")

    def start(self) -> None:
        """Starts server connection. lisitens for clients and connects them."""
        self._connection_loop()


def main() -> None:
    Server.load_from_config().start()


if __name__ == "__main__":
    main()
