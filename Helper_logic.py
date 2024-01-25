import queue
from Monitor_Mouse import Mouse_monitor
from Servercomm import Server_comm
import multiprocessing
from Monitor_Keyboard import Keyboard_monitor

if __name__ == '__main__':
    # change once start multiprocessing
    otherIP = "192.168.4.97"
    port = 2001

    # create new server and monitor mouse or keyboard based on port gotten
    recv_q = queue.Queue()
    server = Server_comm(recv_q, port, otherIP)
    if port == 2001:
        Mouse_monitor(server, otherIP)
    elif port == 2002:
        Keyboard_monitor(server, otherIP)