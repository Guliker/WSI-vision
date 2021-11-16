"""
Used to connect with the customer portal script (CTO-script)
Asks for data and receives the whole product
"""

""" ----- IMPORTS ----- """
import socket
from ast import literal_eval
import numpy as np

# IJsel laptop
#HOST = '192.168.14.219'
# Christiaan laptop
#HOST = '192.168.14.174'
HOST = ''
PORT = 30000

command_message = b"asking_for_file"
command_message_cobot = b"asking_for_data"

arr = []

def ask_for_data(timeout_time=1.0):
    """
    :brief      Start connection with the socket and asking for an available block on the socket
    :return     Array of items that are the product
    """
    try:
        print(" Connecting ..."),
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(timeout_time)   # timeout for connection in seconds
        s.bind((HOST, PORT))
        s.listen(5)
        print("")
        print(" Waiting for data ..."),
        c, addr = s.accept()
        print(" Message received --") 
        recv_msg = c.recv(1024)
        print("Message: ", recv_msg)
        return literal_eval(recv_msg)
    except socket.error as socketerror:
        print("socket error")
        print(socketerror)
    return []