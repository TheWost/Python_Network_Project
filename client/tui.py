import os

from colorama import Fore, Style, init
from prompt_toolkit import PromptSession

# from configs.config import Config

init(autoreset=True)


class Tui:
    def __init__(self, client):
        # self.__config = Config("tui_settings").load_data()
        self.__client = client
        self.__username = None

        self.prompt_session = PromptSession(erase_when_done=True)

        self.login()

    def _print_menu(self):
        print(f"=== {self.__username if self.__username else 'GUEST'} ===")
        print(f"1. {'log out' if self.__username else 'Log in'}")
        print("2. Group Chat")
        print("3. Whisper")
        print("4. Remote command")
        print("5. exit")

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def __invalid_input(self, prompt="Invalid answer"):
        input(f"{Fore.RED}{Style.BRIGHT}{prompt}{Style.RESET_ALL}")

    def _check_if_exit(self, user_msg):
        return user_msg.lower() == "/exit"

    def __int_input(self, length, offset=0, prompt="> "):
        while True:
            try:
                user_choice = self._user_input(prompt)

                if self._check_if_exit(user_choice):
                    return

                user_choice = int(user_choice)

                if 1 <= user_choice <= length:
                    user_choice -= offset
                    return user_choice

                self.__invalid_input()

            except ValueError:
                self.__invalid_input("Value must be an integer!")

    def __print_out_list(self, *items):
        for index, item in enumerate(items, start=1):
            print(f"{index}. {item}")

    def _user_input(self, prompt="> "):
        user_msg = self.prompt_session.prompt(prompt)
        return user_msg

    def login(self):
        user_login = self._user_input("Enter your login: ")

        response = self.__client.send_register(user_login)

        valid = response["data"]

        if valid:
            self.__username = user_login

        else:
            if response["reason"]:
                self.__invalid_input(prompt=response["reason"])

    def logout(self):
        if self.__client.send_logout():
            self.__username = None
            self._user_input("Sing out!")

        else:
            self.__invalid_input(prompt="Couldn't logout!")

    def get_name(self):
        return self.__username

    def _choose_client(self, clients_names):
        self.__print_out_list(*clients_names)

        user_choice = self.__int_input(
            len(clients_names), prompt="(/exit to leave) >", offset=1
        )

        if user_choice != None:
            return clients_names[user_choice]

    def _print_whisper(self, msg):
        print("[" + Fore.MAGENTA + "PRIVATE" + Style.RESET_ALL + "]", end=" ")
        print(Fore.MAGENTA + msg["src"] + Style.RESET_ALL + ": " + msg["data"])

    def _print_msg_with_name(self, msg):
        print(Fore.YELLOW + msg["src"] + ": " + msg["data"] + Style.RESET_ALL)

    def _print_msg(self, msg):
        if msg["action"] == "whisper":
            self._print_whisper(msg)

        elif self.__username in msg["data"]:
            self._print_msg_with_name(msg)

        else:
            print(msg["src"] + ": " + msg["data"])

    def group_chat(self):
        self.clear()

        for msg in self.__client.chat_history:
            self._print_msg(msg)

        self.__client.on_message = self._print_msg

        try:
            while True:
                user_msg = self._user_input("(/exit to leave) > ")

                if self._check_if_exit(user_msg):
                    return

                self.__client.broadcast(user_msg)

        finally:
            self.__client.on_message = None

    def whisper(self):
        self.clear()

        clients = self.__client.get_usernames()

        client = self._choose_client(clients)

        if not client:
            return

        user_msg = self._user_input()

        if self._check_if_exit(user_msg):
            return

        self.__client.send_whisper(user_msg, client)

    def remote_command(self):
        # Same idea like in whisper. Just ask for command instead.
        pass

    def start(self):
        while not self.__client.disconnected.is_set():
            self.clear()

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
                        self.group_chat()
                    else:
                        self.__invalid_input()

                case "3":
                    if logged:
                        self.whisper()
                    else:
                        self.__invalid_input()

                case "4":
                    if logged:
                        self.remote_command()
                    else:
                        self.__invalid_input()

                case "5":
                    self.__client.cleanup()
                    break

                case _:
                    self.__invalid_input()
