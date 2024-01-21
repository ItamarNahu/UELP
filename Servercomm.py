import socket
import select
import threading
from AsymmetricEncryption import RSA_cipher
from SymmetricEncryption import AES_hash_cipher
import queue

class Server_comm:

    def __init__(self, recv_q, port: int, bindIP: str):
        """
        builder method creates a new "Server_comm" object with a Queue, port and bindIP
        :param recv_q: Queue for messages to the logic
        :param port: port that server will run on
        :param bindIP: IP that server will listen too
        """
        self.recv_q = recv_q
        self.port = port
        self.socket = socket.socket()
        self.bindIP = bindIP
        self.open_clients = {}
        self.is_running = False
        self.RSAobject = RSA_cipher()
        threading.Thread(target=self._main_loop).start()

    def _main_loop(self):
        """
        function runs server main loop, connects clients creates shared keys with them and gets msgs from them
         and encrypts them for logic
        :return: nothing
        """

        self.socket.bind((self.bindIP, self.port))
        self.socket.listen(3)
        self.is_running = True

        while self.is_running:
            rlist, wlist, xlist = select.select([self.socket] + list(self.open_clients.keys()),
                                                list(self.open_clients.keys()), [], 0.03)

            for current_socket in rlist:
                # new client
                if current_socket is self.socket:
                    client, addr = self.socket.accept()
                    print(f"{addr[0]} - connected")
                    # check if server is keyboard, mouse or screen server, if yes check if ip connected is bindIP
                    if self.port != 2000 and self.bindIP != addr:
                        self._disconnect_client(client)
                    # create a new shared key with client using RSA and AES encryption
                    threading.Thread(target=self._get_shared_key, args=(addr[0], client)).start()
                else:
                    # get data len of client data
                    try:
                        datalen = current_socket.recv(3).decode()
                    except Exception as e:
                        print(e)
                        print("main server in server conn")
                        self._disconnect_client(current_socket)
                        continue

                    if not datalen.isnumeric():
                        self._disconnect_client(current_socket)
                        continue

                    # get client data and decrypt
                    try:
                        data = current_socket.recv(int(datalen))
                    except Exception as e:
                        print(str(e))
                        print("main server in server conn")
                        self._disconnect_client(current_socket)
                        continue

                    data = self.open_clients[current_socket][1].decrypt(data)

                    # if data is from screen port call recvImage otherwise put in recv_q for logic
                    if self.port == 2003:
                        self.recvImage(current_socket, data)
                    else:
                        self.recv_q.put((data, self.open_clients[current_socket][0]))

    def _get_shared_key(self, clientIP: str, curSocket):
        """
        function sends servers public key to new client and gets and saves the shared key of server and client
        :param clientIP: ip of client to create shared key with
        :param curSocket: socket of client to create shared key with
        :return: nothing
        """
        # send servers public key to client and get a shared encrypted key from client
        try:
            curSocket.send(self.RSAobject.get_string_key().encode())
            sharedKey = curSocket.recv(256)
        except Exception as e:
            print(e)
            print("in get shared key, server comm")
            self._disconnect_client(curSocket)
        else:
            # check length of key is key gotten and decrypt the shared key with private key and save it
            if len(sharedKey) != 256:
                self._disconnect_client(curSocket)
            else:
                sharedKey = self.RSAobject.decrypt(sharedKey)
                self.open_clients[curSocket] = (clientIP, AES_hash_cipher(sharedKey))

    def send(self, ip: str, msg: str):
        """
        send encrypted data to certain client
        :param ip: ip of client to send msg too
        :param msg: msg to send to client
        :return: nothing
        """
        if self.is_running:
            client = self._find_socket_by_ip(ip)
            if client is not None:
                # if client exists in open clients encrypt with AES and send with length by protocol
                if client in self.open_clients.keys():
                    msg = self.open_clients[client][1].encrypt(msg.encode())
                    try:
                        client.send(str(len(msg)).zfill(3).encode() + msg)
                    except Exception as e:
                        print(str(e))
                        self._disconnect_client(client)

    def _disconnect_client(self, client):
        """
        function disconnects client from server, by closing socket and removing from dics
        :param client: socket of client to disconnect
        :return:nothing
        """
        # if client in open_clients remove him and tell logic by sending disconnect
        if client in self.open_clients.keys():
            print(f"{self.open_clients[client]} - disconnect")
            self.recv_q.put(("disconnect", self.open_clients[client]))
            del self.open_clients[client]
        client.close()

    def _find_socket_by_ip(self, findip: str):
        """
        function find clients socket by ip
        :param findip: ip to find it's socket
        :return: socket of clients ip
        """
        client = None
        for soc, ip_enc in self.open_clients.items():
            if findip == ip_enc[0]:
                client = soc
                break
        return client

    def close_server(self):
        """
        end main loop
        :return: nothing
        """
        self.is_running = False

    def is_running(self):
        """
        check if server is running
        :return: True or False if server is running
        """
        return self.is_running

    def closeClient(self, clientIP: str):
        """
        function closes a client
        :param clientIP: ip of client to close
        :return: nothing
        """
        client = self._find_socket_by_ip(clientIP)
        if client is not None:
            self._disconnect_client(self._find_socket_by_ip(clientIP))

    def recvImage(self, client, data: str):
        """

        :param client:
        :param data:
        :return:
        """
        pass
