"""
Used to connect with the customer portal script (CTO-script)
Asks for data and receives the whole product
"""

""" ----- IMPORTS ----- """
import socket

HOST = '192.168.14.92'
PORT = 30000

command_message = b"asking_for_file"

def init():
    """
    :brief      Start connection with the socket
    :return     The socket that is connected to
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    return s

def ask_for_data(s):
    """
    :brief      Asking for an available block on the socket
    :return     Array of items that are the product
    """
    #print("-- sending vision --")
    s.sendall(command_message)
    data = s.recv(1024)

    #print("-- data --")
    #print('Received', repr(data))

    return data