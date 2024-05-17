import queue
import threading

from scapy.layers.l2 import getmacbyip

import Server_protocol as Protocol
from Database import Database_comm
from Servercomm import Server_comm
from Sessioncodes import Session_codes


def handleMsgs(server, recv_q):
    """
    Function creates database comm object and recieves new msgs from server queue unpacks the msg based on protocol
     and calls function by opcode
    :param server: server object to communicate with server
    :param recv_q: servers msgs queue
    """
    # create database object to communicate with database
    db = Database_comm()

    while True:
        data, ip = recv_q.get()
        print(data)
        # if data is disconnect call disconnect client function
        if data == "disconnect":
            disconnectClient(ip, server)
        else:
            opcode, params = Protocol.unpackData(data)
            # call function based on opcode gotten in data and command dic
            commands[opcode](ip, db, server, params)


def handleExpired(server, expired_q):
    """
    Function checks expired codes queue and gets expired code sessions ips and sends expired code protocol to the
     ip goten
    :param server: server object to communicate with server
    :param expired_q: queue that has ips of users with expired session codes
    """
    while True:
        ip = expired_q.get()
        server.send(ip, Protocol.pack_expired_code())


def handle_mac_addr(clientIP, db, server, params):
    """
    Function adds mac address of new user to users dictionary with ip
    :param clientIP: ip of users mac addr
    :param db: database object to communicate with database
    :param server: server object to communicate with server
    :param params: list of paramaters gotten with opcode from user
    """
    mac_addr = params[0]

    users[clientIP] = [mac_addr, None, None]


def handle_login(clientIP, db, server, params):
    """
    Function gets username and password of user checks his password by database and sends msg accordingly back to user
    based on if username and password fit credentials
    :param clientIP: ip of user from whom gotten login msg
    :param db: database object to communicate with database
    :param server: server object to communicate with server
    :param params: list of paramaters gotten with opcode from user
    """
    username = params[0]
    password = params[1]

    if clientIP in users.keys():
        # check if password of username gotten exists in db
        userOK = db.checkPassword(username, password)
        if userOK:
            # check if user is already logged in and set opcode accordingly
            if check_logged_in(username):
                userOK = "2"
            else:
                # add username to users dic and set opcode if user can log in successfully
                users[clientIP][2] = username
                userOK = "0"
        else:
            userOK = "1"
    else:
        userOK = "1"

    # send msg back to user based on if user can login or not
    server.send(clientIP, Protocol.pack_login_ans(userOK))


def handle_signup(clientIP, db, server, params):
    """
    Function gets username and password of user checks his password by database and sends msg accordingly back to user
    based on if username and password fit credentials
    :param clientIP: ip of user from whom gotten signup msg
    :param db: database object to communicate with database
    :param server: server object to communicate with server
    :param params: list of paramaters gotten with opcode from user
    """
    username = params[0]
    password = params[1]

    if clientIP in users.keys():
        # check if can add the user with the username and password to db successfully
        newuserOK = db.addUser(username, password)
        if newuserOK:
            # add username to users dic if created and added to db table
            users[clientIP][2] = username
    else:
        newuserOK = False

    # send msg back to user based on if user can signup or not
    server.send(clientIP, Protocol.pack_signup_ans(newuserOK))


def check_logged_in(username):
    """
    Function checks if user is logged in by checking users dic and seeing if users username exists in this dic
    :param username: username of user to check if logged in
    :return: True if user is logged in and false if not
    """
    for userData in users.values():
        if username == userData[2]:
            ans = True
            break
    else:
        ans = False
    return ans


def handle_typeUser(clientIP, db, server, params):
    """
    Function gets user type asked from user and checks if users mac and mac from arp request is the same and ok
    accordingly the function checks if the user type asked fits the database blacklist credentials
    and returns msg to user accordingly
    :param clientIP: ip of user whom gotten typeuser msg from
    :param db: database object to communicate with database
    :param server: server object to communicate with server
    :param params: list of paramaters gotten with opcode from user
    """
    typeUser = params[0]
    # mac gotten from sending arp request to users ip
    mac_from_arp = getmacbyip(clientIP)

    # check if mac from arp equals mac gotten from user or your own computer
    if mac_from_arp == "ff:ff:ff:ff:ff:ff" or mac_from_arp == users[clientIP][0]:
        # if user wants to be a helper check if users mac is in blacklist based on db table
        # save user type and set msg to user accordingly
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

    # send msg back to user by protocol of if user type is verified or not
    server.send(clientIP, msg)


def handle_getCode(clientIP, db, server, params):
    """
    Function checks if user is Helper and sends msg back to user with protocol and a new session code
    :param clientIP: ip of user whom gotten getcode msg from
    :param db: database object to communicate with database
    :param server: server object to communicate with server
    :param params: list of paramaters gotten with opcode from user
    """
    if users[clientIP][1] == "H":
        msg = Protocol.pack_getcode_ans(codes.createCode(clientIP))
        server.send(clientIP, msg)


def handle_codeCheck(clientIP, db, server, params):
    """
    Function gets code user entered from params and checks if code exists and returns msg to user accordingly
    :param clientIP: ip of user whom gotten check code msg from
    :param db: database object to communicate with database
    :param server: server object to communicate with server
    :param params: list of paramaters gotten with opcode from user
    """
    userCode = params[0]

    # check if user code gotten from is Assistance Seeker
    if users[clientIP][1] == "A":
        # check if code gotten exists as a valid session code and send msg back to user accordingly
        codeAnswer = codes.checkCode(userCode)
        server.send(clientIP, Protocol.pack_code_ans(codeAnswer))
        # check if code is valid or not and send connection data of users who connected to session back to each other
        # to start session
        if codeAnswer:
            otherIP = codes.ip_from_code(userCode)
            server.send(clientIP, Protocol.pack_con_data(otherIP, "A"))
            server.send(otherIP, Protocol.pack_con_data(clientIP, "H"))


def disconnectClient(clientIP, server):
    """
    Function removes client from users dic and closes the users socket from server
    :param clientIP: ip of user to disconnect from server
    :param server: server object to communicate with server
    """
    if clientIP in users.keys():
        del users[clientIP]
    server.closeClient(clientIP)


if __name__ == '__main__':
    expired_q = queue.Queue()
    codes = Session_codes(expired_q)
    recv_q = queue.Queue()
    port = 2000
    server = Server_comm(recv_q, port)

    # dictionary of opcode and function name called for each opcode
    commands = {"00": handle_login, "01": handle_signup, "02": handle_typeUser, "03": handle_getCode,
                "04": handle_codeCheck, "06": handle_mac_addr}
    # dictionary of users in system, Exp: users{ip : (mac_addr, userType, username)}
    users = {}

    # start Threads for msgs from server queue and msgs from expired codes queue
    threading.Thread(target=handleMsgs, args=(server, recv_q,)).start()
    threading.Thread(target=handleExpired, args=(server, expired_q,)).start()
