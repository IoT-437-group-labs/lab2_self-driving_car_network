import socket

HOST = "192.168.68.110"  # IP address of your Raspberry PI
PORT = 65432          # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"Connected to {HOST}:{PORT}")
    
    while True:
        text = input("Enter your message (or 'quit' to exit): ")
        if text.lower() == "quit":
            break
        s.sendall(text.encode())     # send the encoded message (send in binary format)

        try:
            data = s.recv(1024)
            if not data:
                print("Server closed the connection.")
                break
            print("Received from server:", data.decode())
        except ConnectionResetError:
            print("Server closed the connection unexpectedly.")
            break

print("Closing connection")