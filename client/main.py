from client.client import Client
from client.tui import Tui


def main():
    client = Client.load_from_config()

    client.connect_host()

    client.start()

    tui = Tui(client)
    tui.start()
