from Servercomm import Server_comm
from Sessioncodes import Session_codes
from Database import Database_comm
import Server_protocol as Protocol
import queue
import threading
from scapy.layers.l2 import getmacbyip


def handleMsgs(server, recv_q):
    db = Database_comm()
    while True:
        data, ip = recv_q.get()
        print(data)
        if data == "disconnect":
            disconnectClient(ip, server)
        else:
            opcode, params = Protocol.unpackData(data)
            commands[opcode](ip, db, server, params)


def handleExpired(server, expired_q):
    while True:
        ip = expired_q.get()
        server.send(ip, Protocol.pack_expired_code())


def handle_mac_addr(clientIP, db, server, params):
    mac_addr = params[0]

    users[clientIP] = [mac_addr, None, None]


def handle_login(clientIP, db, server, params):
    username = params[0]
    password = params[1]
    if clientIP in users.keys():
        userOK = db.checkPassword(username, password)
        if userOK:
            if check_logged_in(username):
                userOK = "2"
            else:
                users[clientIP][2] = username
                userOK = "0"
        else:
            userOK = "1"
    else:
        userOK = "1"
    server.send(clientIP, Protocol.pack_login_ans(userOK))


def handle_signup(clientIP, db, server, params):
    username = params[0]
    password = params[1]
    if clientIP in users.keys():
        newuserOK = db.addUser(username, password)
        if newuserOK:
            users[clientIP][2] = username
    else:
        newuserOK = False
    server.send(clientIP, Protocol.pack_signup_ans(newuserOK))


def check_logged_in(username):
    for userData in users.values():
        if username == userData[2]:
            ans = True
            break
    else:
        ans = False
    return ans


def handle_typeUser(clientIP, db, server, params):
    typeUser = params[0]
    mac_from_arp = getmacbyip(clientIP)
    if mac_from_arp == "ff:ff:ff:ff:ff:ff" or mac_from_arp == users[clientIP][0]:
        if typeUser == "0":
            if not db.macExists(users[clientIP][0].upper()):
                users[clientIP][1] = "H"
                typeUser_ans = True
            else:
                typeUser_ans = False
        elif typeUser == "1":
            users[clientIP][1] = "A"
            typeUser_ans = True
        msg = Protocol.pack_typeuser_ans(typeUser_ans)
    else:
        msg = Protocol.pack_typeuser_ans(False)
    server.send(clientIP, msg)


def handle_getCode(clientIP, db, server, params):
    if users[clientIP][1] == "H":
        msg = Protocol.pack_getcode_ans(codes.createCode(clientIP))
        server.send(clientIP, msg)


def handle_codeCheck(clientIP, db, server, params):
    userCode = params[0]
    if users[clientIP][1] == "A":
        codeAnswer = codes.checkCode(userCode)
        server.send(clientIP, Protocol.pack_code_ans(codeAnswer))
        if codeAnswer:
            otherIP = codes.code_from_ip(userCode)
            server.send(clientIP, Protocol.pack_con_data(otherIP, "A"))
            server.send(otherIP, Protocol.pack_con_data(clientIP, "H"))


def disconnectClient(clientIP, server):
    if clientIP in users.keys():
        del users[clientIP]
    server.closeClient(clientIP)


if __name__ == '__main__':
    recv_q = queue.Queue()
    expired_q = queue.Queue()
    port = 2000
    codes = Session_codes(expired_q)
    server = Server_comm(recv_q, port)

    commands = {"00": handle_login, "01": handle_signup, "02": handle_typeUser, "03": handle_getCode,
                "04": handle_codeCheck, "06": handle_mac_addr}
    users = {}

    threading.Thread(target=handleMsgs, args=(server, recv_q,)).start()
    threading.Thread(target=handleExpired, args=(server, expired_q,)).start()
