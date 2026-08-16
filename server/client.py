"""Client.py is used to connect with server.py and send msgs."""

import socket, threading, json



# Client will work on two threads
#   1. Takes care of reciving messages 
#   2. Takes care of taking user output and sending into server or any desired PORT





class Client:
    """ARGS:
        address: str
        socket.

        Holds values esseintal for client to recive and send packets."""
    def __init__(self, port, host, IPV=socket.AF_INET, PROTOCOL=socket.SOCK_STREAM):
        self.socket = socket.socket(IPV,PROTOCOL)
        self.HOST = host
        self.PORT = port
        self.thread = None
    
    def connect_host(self):
        self.socket.connect((self.HOST, self.PORT))
    def cleanup(self):
        self.socket.close()

    def recive_msg(self):

        bytes = 1024
        try: 
            while True:
                raw_data = self.socket.recv(bytes)
                
                if not raw_data:
                    break                   
                
                data = raw_data.decode()
                print(data)

        except (ConnectionResetError, BrokenPipeError, socket.error):
            print("Connection Error from host side!")

        finally:
            self.cleanup()

    def send_msg(self):
        try:


            while True:        
                user_input = input("> ").encode()
                self.socket.sendall(user_input)
        
        except KeyboardInterrupt:
            print("\n-- ^C stopping connection...")
        
        finally:
            self.cleanup()
            print("-- Connection closed.")


    def run(self):
        self.connect_host()

        self.thread = threading.Thread(target=self.recive_msg)
        self.thread.daemon = True
        self.thread.start()

        self.send_msg()

            


        
def main():
    server_config_path = "server_config.json"

    with open(server_config_path) as f:
        server_config = json.load(f)["client"]


    Client(**server_config).run()



if __name__ == "__main__":
    main()
