from client.client import Client
from client.tui import Tui


def main():
    client = Client.load_from_config()

    client.start()

    tui = Tui(client)
    tui.start()


if __name__ == "__main__":
    main()
