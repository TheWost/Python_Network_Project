import os
from pathlib import Path
from colorama import init, Fore, Style
import json
from configs.config import Config
from classes.message import msg 
from client.client import Client


init(autostart=True)

class Tui:
    def __init__(self):
        self.__name = None
        self.__config = Config("tui_settings").load_data()
        self.__client = Client()

    def _print_menu(self):
        print(f"=== {self.__name if self.__name else "GUEST"} ===")
        print(f"1. {"log out" if self.__name else "Log in}"}")
        print("2. Group Chat")
        print("3. Whisper")
        print("4. Remote command")
        print("5. exit")

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def __invalid_input(prompt="Invalid answer"):
        input(f"{Fore.RED}{Style.BRIGHT}{prompt}")

    def _check_if_exit(self, user_msg):
        return user_msg.lower() == "exit"

    def __return_if_exit(self,user_msg):
        if self._check_if_exit(user_msg):
            break

    def __int_input(self, length, prompt = "> "):
        try:

            user_choice = int(input(prompt))


            if 1 <= user_choice <= length:
                return user_choice

            self.__invalid_input()


        except ValueError:
            self.__invalid_input("Value must be an integer!")

    def __print_out_list(self, *items):
        for index,item in enumerate(items, start=1):
            print(f"{index}. {item}")


    def login(self):
        user_login = input("Enter your login: ")
        self.__name = user_login

    def logout(self):
        self.__name = None
        input("Sing out!")

    def get_name(self):
        return self.__name



    def group_chat(self):
        while True:

            user_msg = input("> ")
            self.__return_if_exit(user_msg)
            pass # Need to implement from client send to everyone


    def _choose_client(self, client_names):
        self.__print_out_list(*clients_names)
        user_choice = self.__int_input() # Here we need to add len(clients_names)
        return clients_name[user_choice]


    def whisper(self):
        # clients = Need to ask server for list of clients names
        client = _choose_client() # need to put clients_names
        # here needs to add creating a msg
        # Then use self.__return_if_exit

    def remote_command(self):
        # Same idea like in whisper. Just ask for command instead. 
        pass


    def run(self):
        while True:

            self.clear()

            self._print_menu()
            user_choice = input("> ")

            match user_choice:

                case "1":
                    if self.__name:
                        self.logout()
                    else:
                        self.login()

                case "2":
                    self.group_chat()

                case "3":
                    self.whipser()

                case "4":
                    self.remote_command()

                case "5":
                    break

                case _:
                    input("Invalid answer")






