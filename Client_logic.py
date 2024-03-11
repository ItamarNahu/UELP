import Client_protocol as Protocol
import queue
import threading
from clientComm import Client_comm
from getmac import get_mac_address as gma
import wx
import graphics
from pubsub import pub
import multiprocessing
import Helper_logic
import Helper_screen_logic
import AssistanceSeeker_keyboard_logic
import AssistanceSeeker_mouse_logic
import AssistanceSeeker_screen_logic


def handleMsgs(client, recv_q):
    while True:
        data = recv_q.get()
        if data == "close":
            break
        else:
            opcode, params = Protocol.unpackData(data)
            print(params)
            commands[opcode](params)


def send_mac(client):
    mac_address = gma()
    client.send(Protocol.pack_mac_addr(mac_address))


def handle_login_ans(params):
    login_ans = params[0]
    wx.CallAfter(pub.sendMessage, "login_ans", ans=login_ans)


def handle_signup_ans(params):
    signup_ans = params[0]
    wx.CallAfter(pub.sendMessage, "signup_ans", ans=signup_ans)


def handle_typeUser_ans(params):
    typeUser_ans = params[0]
    wx.CallAfter(pub.sendMessage, "typeUser_ans", ans=typeUser_ans)


def handle_getCode_ans(params):
    getCode_ans = params[0]
    wx.CallAfter(pub.sendMessage, "gotten_code", ans=getCode_ans)


def handle_code_ans(params):
    code_ans = params[0]
    wx.CallAfter(pub.sendMessage, "code_ans", ans=code_ans)


def check_closed(close_queue, mouse, screen):
    while True:
        data = close_queue.get()
        if data == "close":
            mouse.terminate()
            screen.terminate()
            print(33333)
            break


def handle_conData(params):
    otherIP = params[0]
    user_Type = params[1]
    if user_Type:
        close_queue = multiprocessing.Queue()
        if user_Type == "H":
            mouse = multiprocessing.Process(target=Helper_logic.main_Helper, args=(otherIP, 2001, None,))
            keyboard = multiprocessing.Process(target=Helper_logic.main_Helper, args=(otherIP, 2002, close_queue,))
            screen = multiprocessing.Process(target=Helper_screen_logic.main_Helper_screen, args=(otherIP,))
        elif user_Type == "A":
            mouse = multiprocessing.Process(target=AssistanceSeeker_mouse_logic.main_AS_mouse, args=(otherIP,))
            keyboard = multiprocessing.Process(target=AssistanceSeeker_keyboard_logic.main_AS_keyboard,
                                               args=(otherIP, close_queue,))
            screen = multiprocessing.Process(target=AssistanceSeeker_screen_logic.main_AS_screen, args=(otherIP,))
        client.close()
        client.close()
        allGraphics.Close()
        mouse.start()
        keyboard.start()
        screen.start()
        check_closed(close_queue, mouse, screen)


if __name__ == '__main__':
    ip = "192.168.4.91"
    port = 2000
    recv_q = queue.Queue()
    client = Client_comm(ip, port, recv_q)
    commands = {"00": handle_login_ans, "01": handle_signup_ans, "02": handle_typeUser_ans,
                "03": handle_getCode_ans, "04": handle_code_ans, "05": handle_conData}
    app = wx.App()
    allGraphics = graphics.MyFrame(client)

    threading.Thread(target=handleMsgs, args=(client, recv_q,)).start()
    threading.Thread(target=send_mac, args=(client,)).start()
    app.MainLoop()
