"""
Used to connect with the customer portal script (CTO-script)
Asks for data and receives the whole product
"""

""" ----- IMPORTS ----- """
import socket
from ast import literal_eval
# IJsel laptop
#HOST = '192.168.14.219'
# Christiaan laptop
#HOST = '192.168.14.174'
HOST = ''
PORT = 30000

command_message = b"asking_for_file"
command_message_cobot = b"asking_for_data"

def ask_for_data():
    """
    :brief      Start connection with the socket and asking for an available block on the socket
    :return     Array of items that are the product
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    print("")
    print("-- Waiting for data ..."),
    c, addr = s.accept()
    print(" Message received --") 
    try:
        recv_msg = c.recv(1024)
        print("Message: ", recv_msg)
        return literal_eval(recv_msg)
    except socket.error as socketerror:
        print("socket error")
    
    return "[]"