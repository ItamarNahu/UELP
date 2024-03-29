import socket
import select
import threading
from AsymmetricEncryption import RSA_cipher
from SymmetricEncryption import AES_hash_cipher
import Helper_protocol


class Server_comm:

    def __init__(self, recv_q, port: int, bindIP: str = None):
        """
        builder method creates a new "Server_comm" object with a Queue, port and bindIP
        :param recv_q: Queue for messages to the logic
        :param port: port that server will run on
        :param bindIP: IP that server will check if it uses port 2001, 2002, 2003
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
        """

        self.socket.bind(("0.0.0.0", self.port))
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
                    if self.port != 2000 and self.bindIP != addr[0]:
                        self._disconnect_client(client)

                    # create a new shared key with client using RSA and AES encryption
                    threading.Thread(target=self._get_shared_key, args=(addr[0], client)).start()
                else:
                    # get data len of client data and client data and decrypt
                    try:
                        datalen = int(current_socket.recv(3).decode())
                        data = current_socket.recv(int(datalen))
                    except Exception as e:
                        print(str(e))
                        print("main server in server conn")
                        self._disconnect_client(current_socket)
                        continue

                    data = self.open_clients[current_socket][1].decrypt(data)
                    # if data is from screen port call recvImage otherwise put in recv_q for logic
                    if self.port == 2003:
                        self._recvImage(current_socket, data)
                    else:
                        self.recv_q.put((data, self.open_clients[current_socket][0]))

    def _get_shared_key(self, clientIP: str, curSocket):
        """
        function sends servers public key to new client and gets and saves the shared key of server and client
        :param clientIP: ip of client to create shared key with
        :param curSocket: socket of client to create shared key with
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
        if client in self.open_clients.keys() and self.recv_q:
            print(f"{self.open_clients[client]} - disconnect")
            self.recv_q.put(("disconnect", self.open_clients[client][0]))
            if (self.port == 2001 or self.port == 2002 or self.port == 2003) and self.open_clients[client][0] == self.bindIP:
                self.close_server()
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
        """
        client = self._find_socket_by_ip(clientIP)

        if client is not None:
            self._disconnect_client(self._find_socket_by_ip(clientIP))

    def _recvImage(self, client, data: str):
        """
        Function is called when port is screen port and data was gotten from client of bindIP
        :param client: client gotten data from
        :param data: data gotten from client for screen
        """

        if client and client in self.open_clients.keys():
            client_ip = self.open_clients[client][0]
            # unpack data based on protocol
            opcode, params = Helper_protocol.unpackData(data)
            file_is_ok = True
            image_data_size = ""
            # if opcode is 01 we got a part image, if it is 02 we got a full Image
            # take out data accordingly
            if opcode == "01":
                if len(params) == 5:
                    top = params[0]
                    left = params[1]
                    bottom = params[2]
                    right = params[3]
                    image_data_size = params[4]
                else:
                    self._disconnect_client(client)
                    file_is_ok = False
            elif opcode == "02":
                if len(params) == 1:
                    image_data_size = params[0]
                else:
                    self._disconnect_client(client)
                    file_is_ok = False
            else:
                self._disconnect_client(client)
                file_is_ok = False

            # check image data size gotten
            if not image_data_size.isnumeric():
                self._disconnect_client(client)
                file_is_ok = False

            if file_is_ok:
                image_data_size = int(image_data_size)

                # receive file data
                file = bytearray()
                while len(file) < image_data_size and file_is_ok:
                    size = image_data_size - len(file)
                    if size > 1024:
                        try:
                            file.extend(client.recv(1024))
                        except Exception as e:
                            self._disconnect_client(client)
                            file_is_ok = False
                    else:
                        try:
                            file.extend(client.recv(size))
                        except Exception as e:
                            self._disconnect_client(client)
                            file_is_ok = False

                # put image header data and image data in queue
                if file_is_ok:
                    all_image_data = []
                    if len(params) == 5:
                        all_image_data.append(top)
                        all_image_data.append(left)
                        all_image_data.append(bottom)
                        all_image_data.append(right)
                    all_image_data.append(file)
                    self.recv_q.put((all_image_data, client_ip))
