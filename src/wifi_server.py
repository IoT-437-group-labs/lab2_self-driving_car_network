import socket
from datetime import datetime
import picar_4wd as fc
import sys
import tty
import termios

HOST = "192.168.68.110"  # IP address of your Raspberry PI
PORT = 65432          # Port to listen on (non-privileged ports are > 1023)

power_val = 50
invert_turns = True  # Flag to invert turn directions, True by default

print("If you want to quit, please press q")
print("Press 'i' to toggle turn inversion")

def readchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def readkey(getchar_fn=None):
    getchar = getchar_fn or readchar
    c1 = getchar()
    if ord(c1) != 0x1b:
        return c1
    c2 = getchar()
    if ord(c2) != 0x5b:
        return c1
    c3 = getchar()
    return chr(0x10 + ord(c3) - 65)

def Keyboard_control():
    global power_val, invert_turns
    while True:
        key = readkey()
        if key == '6':
            if power_val <= 90:
                power_val += 10
                print("power_val:", power_val)
        elif key == '4':
            if power_val >= 10:
                power_val -= 10
                print("power_val:", power_val)
        
        if key == 'w':
            fc.forward(power_val)
        elif key == 's':
            fc.backward(power_val)
        elif key == 'a':
            if invert_turns:
                fc.turn_right(power_val)
            else:
                fc.turn_left(power_val)
        elif key == 'd':
            if invert_turns:
                fc.turn_left(power_val)
            else:
                fc.turn_right(power_val)
        elif key == 'i':
            invert_turns = not invert_turns
            print("Turn inversion:", "ON" if invert_turns else "OFF")
        else:
            fc.stop()
        
        if key == 'q':
            print("Quitting")
            break

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
