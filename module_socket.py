"""
Used to connect with the customer portal script (CTO-script)
Asks for data and receives the whole product
"""

""" ----- IMPORTS ----- """
import socket
from ast import literal_eval
# IJsel laptop
#HOST = '192.168.14.92'
# Christiaan laptop
HOST = '192.168.14.174'
PORT = 30000

command_message = b"asking_for_file"
command_message_cobot = b"asking_for_data"

def ask_for_data():
    """
    :brief      Start connection with the socket and asking for an available block on the socket
    :return     Array of items that are the product
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    #print("-- sending vision --")
    s.sendall(command_message)
    data = s.recv(1024)

    #print("-- data --")
    #print('Received', repr(data))

    return literal_eval(data)


def ask_for_data_cobot():
    """
    :brief      Asking for an available block on the socket
    :return     Array of items that are the product
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    #print("-- sending vision --")
    s.sendall(command_message_cobot)
