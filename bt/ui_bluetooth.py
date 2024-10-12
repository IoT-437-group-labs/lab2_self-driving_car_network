import sys
import socket
import threading
from collections import deque
import signal
import time
import tkinter as tk


server_addr = 'D8:3A:DD:A1:F1:04'
server_port = 1

buf_size = 1024

client_sock = None
server_sock = None
sock = None

exit_event = threading.Event()
ack_event = threading.Event()

message_queue = deque([])
output = ""

dq_lock = threading.Lock()
output_lock = threading.Lock()

def handler(signum, frame):
    exit_event.set()

signal.signal(signal.SIGINT, handler)

def send_msg(msg, wait_ack=False):
    print(f"send {msg}")
    global dq_lock
    dq_lock.acquire()
    message_queue.append("PC " + str(msg) + " \r\n")
    dq_lock.release()
    if wait_ack and not ack_event.wait(timeout=3):
        assert(0)
    ack_event.clear()

def start_client():
    global sock
    global dq_lock
    global output_lock
    global exit_event
    global message_queue
    global output
    global server_addr
    global server_port
    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    sock.settimeout(10)
    sock.connect((server_addr,server_port))
    sock.settimeout(None)
    print("after connect")
    sock.setblocking(False)
    while not exit_event.is_set():
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
        
        if output_lock.acquire(blocking=False):
            data = ""
            try:
                try:
                    data = sock.recv(1024).decode("utf-8")
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
                if 'RPi ACK' in output_split[i]:
                    ack_event.set()
                else:
                    car_info = output_split[i].split()
                    update_car_info(car_info)
            output = output_split[-1]
            output_lock.release()
    sock.close()
    print("client thread end")

def update_car_info(car_info):
    lbl_status_value["text"] = car_info[1]
    lbl_dir_value["text"] = car_info[2]
    lbl_dist_value["text"] = f"{float(car_info[3]):.2f} CM"
    lbl_temp_value["text"] = f"{car_info[4]} C"
    lbl_usage_value["text"] = f"{float(car_info[5]):.2f}%"
    lbl_battery_value["text"] = f"{car_info[6]}V/8.4V"

def connect():
    if btn_conn["text"] == "Connect":
        cth = threading.Thread(target=start_client)
        cth.start()
        lbl_connection_value["text"] = "Connected"
        btn_conn["text"] = "Disconnect"
    elif btn_conn["text"] == "Disconnect":
        send_msg('disconnect')
        exit_event.set()
        lbl_connection_value["text"] = "Disconnected"
        btn_conn["text"] = "Close"
    elif btn_conn["text"] == "Close":
        global window
        #window.quit()
        window.destroy()
        sys.exit(0)
    else:
        assert(0)

def stop():
    send_msg('picar stop', True)

def forward():
    send_msg('picar forward', True)

def backward():
    send_msg('picar backward', True)

def turnright():
    send_msg('picar turnright', True)

def turnleft():
    send_msg('picar turnleft', True)
    

# Create a new window with the title "Address Entry Form"
window = tk.Tk()
window.title("Picar Bluetooth Controller")

# Create a new frame `frm_info` to contain the
# information
frm_info = tk.Frame(relief=tk.SUNKEN, borderwidth=3)
# Pack the frame into the window
frm_info.pack()

lbl_connection = tk.Label(master=frm_info, text=f"Connection:")
# Use the grid geometry manager to place the Label and
# Entry widgets in the first row of the grid
lbl_connection.grid(row=0, column=0, sticky="e")
lbl_connection_value = tk.Label(master=frm_info, text=f"Disconnected")
lbl_connection_value.grid(row=0, column=1)

lbl_status = tk.Label(master=frm_info, text=f"Status:")
lbl_status.grid(row=1, column=0, sticky="e")
lbl_status_value = tk.Label(master=frm_info, text="")
lbl_status_value.grid(row=1, column=1)

lbl_dir = tk.Label(master=frm_info, text=f"Direction:")
lbl_dir.grid(row=2, column=0, sticky="e")
lbl_dir_value = tk.Label(master=frm_info, text="")
lbl_dir_value.grid(row=2, column=1)

lbl_dist = tk.Label(master=frm_info, text=f"Total travel distance:")
lbl_dist.grid(row=3, column=0, sticky="e")
lbl_dist_value = tk.Label(master=frm_info, text="")
lbl_dist_value.grid(row=3, column=1)

lbl_temp = tk.Label(master=frm_info, text=f"CPU Temperature:")
lbl_temp.grid(row=4, column=0, sticky="e")
lbl_temp_value = tk.Label(master=frm_info, text="")
lbl_temp_value.grid(row=4, column=1)

lbl_usage = tk.Label(master=frm_info, text=f"CPU Usage:")
lbl_usage.grid(row=5, column=0, sticky="e")
lbl_usage_value = tk.Label(master=frm_info, text="")
lbl_usage_value.grid(row=5, column=1)

lbl_battery = tk.Label(master=frm_info, text=f"Battery:")
lbl_battery.grid(row=6, column=0, sticky="e")
lbl_battery_value = tk.Label(master=frm_info, text="")
lbl_battery_value.grid(row=6, column=1)


# Create a new frame `frm_btn_conn` to contain the
# button for socket connection. This frame fills the
# whole window in the horizontal direction and has
# 5 pixels of horizontal and vertical padding.
frm_btn_conn = tk.Frame()
frm_btn_conn.pack(fill=tk.X, ipadx=5, ipady=5)

# Create the "Connect" button and pack it to the
# left side of `frm_buttons`
btn_conn = tk.Button(master=frm_btn_conn, text="Connect", command=connect)
btn_conn.pack(side=tk.LEFT, padx=10, ipadx=10)

frm_buttons = tk.Frame()
frm_buttons.pack()

btn_stop = tk.Button(master=frm_buttons, text="Stop", command=stop)
btn_stop.grid(row=1, column=1)
btn_forward = tk.Button(master=frm_buttons, text="Forward", command=forward)
btn_forward.grid(row=0, column=1)
btn_backward = tk.Button(master=frm_buttons, text="Backward", command=backward)
btn_backward.grid(row=2, column=1)
btn_turnright = tk.Button(master=frm_buttons, text="Turn Right", command=turnright)
btn_turnright.grid(row=1, column=2)
btn_turnleft = tk.Button(master=frm_buttons, text="Turn Left", command=turnleft)
btn_turnleft.grid(row=1, column=0)

window.mainloop()
