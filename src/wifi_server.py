import socket
import json
from datetime import datetime
import picar_4wd as fc
import os

HOST = "192.168.68.110"  # IP address of your Raspberry PI
PORT = 65432             # Port to listen on (non-privileged ports are > 1023)

power_val = 50
direction = "STOP"
invert_turns = False  # Default inversion state

def control_car(command):
    global direction, power_val, invert_turns
    print(f"Controlling car with command: {command}")
    
    if command == "w":
        fc.forward(power_val)
        direction = "FORWARD"
    elif command == "s":
        fc.backward(power_val)
        direction = "BACKWARD"
    elif command == "a":
        if invert_turns:
            fc.turn_right(power_val)
            direction = "RIGHT"
        else:
            fc.turn_left(power_val)
            direction = "LEFT"
    elif command == "d":
        if invert_turns:
            fc.turn_left(power_val)
            direction = "LEFT"
        else:
            fc.turn_right(power_val)
            direction = "RIGHT"
    elif command == "i":
        invert_turns = not invert_turns
        print(f"Turn inversion set to: {invert_turns}")
    elif command == "q":
        fc.stop()
        direction = "STOP"
    else:
        print(f"Unknown command: {command}")

def get_cpu_temperature():
    try:
        # Read the CPU temperature from the system
        temp_str = open("/sys/class/thermal/thermal_zone0/temp").readline()
        return round(float(temp_str) / 1000, 2)  # Convert to Celsius
    except Exception as e:
        print(f"Error reading CPU temperature: {e}")
        return "N/A"

def get_status():
    return {
        "direction": direction,
        "speed": power_val,
        "temperature": get_cpu_temperature(),
        "invert_turns": invert_turns  
    }

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")
    
    while True:
        client, clientInfo = s.accept()
        print("Connected by", clientInfo)
        
        try:
            while True:
                data = client.recv(1024).decode().strip()
                if not data:
                    break
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] Received: {data}")
                
                if data == "STATUS":
                    status = get_status()
                else:
                    control_car(data)
                    status = get_status()
                
                response = json.dumps(status)
                print(f"Sending response: {response}")
                client.sendall(response.encode() + b'\n')
        except Exception as e: 
            print(f"An error occurred: {e}")
        finally:
            print("Closing connection")
            client.close()
