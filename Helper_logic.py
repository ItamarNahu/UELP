from Monitor_Mouse import Mouse_monitor
from Servercomm import Server_comm
from Monitor_Keyboard import Keyboard_monitor
import queue
import threading


def check(check_queue, listener):
    while True:
        data, ip = check_queue.get()
        if data == "disconnect":
            listener.stop_listening()
            break


def main_Helper(otherIP, port, close_queue):
    check_queue = queue.Queue()
    # create new server and monitor mouse or keyboard based on port gotten
    server = Server_comm(check_queue, port, otherIP)
    if port == 2001:
        mouse = Mouse_monitor(server, otherIP)
        threading.Thread(target=check, args=(check_queue, mouse,)).start()
    elif port == 2002:
        keyboard = Keyboard_monitor(server, otherIP, close_queue)
        threading.Thread(target=check, args=(check_queue, keyboard,)).start()
