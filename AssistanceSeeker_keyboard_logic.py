from clientComm import Client_comm
import queue
from pynput import keyboard
import keyboard as Keyboard
import threading
from pynput.keyboard import Key
import AssistanceSeeker_protocol as protocol


def check_close(close_queue, client):
    while True:
        if Keyboard.is_pressed("shift+ctrl+d"):
            close_queue.put("close")
            client.close()
            break


def main_AS_keyboard(otherIP, close_queue):
    port = 2002
    recv_q = queue.Queue()
    client = Client_comm(otherIP, port, recv_q)
    keyboard_cont = keyboard.Controller()
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
    closed = threading.Thread(target=check_close, args=(close_queue, client,))
    closed.start()
    while True:
        data = recv_q.get()
        if data != "close":
            opcode, key_val = protocol.unpackData(data)
            key_val = int(key_val)
            if key_val == 9999999:
                print("released end")
                keyboard_cont.release(Key.shift)
                keyboard_cont.release(Key.ctrl)
                keyboard_cont.release("d")
                break
            if key_val in special_keys_mapping.keys():
                key = special_keys_mapping[key_val]
            else:
                if 0 < key_val < 27:
                    key_val += 96
                key = chr(key_val)

            if opcode == "01":
                print(key)
                keyboard_cont.press(key)
            elif opcode == "02":
                keyboard_cont.release(key)
                print(key)
        else:
            break
