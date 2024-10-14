import sys

import socket
import threading
from collections import deque
import signal
import time

#MODEL = 'Picarx'
MODEL = 'Picar_4WD'

if MODEL=='Picar_4WD':
    from picar import Picar

elif MODEL=='Picar_4WD':
    from picamera2 import Picamera2
    sys.path.insert(0, '../picarx')
    from picarx import Picarx



server_addr = 'D8:3A:DD:F5:2B:80'
server_port = 1

buf_size = 1024

client_sock = None
server_sock = None

sock = None

exit_event = threading.Event()

message_queue = deque([])
output = ""

dq_lock = threading.Lock()
output_lock = threading.Lock()

#car = Picarx()
car = Picar()

def send_msg(msg):
    global dq_lock
    dq_lock.acquire()
    message_queue.append("RPi " + str(msg) + " \r\n")
    dq_lock.release()

def handler(signum, frame):
    exit_event.set()

signal.signal(signal.SIGINT, handler)

def start_client():
    global server_addr
    global server_port
    global server_sock
    global sock
    global exit_event
    global message_queue
    global output
    global dq_lock
    global output_lock
    global car
    server_sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    server_sock.bind((server_addr, server_port))
    server_sock.listen(1)
    #server_sock.settimeout(10)
    try:    
        sock, address = server_sock.accept()
    except Exception as e:
        print(e)
        assert(0)
    print("Connected")
    server_sock.settimeout(None)
    sock.setblocking(0)
    while not exit_event.is_set():
        # send data
        if dq_lock.acquire(blocking=False):
            if(len(message_queue) > 0):
                try:
                    sent = sock.send(bytes(message_queue[0], 'utf-8'))
                except Exception as e:
                    exit_event.set()
                    continue
                if sent < len(message_queue[0]):
                    message_queue[0] = message_queue[0][sent:]
                else:
                    message_queue.popleft()
            dq_lock.release()
        
        # rec data
        if output_lock.acquire(blocking=False):
            data = ""
            try:
                try:
                    data = sock.recv(1024).decode('utf-8')
                except socket.error as e:
                    assert(1==1)
                    #no data

            except Exception as e:
                exit_event.set()
                continue
            
            output += data
            output_split = output.split("\r\n")
            for i in range(len(output_split) - 1):
                print(output_split[i])
                if 'picar' in output_split[i]:
                    cmd_split = output_split[i].split()
                    print(cmd_split)
                    getattr(car, cmd_split[2])()
                    send_msg("ACK")
                elif 'disconnect' in output_split[i]:
                    exit_event.set()
                    break
            output = output_split[-1]
            output_lock.release()

    # Close connection
    server_sock.close()
    sock.close()
    print("client thread end")
    



cth = threading.Thread(target=start_client)

cth.start()


while not exit_event.is_set():
    if sock:
        pi_data = car.get_pi_data()
        #print(pi_data)
        send_msg(f"{car.status} {car.direction} {car.update_distance()} " + \
         f"{pi_data['cpu_temperature']} {float(pi_data['cpu_usage'])*100} {pi_data['battery']}")
    time.sleep(1)

# Shutdown car connection    
del car
print("Disconnected.")
print("All done.")
