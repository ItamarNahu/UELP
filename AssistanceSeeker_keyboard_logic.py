from clientComm import Client_comm
import queue
from pynput import keyboard
import keyboard as Keyboard
import threading
from pynput.keyboard import Key
import AssistanceSeeker_protocol as protocol


def check_close(close_queue, client):
    """
    Function waits until detected close session combo closes client and puts close in close queue
    :param close_queue: multiprocessing queue between main client and keyboard process to
    let main client know when to close session
    :param client: client object to comm with server
    """
    while True:
        if Keyboard.is_pressed("shift+ctrl+d"):
            close_queue.put("close")
            client.close()
            break


def main_AS_keyboard(otherIP, close_queue):
    """
    Function controls keyboard click and releases gotten from Helper, unpack data and register
    key click on computer keyboard
    :param otherIP: ip of server of Keyboard helper 
    :param close_queue: multiprocessing queue between main client and keyboard process to
    let main client know when to close session
    """
    port = 2002
    recv_q = queue.Queue()
    client = Client_comm(otherIP, port, recv_q)

    # keyboard controller object
    keyboard_cont = keyboard.Controller()

    # values for keys who do not have values in pynput
    special_keys_mapping = {
        1114112: Key.ctrl_l,
        1114113: Key.ctrl_r,
        1114114: Key.shift_l,
        1114115: Key.shift_r,
        1114116: Key.alt_l,
        1114117: Key.alt_r,
        1114118: Key.cmd,
        1114119: Key.cmd_l,
        1114120: Key.cmd_r,
        1114121: Key.enter,
        1114122: Key.backspace,
        1114123: Key.tab,
        1114124: Key.space,
        1114125: Key.delete,
        1114126: Key.esc,
        1114127: Key.f1,
        1114128: Key.f2,
        1114129: Key.f3,
        1114130: Key.f4,
        1114131: Key.f5,
        1114132: Key.f6,
        1114133: Key.f7,
        1114134: Key.f8,
        1114135: Key.f9,
        1114136: Key.f10,
        1114137: Key.f11,
        1114138: Key.f12,
        1114139: Key.home,
        1114140: Key.end,
        1114141: Key.page_up,
        1114142: Key.page_down,
        1114143: Key.insert,
        1114144: Key.menu,
        1114145: Key.caps_lock,
        1114146: Key.num_lock,
        1114147: Key.scroll_lock,
        1114148: Key.pause,
        1114149: Key.print_screen,
        1114150: Key.shift,
        1114151: Key.ctrl,
        1114152: Key.alt,
        1114153: Key.up,
        1114154: Key.down,
        1114155: Key.left,
        1114156: Key.right}

    # start thread for checking close session combo and comm with main client
    closed = threading.Thread(target=check_close, args=(close_queue, client,))
    closed.start()

    while True:
        data = recv_q.get()
        if data != "close":
            opcode, key_val = protocol.unpackData(data)
            key_val = int(key_val)
            # gotten end session opcode from Helper, release end session combo and end loop
            if key_val == 9999999:
                keyboard_cont.release(Key.shift)
                keyboard_cont.release(Key.ctrl)
                keyboard_cont.release("d")
                print("released end session combo")
                break
            # check if value gotten is registered in special keys and translate to key accordingly
            if key_val in special_keys_mapping.keys():
                key = special_keys_mapping[key_val]
            else:
                # add value for keys gotten between 0 and 27 as
                # these keys are (Ctrl + key) and are not registered correctly in pynput
                if 0 < key_val < 27:
                    key_val += 96
                key = chr(key_val)

            # check if key is released or clicked and change computer keyboard accordingly
            if opcode == "01":
                keyboard_cont.press(key)
                print("pressed " + key)
            elif opcode == "02":
                keyboard_cont.release(key)
                print("released " + key)
        else:
            break
