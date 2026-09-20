"""This code dosen't have exit program. It will run forever untill program will get KeyInterupted/Closed. Threads won't close automaticly, python and linux will close them after a 1 min after closing program."""

import json
from pathlib import Path

from server.server import Server


def main():
    """Runs program"""

    CONFIG_PATH = (
        Path(__file__).resolve().parent.parent / "config" / "server_config.json"
    )

    with open(CONFIG_PATH, encoding="utf-8") as f:
        server_config = json.load(f)["server"]

    Server(**server_config).connection_loop()


if __name__ == "__main__":
    main()
