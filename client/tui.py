from pathlib import Path

from colorama import Fore, Style
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import ANSI

from client.client import Client
from utils import clear


class Tui:
    """Terminal user interface for interacting with the chat client.

    Handles login, chat, whisper, and remote command flows, and renders
    all menus and prompts to the terminal.

    Attributes:
        prompt_session (PromptSession): Prompt-toolkit session used for all
            user input, configured to erase the prompt when done.
        source_files_prefix (str): Directory prefix prepended to source file
            names before they are sent.
        inbox_prefix (str): Directory prefix prepended to destination
            file names on the remote client.
        recived_files_history (list): List tracking the history of files
            received from the server/clients.
        not_read_new_file (bool): Flag indicating if there are unread
            newly received files.
        BACK_INPUTS (set): Collection of command strings that trigger
            an exit or back action.
        __client (Client): Client instance used for all network operations.
        __username (str | None): Currently logged-in username, or ``None``
            when logged in as guest.
    """

    def __init__(self, client: Client) -> None:
        """Initilize the TUI and starts loggin process

        Args:
            client (Client): Client insteance.
        """
        # self.__config = Config("tui_settings").load_data()
        self.__client = client
        self.__username = None

        self.prompt_session = PromptSession(erase_when_done=True)

        self.source_files_prefix = "source_files/"
        self.inbox_prefix = "inbox/"

        self.__client.download_dir = self.inbox_prefix

        self.recived_files_history = []
        self.not_read_new_file = False
        self.__client.on_recived_file = self._update_file_history
        self.in_menu = False

        Path(self.source_files_prefix).mkdir(parents=True, exist_ok=True)

        self.BACK_INPUTS = {"exit", "/exit", "/q", "q", "b", "back", "\x1b"}

        self.login()

    def _print_menu(self) -> None:
        """Displays the main navigation menu in the terminal."""
        username = (
            self.__username
            if self.__username
            else f"{Fore.YELLOW}GUEST{Style.RESET_ALL}"
        )
        print(f"=== {Fore.CYAN}{username}{Style.RESET_ALL} ===")
        print(
            f"{Fore.CYAN}1.{Style.RESET_ALL} {'Log out' if self.__username else 'Log in'}"
        )
        print(f"{Fore.CYAN}2.{Style.RESET_ALL} Group Chat")
        print(f"{Fore.CYAN}3.{Style.RESET_ALL} Whisper")
        print(f"{Fore.CYAN}4.{Style.RESET_ALL} Remote command")
        file_badge = (
            f"[{Fore.RED}NEW{Style.RESET_ALL}] File History"
            if self.not_read_new_file
            else "File History"
        )
        print(f"{Fore.CYAN}5.{Style.RESET_ALL} {file_badge}")
        print(f"{Fore.CYAN}q.{Style.RESET_ALL} Exit")

    def _print_file_history(self) -> None:
        """Displays the received file history."""
        print(f"\n=== {Fore.CYAN}Received Files History{Style.RESET_ALL} ===")

        if not self.recived_files_history:
            print(f"{Fore.YELLOW}No files received yet.{Style.RESET_ALL}")
        else:
            for i, file_item in enumerate(self.recived_files_history, start=1):
                print(
                    f"{Fore.CYAN}{i}.{Style.RESET_ALL} From:{file_item[0]} File:{file_item[1]}"
                )

    def file_history(self) -> None:
        """Displays received files history with color coding and management options."""
        clear()
        self.not_read_new_file = False

        self._print_file_history()

        print(f"\n{Fore.YELLOW}/clear{Style.RESET_ALL} to clear history")
        print(f"{Fore.CYAN}q.{Style.RESET_ALL} back")

        user_input = self._user_input("\n> ").strip().lower()

        if self._check_if_exit(user_input):
            return

        elif user_input == "/clear":
            confirm = (
                self._user_input(f"{Fore.RED}Are you sure? (y/n): {Style.RESET_ALL}")
                .strip()
                .lower()
            )

            if confirm == "y" or confirm == "yes":
                self.recived_files_history.clear()
                print(f"{Fore.GREEN}File history cleared.{Style.RESET_ALL}")

    def __invalid_input(self, prompt: str = "Invalid answer") -> None:
        """Displays an error msg and waits for user input

        args:
            prompt (str) : Displays error msg and waits for user input
        """
        input(f"{Fore.RED}{Style.BRIGHT}{prompt}{Style.RESET_ALL}")

    def _check_if_exit(
        self, user_msg: str, include_back_inputs: list[str] | None = None
    ) -> bool:
        """Checks if the user input matches any registered back or exit command.

        Args:
            user_msg (str): Input string to evaluate.
            include_back_inputs (list[str]): Included inside BACK_INPUTS to exit command

        Returns:
            bool: True if the input is in BACK_INPUTS, else False.
        """
        back_inputs = self.BACK_INPUTS.copy()
        if include_back_inputs:
            back_inputs.add(*include_back_inputs)

        return user_msg.lower() in back_inputs

    def __int_input(
        self,
        length: int,
        offset: int = 0,
        prompt: str = "> ",
        include_back_inputs: list[str] | None = None,
    ) -> int | None:
        """Askes user for int input in range of 1-lenght. Returns None if user types /q

        Args:
            lenght (int): Range that it will be compered to.
            offset (int): Number that will move backwards result by that amount
            propmt (str): Prompt that will be displayed while asking for input.
            include_back_inputs (list[str]): List of allowed back inputs. See meth:`_check_if_exit` for more info

        returns:
            None if user types in ``self.BACK_INPUTS`` else user_choosen number
        """
        while True:
            try:
                user_choice = self._user_input(prompt)

                if self._check_if_exit(
                    user_choice, include_back_inputs=include_back_inputs
                ):
                    return

                user_choice = int(user_choice)

                if 1 <= user_choice <= length:
                    user_choice += offset
                    return user_choice

                self.__invalid_input()

            except ValueError:
                self.__invalid_input("Value must be an integer!")

    def __print_out_list(self, *items):
        """Goes over items and prints them out with index=1 at start.

        Args:
            *items: Items that will get printed
        """

        for index, item in enumerate(items, start=1):
            print(f"{index}. {item}")

    def _user_input(self, prompt="> ") -> str:
        """Asks user for input using prompt_session.prompt and retuns value.

        Args:
            prompt='> ' (str): Prompt that will be displayed while asking user for input.

        Returns:
            user input
        """
        user_msg = self.prompt_session.prompt(ANSI(prompt))
        return user_msg

    def _update_file_history(self, msg):
        """Updates the received files history with a new file entry and marks it as unread.

        If the user is currently viewing the main menu, it refreshes the display
        to show the new file notification badge.

        Args:
            msg (dict): msg from classes.protcol
        """
        self.recived_files_history.append([msg["src"], msg["filename"]])
        self.not_read_new_file = True

        if self.in_menu:
            clear()
            self._print_menu()

    def login(self):
        """Asks user for login name and sends to server. if successfull then sets it as sef.__username"""
        user_login = self._user_input("Enter your login: ")

        response = self.__client.send_register(user_login)

        valid = response["data"]

        if valid:
            self.__username = user_login

        else:
            if response["reason"]:
                self.__invalid_input(prompt=response["reason"])

    def logout(self):
        """Sends server information about logout and if successfull sets 'self.__username' to None"""
        if self.__client.send_logout():
            self.__username = None
            self._user_input("Sing out!")

        else:
            self.__invalid_input(prompt="Couldn't logout!")

    def get_name(self) -> str | None:
        """Returns currently logged in user name

        Returns:
            The username if user is logged in else 'None'
        """
        return self.__username

    def _choose_client(self, clients_names: list[str]) -> str | None:
        """Print the client list and ask the user to pick one by number.

        Args:
            clients_names: Client names to choose from.

        Returns:
            The chosen client name, or None if the user backs out or the list
            is empty.
        """
        if not clients_names:
            print(f"{Fore.YELLOW}No clients are connected.{Style.RESET_ALL}")
            input(f"{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
            return None

        print(f"{Style.BRIGHT}Connected clients{Style.RESET_ALL}\n")
        for number, name in enumerate(clients_names, start=1):
            print(f"  {Fore.CYAN}{number}.{Style.RESET_ALL} {name}")
        print()

        prompt_msg = (
            f"{Fore.YELLOW}{self.__username}{Style.RESET_ALL} "
            f"[{Fore.CYAN}1-{len(clients_names)}{Style.RESET_ALL}] > "
        )

        choice = self.__int_input(len(clients_names), prompt=prompt_msg, offset=-1)

        if choice is None:
            return None

        return clients_names[choice]

    def _print_whisper(self, msg: dict):
        """Prints msg and it's source with [PRIAVTE] at start with magenta color

        Args:
            msg (dict): Msg from classes.protocol
        """
        print("[" + Fore.MAGENTA + "PRIVATE" + Style.RESET_ALL + "]", end=" ")
        print(Fore.MAGENTA + msg["src"] + Style.RESET_ALL + ": " + msg["data"])

    def _print_msg_with_name(self, msg):
        """Prints msg and it's source with yellow color

        Args:
            msg (dict): Msg from classes.protocol
        """
        print(Fore.YELLOW + msg["src"] + ": " + msg["data"] + Style.RESET_ALL)

    def _print_msg(self, msg):
        """Takes msg and parses it to find correct way to print it

        Args:
            msg (dict): Msg from classes.protocol
        """
        if msg["action"] == "whisper":
            self._print_whisper(msg)

        elif self.__username in msg["data"]:
            self._print_msg_with_name(msg)

        else:
            print(msg["src"] + ": " + msg["data"])

    def group_chat(self):
        clear()

        for msg in self.__client.chat_history:
            self._print_msg(msg)

        self.__client.on_message = self._print_msg

        try:
            while True:
                user_msg = self._user_input("(/q to leave) > ")

                if self._check_if_exit(user_msg):
                    return

                self.__client.broadcast(user_msg)

        finally:
            self.__client.on_message = None

    def whisper(self):
        clear()

        clients = self.__client.get_usernames()

        client = self._choose_client(clients)

        if not client:
            return

        user_msg = self._user_input()

        if self._check_if_exit(user_msg):
            return

        self.__client.send_whisper(user_msg, client)

    def _print_source_files(self) -> list[str] | None:
        """List files available under ``self.source_files_prefix``.

        Prints a numbered listing so the user can see what the prefix contains
        before typing a name. Prints a short notice instead if the prefix is
        missing or contains no files.

        Returns:
            files_list if folder exists or there are any files.
        """
        folder = Path(self.source_files_prefix)

        if not folder.is_dir():
            print(f"{Fore.YELLOW}({folder} does not exist){Style.RESET_ALL}\n")
            return

        files = sorted(entry.name for entry in folder.iterdir() if entry.is_file())

        if not files:
            print(f"{Fore.YELLOW}(no files in {folder}){Style.RESET_ALL}\n")
            return

        files_list = []

        print(f"{Style.BRIGHT}Available files in {folder}{Style.RESET_ALL}")
        for number, name in enumerate(files, start=1):
            files_list.append(name)
            print(f"  {Fore.CYAN}{number}.{Style.RESET_ALL} {name}")
        print()

        return files_list

    def _menu_remote(self, title: str, options: list[str]) -> str | None:
        """Render a remote menu and return the chosen option number as a string.

        Uses ``__int_input`` for validation, so ``/q`` and any entry in
        ``BACK_INPUTS`` return None instead of a number.

        Args:
            title: Heading printed above the menu.
            options: Option labels; numbering starts at 1.

        Returns:
            The chosen option as a string ("1", "2", ...), or None if the user
            backed out.
        """
        while True:
            clear()
            print(f"{Style.BRIGHT}{title}{Style.RESET_ALL}\n")

            for number, label in enumerate(options, start=1):
                print(f"  {Fore.CYAN}{number}.{Style.RESET_ALL} {label}")
            print(f"  {Fore.CYAN}q.{Style.RESET_ALL} Back")
            print()

            choice = self.__int_input(len(options))

            if choice is None:
                return None

            return str(choice)

    def _prompt_target_file(self, dst: str) -> str | None:
        """Prompt for target file name. Returns None if user cancels."""
        value = self._user_input(
            f"Enter target file name on client {Fore.GREEN}{dst}{Style.RESET_ALL} "
            f"(blank to cancel): {Fore.YELLOW}{self.inbox_prefix}{Style.RESET_ALL}"
        ).strip()

        return value or None

    def _send_file_into_file(self) -> None:
        """Handle the 'File -> File' action."""
        clear()
        dst = self._choose_client(self.__client.get_usernames())
        clear()

        if dst is None:
            return

        files_list = self._print_source_files()

        source_input = self._user_input(
            f"Enter your file name or number: {Fore.YELLOW}{self.source_files_prefix}{Style.RESET_ALL}"
        ).strip()

        if not source_input:
            return

        if source_input.isdigit():
            index = int(source_input) - 1

            if files_list and 0 <= index < len(files_list):
                source_file = files_list[index]

            else:
                self.__invalid_input("Invalid file number")
                return
        else:
            source_file = source_input

        target_file = self._prompt_target_file(dst)

        if target_file is None:
            return

        self.__client.send_into_file(
            dst,
            source_path=self.source_files_prefix + source_file,
            target_filename=target_file,
        )

        input(f"{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

    def _send_msg_into_file(self) -> None:
        """Handle the 'Msg -> File' action."""
        clear()
        dst = self._choose_client(self.__client.get_usernames())
        clear()
        if dst is None:
            return

        data = self._user_input("Enter your message: ")
        if not data:
            return

        target_file = self._prompt_target_file(dst)
        if target_file is None:
            return

        self.__client.send_into_file(dst, data=data, target_filename=target_file)

        self._user_input(f"{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

    def send_into_file(self) -> None:
        """Handle the submenu for sending a file or a message into a remote client's file."""
        while True:
            choice = self._menu_remote(
                "Send into file",
                ["File -> File", "Msg -> File"],
            )

            match choice:
                case None:
                    break
                case "1":
                    self._send_file_into_file()
                case "2":
                    self._send_msg_into_file()

    def remote_command(self) -> None:
        """Top-level loop for remote commands."""
        while True:
            choice = self._menu_remote(
                "Remote Commands",
                ["Send file/msg into someone's file"],
            )

            match choice:
                case None:
                    break
                case "1":
                    self.send_into_file()

    def start(self) -> None:
        """Starts the main TUI event loop, handling menu navigation and user choices
        until the client disconnects or exits.
        """
        while not self.__client.disconnected.is_set():
            self.in_menu = True
            clear()

            self._print_menu()
            user_choice = self._user_input()

            if self.__client.disconnected.is_set():
                return

            logged = bool(self.__username)

            match user_choice:
                case "1":
                    if logged:
                        self.logout()
                    else:
                        self.login()

                case "2":
                    if logged:
                        self.in_menu = False
                        self.group_chat()
                    else:
                        self.__invalid_input()

                case "3":
                    if logged:
                        self.in_menu = False
                        self.whisper()
                    else:
                        self.__invalid_input()

                case "4":
                    if logged:
                        self.in_menu = False
                        self.remote_command()
                    else:
                        self.__invalid_input()

                case "5":
                    if logged:
                        self.in_menu = False
                        self.file_history()
                    else:
                        self.__invalid_input()

                case "q":
                    self.__client.cleanup()
                    break

                case _:
                    self.__invalid_input()
