"""This code dosen't have exit program. It will run forever untill program will get KeyInterupted/Closed. Threads won't close automaticly, python and linux will close them after a 1 min after closing program."""

from server.server import Server


def main():
    """Runs program"""
    server = Server.load_from_config()

    server.start()


if __name__ == "__main__":
    main()
