import Client_protocol as Protocol
import queue
import threading
from clientComm import Client_comm
from uuid import getnode
import wx
import graphics
from pubsub import pub
import multiprocessing
import Helper_logic
import Helper_screen_logic
import AssistanceSeeker_keyboard_logic
import AssistanceSeeker_mouse_logic
import AssistanceSeeker_screen_logic
import time


def handleMsgs(client, recv_q):
    """
    Function recieves new msgs from queue from server, unpacks the msg based on protocol
     and calls function by opcode
    :param client: client object for comm with server
    :param recv_q: queue of msgs gotten from server
    """
    while True:
        data = recv_q.get()
        # if data gotten is close stop getting new msgs
        if data == "close":
            break
        else:
            # unpack data by protocol and call function by opcode from data
            opcode, params = Protocol.unpackData(data)
            print(params)
            commands[opcode](params)


def send_mac(client):
    """
    Function gets the computers mac and sends it to server by protocol
    :param client: client object for comm with server
    """
    mac_address = ':'.join(['{:02x}'.format((getnode() >> i) & 0xff) for i in range(0, 8 * 6, 8)][::-1])
    client.send(Protocol.pack_mac_addr(mac_address))


def handle_login_ans(params):
    """
    Function gets the answer of login msg from server and sends the login ans to graphics
    :param params: list of all parameters unpacked and gotten from data from server
    """
    login_ans = params[0]
    wx.CallAfter(pub.sendMessage, "login_ans", ans=login_ans)


def handle_signup_ans(params):
    """
    Function gets the answer of signup msg from server and sends the signup ans to graphics
    :param params: list of all parameters unpacked and gotten from data from server
    """
    signup_ans = params[0]
    wx.CallAfter(pub.sendMessage, "signup_ans", ans=signup_ans)


def handle_typeUser_ans(params):
    """
    Function gets the answer of typeUser msg from server and sends the typeUser ans to graphics
    :param params: list of all parameters unpacked and gotten from data from server
    """
    typeUser_ans = params[0]
    wx.CallAfter(pub.sendMessage, "typeUser_ans", ans=typeUser_ans)


def handle_getCode_ans(params):
    """
    Function gets the answer of getCode msg from server and sends the getCode ans to graphics
    :param params: list of all parameters unpacked and gotten from data from server
    """
    getCode_ans = params[0]
    wx.CallAfter(pub.sendMessage, "gotten_code", ans=getCode_ans)


def handle_code_ans(params):
    """
    Function gets the answer of code msg from server and sends the code ans to graphics
    :param params: list of all parameters unpacked and gotten from data from server
    """
    code_ans = params[0]
    wx.CallAfter(pub.sendMessage, "code_ans", ans=code_ans)


def handle_conData(params):
    """
    Function gets connection data of other user to connect too and starts process for mouse keyboard and screen
     accordingly to user type
    :param params: list of all parameters unpacked and gotten from data from server
    """
    otherIP = params[0]
    my_user_Type = params[1]

    if my_user_Type:
        # queue for comm between keyboard and client to send msgs when keyboard detects to disconnect from session
        close_queue = multiprocessing.Queue()
        # create proccesss for keyboard screen and mouse as both a Helper and Assistance Seeker accordingly
        # if a user is a Helper send to graphic connecting_session to switch to connecting session screen
        if my_user_Type == "H":
            mouse = multiprocessing.Process(target=Helper_logic.main_Helper, args=(otherIP, 2001, None,))
            keyboard = multiprocessing.Process(target=Helper_logic.main_Helper, args=(otherIP, 2002, close_queue,))
            screen = multiprocessing.Process(target=Helper_screen_logic.main_Helper_screen, args=(otherIP,))
            wx.CallAfter(pub.sendMessage, "connecting_session")
        elif my_user_Type == "A":
            mouse = multiprocessing.Process(target=AssistanceSeeker_mouse_logic.main_AS_mouse, args=(otherIP,))
            keyboard = multiprocessing.Process(target=AssistanceSeeker_keyboard_logic.main_AS_keyboard,
                                               args=(otherIP, close_queue,))
            screen = multiprocessing.Process(target=AssistanceSeeker_screen_logic.main_AS_screen, args=(otherIP,))

        # close client to main server (not needed anymore as connection switches to P2P)
        client.close()

        # wait five seconds before starting mouse screen and keyboard process for connecting to session screen
        # to finish in graphics
        time.sleep(5)
        mouse.start()
        keyboard.start()
        screen.start()

        # call function for when user asks session to close
        check_closed(close_queue, mouse, screen, keyboard)


def check_closed(close_queue, mouse, screen, keyboard):
    """
    Function gets data from close_queue when data gotten is close
    (keyboard process tells the client to terminate all processes to end session)
    terminate all running processes and leave loop
    :param close_queue: multiprocessing queue for comm between client and keyboard processes
    :param mouse: running process of mouse control
    :param screen: running process of screen control
    :param keyboard: running process of keyboard control
    """
    while True:
        data = close_queue.get()
        if data == "close":
            mouse.terminate()
            screen.terminate()
            keyboard.terminate()
            break


if __name__ == '__main__':
    ip = "192.168.4.77"
    port = 2000
    recv_q = queue.Queue()
    client = Client_comm(ip, port, recv_q)

    # dictionary of opcode and function name called for each opcode
    commands = {"00": handle_login_ans, "01": handle_signup_ans, "02": handle_typeUser_ans,
                "03": handle_getCode_ans, "04": handle_code_ans, "05": handle_conData}

    # create graphic object
    app = wx.App()
    allGraphics = graphics.MyFrame(client)

    # start Threads for msgs from server queue and sending computer mac to server
    threading.Thread(target=handleMsgs, args=(client, recv_q,)).start()
    threading.Thread(target=send_mac, args=(client,)).start()

    # run main graphic
    app.MainLoop()
