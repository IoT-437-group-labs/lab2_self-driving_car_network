import socket
from datetime import datetime

HOST = "192.168.68.110"  # IP address of your Raspberry PI
PORT = 65432          # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")
    
    client, clientInfo = s.accept()
    print("Connected by", clientInfo)
    
    try:
        while True:
            data = client.recv(1024)      # receive 1024 Bytes of message in binary format
            if not data:
                break
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] Received: {data.decode()}")
            client.sendall(data) # Echo back to client
    except Exception as e: 
        print(f"An error occurred: {e}")
    finally:
        print("Closing connection")
        client.close()