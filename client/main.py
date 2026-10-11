from prompt_toolkit.patch_stdout import patch_stdout

from client.client import Client
from client.tui import Tui


def main():
    client = Client.load_from_config()

    with patch_stdout():
        client.start()

        tui = Tui(client)
        tui.start()


if __name__ == "__main__":
    main()
