import os
from pathlib import Path

class Tui:
    def __init__(self):
        self.__name = None





    def _print_menu(self):
        print(f"=== {self.__name if self.__name else "GUEST"} ===")
        print(f"1. {"log out" if self.__name else "Log in}"}")
        print("2. Group Chat")
        print("3. Whisper")
        print("4. Remote command")
        print("5. exit")

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")


    def _check_leave_command(self, text):
        if text.startswith("EXIT"):
            return True
        return False

    def login(self):
        pass

    def logout(self):
        pass

    def group_chat(self):
        pass

    def whisper(self):
        pass

    def remote_command(self):
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






