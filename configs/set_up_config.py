"""Quick TUI version of setting up config if the person doesn't know where to find it.

This module is designed to be imported by a larger application. When run
directly, it launches an interactive menu for editing ``server_config.json``.

Typical usage::

    from quick_tui import set_up_config

    data = set_up_config()
"""

import json

from colorama import Fore, Style, init

from utils import clear

init(autoreset=True)

CONFIG_FILE = "configs/server_config.json"


def load_config() -> dict:
    """Load the server configuration from :data:`CONFIG_FILE`.

    Returns:
        dict: Parsed configuration containing at least ``client`` and
        ``server`` sections, each with ``host`` and ``port`` keys.

    Raises:
        FileNotFoundError: If :data:`CONFIG_FILE` does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(data: dict) -> None:
    """Write the given configuration back to :data:`CONFIG_FILE`.

    Args:
        data: The full configuration dictionary to persist. It is written
            with an indent of 4 for readability.

    Raises:
        OSError: If the file cannot be opened for writing.
    """
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


def set_up_config() -> dict:
    """Run the interactive configuration menu.

    Loads the current config, presents a colored TUI menu, and lets the
    user edit the client/server host and port values. Each successful
    edit is saved immediately to disk.

    Returns:
        dict: The final configuration dictionary after the user selects
        "Exit". This allows callers to use the updated values without
        re-reading the file.
    """
    data = load_config()

    while True:
        clear()

        print(
            f"{Fore.CYAN}1. {Fore.WHITE}Address client will connect to: {Fore.YELLOW}{data['client']['host']}"
        )
        print(
            f"{Fore.CYAN}2. {Fore.WHITE}Client port: {Fore.YELLOW}{data['client']['port']}"
        )
        print(
            f"{Fore.CYAN}3. {Fore.WHITE}Address that server will listen on "
            f"{Fore.LIGHTBLACK_EX}(leave at 0.0.0.0 so it will listen for everyone)"
            f"{Fore.WHITE}: {Fore.YELLOW}{data['server']['host']}"
        )
        print(
            f"{Fore.CYAN}4. {Fore.WHITE}Server port: {Fore.YELLOW}{data['server']['port']}"
        )
        print(f"{Fore.CYAN}5. {Fore.WHITE}Exit")

        user_choice = input(f"{Fore.GREEN}> {Style.RESET_ALL}").strip()

        match user_choice:
            case "1":
                new_value = input("Enter new client host: ").strip()
                if new_value:
                    data["client"]["host"] = new_value
                    save_config(data)
                    print(f"{Fore.GREEN}Updated client host to {new_value}")
                else:
                    print(f"{Fore.RED}No change made.")

            case "2":
                new_value = input("Enter new client port: ").strip()
                if new_value.isdigit():
                    data["client"]["port"] = int(new_value)
                    save_config(data)
                    print(f"{Fore.GREEN}Updated client port to {new_value}")
                else:
                    print(f"{Fore.RED}Invalid port. Please enter a number.")

            case "3":
                new_value = input("Enter new server host: ").strip()
                if new_value:
                    data["server"]["host"] = new_value
                    save_config(data)
                    print(f"{Fore.GREEN}Updated server host to {new_value}")
                else:
                    print(f"{Fore.RED}No change made.")

            case "4":
                new_value = input("Enter new server port: ").strip()
                if new_value.isdigit():
                    data["server"]["port"] = int(new_value)
                    save_config(data)
                    print(f"{Fore.GREEN}Updated server port to {new_value}")
                else:
                    print(f"{Fore.RED}Invalid port. Please enter a number.")

            case "5":
                print(f"{Fore.CYAN}Exiting...")
                return data

            case _:
                print(f"{Fore.RED}Invalid choice. Please try again.")


if __name__ == "__main__":
    set_up_config()
