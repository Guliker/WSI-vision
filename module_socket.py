"""
Used to connect with the customer portal script (CTO-script)
Asks for data and receives the whole product
"""

""" ----- IMPORTS ----- """
import config as cfg
import socket
import time
from ast import literal_eval
""" ----- ----- ----- """

arr = []

def ask_for_data(timeout_send=1.0, timeout_receive=5.0):
    """
    :brief      Start connection with the socket and asking for an available block on the socket
    :return     Array of items that are the product
    """
    # send data request
    #print("")
    #print("Sending ... "),
    msg = send_request(timeout_send, timeout_receive)
    #print("Done")
    return msg
    
def send_request(timeout_send, timeout_receive):
    """
    :brief      Send to the cto a request for data
    :return     If the request was succesfull
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout_send)   # timeout for connection in seconds
        s.connect((cfg.HOST_send, cfg.PORT))
        s.sendall(str(cfg.command_message_vision))
        s.settimeout(timeout_receive)
        print("Receiving ... "),
        recv_msg = s.recv(1024)
        s.close()
        print(recv_msg)
        return literal_eval(recv_msg)
    except socket.error as socketerror:
        s.close()
        return []
    
def receive_data(timeout_time=1.0):
    """
    :brief      Send to the cto a request for data
    :return     If the request was succesfull
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(timeout_time)   # timeout for connection in seconds
        s.bind((cfg.HOST, cfg.PORT))
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
    