# IMPORANT NOTE:
# This code dosen't have exit program. It will run forever untill program will get KeyInterupted/Closed. Threads won't close automaticly, python and linux will close them after a 1 min after closing program.

#TODO
# Add Try/except/finally. Inside finally when code gets closed terminate all theards
# When user gets disconnected/leaves add code that will detect that and remove him from chat

#FUTURE
# Fix terminal issue with typing
# Add whisper/private chat
# Log chat like discord does ;)
# Add command usage (os.system())




import threading, socket

class Client:
    """ARGS:
        socket: socket
        address: str
        server: Server

        Holds values esseintal for client to recive and send packets."""
    def __init__(self,socket,address, server):
        self.socket = socket
        self.address = address
        self.thread = None
        self.server = server
    
    def cleanup(self):
        del self.server.clients[self.address] 
        self.socket.close()
        del self

    def recive_msg(self):

        bytes = 1024
        while True:
            try: 
                raw_data = self.socket.recv(bytes)
                
                if not raw_data:
                    break                   
                
                data = raw_data.decode()
                self.server.send_to_all_clients(self.address,data)

            except (ConnectionResetError, BrokenPipeError, socket.error):
                break

        self.cleanup() 



class Server:
    """Class creates a socket that local machines can connect to and send msgs to"""
    def __init__(self, port=5000, host="0.0.0.0"):
        self.PORT = port # Holds to which PORT socket will be connected to
        self.HOST = host # Holds...
        self.clients = dict() # Holds key:client_address value:client_socket


    def create_server(self,IPV=socket.AF_INET, PROTOCOL=socket.SOCK_STREAM):
        self.server = socket.socket(IPV,PROTOCOL)
        self.server.bind((self.HOST, self.PORT))
    
    def accept_connection(self):
        self.server.listen()
        return Client(*self.server.accept(),self)
        
    
    def send_to_all_clients(self,address,data):
        for client in self.clients.values():
            client.socket.send(f"({address}) -> {data}".encode())


    def connection_loop(self):
        self.create_server()
        
        while True:

            client = self.accept_connection() # Adress returns tuple (IP,PORT)
            
            client.thread = threading.Thread(
                    target=client.recive_msg,
                    name=f"Thread{client.address[0]}:{client.address[1]}")

            self.clients[client.address] = client
            
            client.thread.daemon = True
            client.thread.start()


def main():
    Server().connection_loop()


if __name__ == "__main__":
    main()
