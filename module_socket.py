"""
Used to connect with the customer portal script (CTO-script)
Asks for data and receives the whole product
"""

""" ----- IMPORTS ----- """
import socket
import time
from ast import literal_eval
# IJsel laptop
#HOST = '192.168.14.219'
# debug laptop
#HOST = '192.168.14.174'
HOST = ''
PORT = 30001
HOST_send = '192.168.14.219'


command_message = b"asking_for_file"
command_message_cobot = b"asking_for_data"

arr = []

def ask_for_data(timeout_time=1.0):
    """
    :brief      Start connection with the socket and asking for an available block on the socket
    :return     Array of items that are the product
    """
    # send data request
    msg = []
    print("")
    print("Sending ... "),
    succes = send_request(timeout_time)
    if(succes):
        print("Receiving ... "),
        time.sleep(0.1)
        msg = receive_data()
    print("Done")
    return msg
    
def send_request(timeout_time=1.0):
    """
    :brief      Send to the cto a request for data
    :return     If the request was succesfull
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout_time)   # timeout for connection in seconds
        s.connect((HOST_send, PORT))
        s.sendall(str("asking_for_file"))
        s.close()
        return True
    except socket.error as socketerror:
        print(""),
        s.close()
        return False
    
def receive_data(timeout_time=1.0):
    """
    :brief      Send to the cto a request for data
    :return     If the request was succesfull
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(timeout_time)   # timeout for connection in seconds
        s.bind((HOST, PORT))
        s.listen(5)
        c, addr = s.accept()
        recv_msg = c.recv(1024)
    except socket.error as socketerror:
        print(socketerror),
        
    try:
        s.close()
        c.close()
        return literal_eval(recv_msg)
    except NameError:
        return []
    