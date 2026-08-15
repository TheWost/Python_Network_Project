import threading, socket





class Server:
    """Class creates a socket that local machines can connect to and send msgs to"""
    def __init__(self, port=5000, host="0.0.0.0"):
        self.PORT = port # Holds to which PORT socket will be connected to
        self.HOST = host # Holds...
        self.clients = dict() # Holds key:client_adress value:client_socket
        self.threads = dict() # Holds key:client_adress value:thread


    def create_server(self,IPV=socket.AF_INET, PROTOCOL=socket.SOCK_STREAM):
        """This function creates socket binded to self.PORT"""
        self.server = socket.socket(IPV,PROTOCOL)
        self.server.bind((self.HOST, self.PORT))
    
    def accept_connection(self):
        self.server.listen()
        socket, adress = self.server.accept() 
        return socket, adress
    
    def handle_client(self,adress,socket):
        bytes = 1024 

        while True:
            data = socket.recv(bytes).decode()
            self.send_to_all_clients(adress,data)

    
    def send_to_all_clients(self,adress,data):
        for client in self.clients.values():
            client.send(f"({adress}) -> {data}")

            

    def main_loop(self):
        self.create_server()
        
        while True:

            socket, adress = self.accept_connection() # Adress returns tuple (IP,PORT)
            
            t = threading.Thread(
                    target=self.handle_client,
                    args=(adress,socket),
                    name=f"Thread{adress[0]}:{adress[1]}")

            clients[adress] = socket
            thread[adress] = t
            
            t.daemon()
            t.start = True


