import base64
import socket
import json
from datetime import datetime
import sys
import picar_4wd as fc
import cv2

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address

CAMERA_ID = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

HOST = get_ip_address()
PORT = 65432

power_val = 50
direction = "STOP"
invert_turns = False 

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


def take_pic(flip_frame=False):
    cap = cv2.VideoCapture(CAMERA_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    print("camera turned on")
    success, frame = cap.read()
    cap.release()  # Don't forget to release the camera resource

    if not success:
        sys.exit("ERROR: Unable to read from camera.")

    if flip_frame:
        frame = cv2.rotate(frame, cv2.ROTATE_180)

    # Encode the frame as a JPEG
    success, jpeg_frame = cv2.imencode('.jpg', frame)
    if not success:
        print("ERROR: Could not encode frame.")
        return None
    
    # Convert the JPEG frame to base64
    jpeg_base64 = base64.b64encode(jpeg_frame.tobytes()).decode('utf-8')

    # Return the base64-encoded image
    return jpeg_base64


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
                    status = fc.pi_read()
                elif data == "TAKE_PIC":
                    image_base64 = take_pic(False)
                    if image_base64:
                        response = {"image": image_base64}
                    else:
                        response = {"error": "Failed to capture image"}
                    status = fc.pi_read()
                else:
                    control_car(data)
                    status = fc.pi_read()
                
                response = json.dumps(status)
                print(f"Sending response: {response}")
                client.sendall(response.encode() + b'\n')
        except Exception as e: 
            print(f"An error occurred: {e}")
        finally:
            print("Closing connection")
            client.close()
