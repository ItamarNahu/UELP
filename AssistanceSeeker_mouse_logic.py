from clientComm import Client_comm
import queue
from pynput import mouse


def main_AS_mouse(otherIP):
    port = 2001
    recv_q = queue.Queue()
    client = Client_comm(otherIP, port, recv_q)
    mouse_cont = mouse.Controller()
    # get mouse pos and funcs from queue
    while True:
        data = recv_q.get()
        if data != "close":
            x = data[:4]
            y = data[4:-1]
            type_mov = data[-1]

            # move mouse and do func based on protocol
            mouse_cont.position = (int(x), int(y))
            # left click
            if type_mov == "0":
                mouse_cont.press(mouse.Button.left)
            # right click
            elif type_mov == "1":
                mouse_cont.press(mouse.Button.right)
            # scroll up
            elif type_mov == "2":
                mouse_cont.scroll(0, 1)
            # scroll down
            elif type_mov == "3":
                mouse_cont.scroll(0, -1)
            # left release
            elif type_mov == "5":
                mouse_cont.release(mouse.Button.left)
            # right release
            elif type_mov == "6":
                mouse_cont.release(mouse.Button.right)
