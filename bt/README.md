# Requirement
* Python version: `>=3.9`
* PC and RaspberryPi are connected via Bluetooth

# Instruction
1. update server_addr in ui_bluetooth.py and pi_socket.py to RaspberryPi's Bluetooth MAC address
2. copy ui_bluetooth.py to PC
3. copy pi_socket.py and picar.py to RaspberryPi
4. run pi_socket.py
5. run ui_bluetooth.py
6. click "Connect" in UI
7. once connection is established, pi_socket.py will start to sream information to UI
8. click "Disconnect" to end the connection and "Close" to end the scripts on both PC and RaspberryPi
