from colorama import Fore, Style

from utils import clear


def main():
    while True:
        clear()
        print(Fore.BLUE + "1. Server" + Style.RESET_ALL)
        print(Fore.GREEN + "2. Client" + Style.RESET_ALL)
        print(Fore.YELLOW + "3. Connection config" + Style.RESET_ALL)
        print(Fore.RED + "4. Exit" + Style.RESET_ALL)

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

            case "3":
                from configs.set_up_config import set_up_config

                clear()
                set_up_config()

            case "4" | "quit" | "exit" | "disconnect" | "dsc":
                return

            case _:
                input(Fore.RED + "Invalid" + Style.RESET_ALL)

        clear()


if __name__ == "__main__":
    main()
