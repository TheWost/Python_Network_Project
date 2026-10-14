import os

from colorama import Fore, Style


def clear():
    os.system("clear" if os.name == "posix" else "cls")


def main():
    while True:
        clear()
        print(Fore.BLUE + "1. Server" + Style.RESET_ALL)
        print(Fore.YELLOW + "2. Client" + Style.RESET_ALL)
        print(Fore.RED + "3. Exit" + Style.RESET_ALL)

        user_choice = input(Fore.GREEN + "> " + Style.RESET_ALL)

        match user_choice.lower():
            case "1" | "server":
                from server.main import main

                clear()
                main()

            case "2" | "client":
                from client.main import main

                clear()
                main()

            case "3" | "quit" | "exit" | "disconnect" | "dsc":
                return

            case _:
                input(Fore.RED + "Invalid" + Style.RESET_ALL)

        clear()


if __name__ == "__main__":
    main()
