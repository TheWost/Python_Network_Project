import threading, time, socket

class Utils:
    @staticmethod
    def loading_anim(stop_event,text):
        """FUNCTION USED WITHIN A THREAD"""
        animation = ["|", "/", "-", "\\"]
        idx = 0
        
        def anim(i):
            return animation[i % len(animation)]

        while not stop_event.is_set():
            print(f"\r{text}... [{anim(idx) * 3}]", end ="", flush=True)
            time.sleep(0.1)
            idx += 1

## Config
class Connection:
    def __init__(self,adress,port,protocol=socket.SOCK_STREAM):
        self.ADRESS = adress
        self.PORT = port
        self.server = socket.socket(socket.AF_INET, protocol)

        

    def bind(self):
        self.server.bind((self.ADRESS,self.PORT))

    def connect(self):
        self.bind()
        
        stop_event = threading.Event() # Stop event flag

        print_loading = threading.Thread(target=Utils.loading_anim, args=(stop_event, "Waiting for connection..."))
        print_loading.start()

        try:

            self.server.listen()
            client_socket, client_adress = self.server.accept()
            
        finally:
            stop_event.set()
            print_loading.join()

        print("[+] Connected!")
        return client_socket, client_adress
        


class Chat:
    def __init__(self,client_socket, client_adress):
        self.client_socket = client_socket
        self.client_adress = client_adress
    


    def msg_listener(self):
        
        # Gets client msgs in background thread
        def background_msg_listener(client_socket, client_address):
            max_bytes = 1024
            while True:
                try:
                    data = client_socket.recv(max_bytes)
                    
                    # Handle client disconnection
                    if not data:
                        print(f"\n[{client_address}] Disconnected.")
                        break
                        
                    print(f"\n({client_address}) -> {data.decode()}\n")
                except ConnectionResetError:
                    print(f"\n[{client_address}] Connection lost unexpectedly.")
                    break
        # Program freezes while waiting for msg
        client_msg = threading.Thread(
            target=background_msg_listener,
            args=(self.client_socket, self.client_adress)
        )
        client_msg.daemon = True 
        client_msg.start()


    def start_chat(self):
                
        self.msg_listener()

        while True:
            user_input = input("> ")
            if user_input.strip():
                self.client_socket.send(user_input.encode())






def main():
    PORT = 5000
    ADRESS = "0.0.0.0"
    chat = Chat(*Connection(ADRESS,PORT).connect())
    chat.start_chat()

if __name__ == "__main__":
    main()



