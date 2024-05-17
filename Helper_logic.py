import queue
import threading

from Monitor_Keyboard import Keyboard_monitor
from Monitor_Mouse import Mouse_monitor
from Servercomm import Server_comm


def check(check_queue, listener):
    """
    Function checks if Assistance Seeker client disconnected from server, if yes stop listener for keyboard/mouse
    :param check_queue: queue for comm between server object and logic
    :param listener: listener object of keyboard/mouse to listen to computer
    """
    while True:
        data, ip = check_queue.get()
        if data == "disconnect":
            listener.stop_listening()
            break


def main_Helper(otherIP, port, close_queue):
    """
    Main helper function, run listener for mouse or keyboard based on server port and start thread
    for checking disconnect from server
    :param otherIP: ip of Assistance Seeker client that needs to connect to server 
    :param port: port Helper server runs on
    :param close_queue: multiprocessing queue for Keyboard listener, to send close session request to main client to
     terminate all running proccesses
    """
    check_queue = queue.Queue()
    # create new server and monitor mouse or keyboard based on port gotten
    # start thread for checking disconnect client from server
    server = Server_comm(check_queue, port, otherIP)
    if port == 2001:
        mouse = Mouse_monitor(server, otherIP)
        threading.Thread(target=check, args=(check_queue, mouse,)).start()
    elif port == 2002:
        keyboard = Keyboard_monitor(server, otherIP, close_queue)
        threading.Thread(target=check, args=(check_queue, keyboard,)).start()
