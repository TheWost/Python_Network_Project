import threading, socket


class Client:
    def __init__(self,socket,address, server):
        self.socket = socket
        self.address = address
        self.thread = None
        self.server = server
    
    def recive_msg(self):
        bytes = 1024

        while True:
            data = self.socket.recv(bytes).decode()
            self.server.send_to_all_clients(self.address,data)

class Server:
    """Class creates a socket that local machines can connect to and send msgs to"""
    def __init__(self, port=5000, host="0.0.0.0"):
        self.PORT = port # Holds to which PORT socket will be connected to
        self.HOST = host # Holds...
        self.clients = dict() # Holds key:client_address value:client_socket


    def create_server(self,IPV=socket.AF_INET, PROTOCOL=socket.SOCK_STREAM):
        """This function creates socket binded to self.PORT"""
        self.server = socket.socket(IPV,PROTOCOL)
        self.server.bind((self.HOST, self.PORT))
    
    def accept_connection(self):
        self.server.listen()
        return Client(*self.server.accept(),self)
        
    
    def send_to_all_clients(self,address,data):
        for client in self.clients.values():
            client.socket.send(f"({address}) -> {data}".encode())


            

    def main_loop(self):
        self.create_server()
        
        while True:

            client = self.accept_connection() # Adress returns tuple (IP,PORT)
            
            client.thread = threading.Thread(
                    target=client.recive_msg,
                    name=f"Thread{client.address[0]}:{client.address[1]}")

            self.clients[client.address] = client
            
            client.thread.daemon = True
            client.thread.start()


