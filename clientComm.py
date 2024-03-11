import socket
import threading
import sys
import secrets
import base64
from AsymmetricEncryption import RSA_cipher
from SymmetricEncryption import AES_hash_cipher


class Client_comm:
    def __init__(self, serverIP: str, port: int, recv_q):
        """
        builder function creates new "Client_comm" object and runs main loop of client
        :param serverIP: ip of server to connect to
        :param port: port in which to connect to server through
        :param recv_q: queue of data gotten to server to put
        """
        self.serverIP = serverIP
        self.port = port
        self.recv_q = recv_q
        self.socket = socket.socket()
        self.is_running = True
        self.sharedKey = None
        threading.Thread(target=self._main_loop).start()

    def _main_loop(self):
        """
        main client loop
        """
        # connect to server
        try:
            self.socket.connect((self.serverIP, self.port))
        except Exception as e:
            sys.exit("server is down, try again later")

        # create new shared key with server to encrypt and decrypt data
        self._get_shared_key()

        while self.is_running:
            # get datalen from server
            try:
                datalen = self.socket.recv(3).decode()
            except Exception as e:
                sys.exit("server is down, try again later")

            if not datalen.isnumeric():
                sys.exit("server is down, try again later")

            # get data by data len and decrypt data
            try:
                data = self.socket.recv(int(datalen)).decode()
            except Exception as e:
                sys.exit("server is down, try again later")

            data = self.sharedKey.decrypt(data)

            # put data in recv q for main client
            self.recv_q.put(data)

    def _get_shared_key(self):
        """
        function creates new shared key and sends it by servers public key to server
        """

        # get servers string public key for RSA
        try:
            pubKey = self.socket.recv(451).decode()
        except Exception as e:
            sys.exit("server is down, try again later")
        # check string public key length
        if len(pubKey) != 451:
            sys.exit("server error in key gotten")

        # create new 64 character random shared key to send to server and for AES encryption
        shared_key_string = base64.b64encode(secrets.token_bytes(48)).decode()
        # send RSA encrypted shared key to server
        try:
            self.socket.send(RSA_cipher.encrypt(shared_key_string, pubKey))
        except Exception as e:
            sys.exit("server is down, try again later")

        # save AES encryption object of shared key
        self.sharedKey = AES_hash_cipher(shared_key_string)

    def send(self, msg: str):
        """
        function sends encrypted msg to server
        :param msg: msg to send to server
        """
        # send data only if there is a shared key
        while self.sharedKey is None:
            continue

        # encrypt msg and send it with msg length
        msg = self.sharedKey.encrypt(msg.encode())

        try:
            self.socket.send((str(len(msg)).zfill(3)).encode() + msg)
        except Exception as e:
            print('client comm - send', str(e))
            sys.exit("server is down, try again later")

    def sendImage(self, data: str, imageData: bytes):
        """
        Function gets Image data and data header and sends to server
        :param data: data header to send to server with data about Image
        :param imageData: data of image
        """
        # send data only if there is a shared key
        if self.sharedKey is not None:
            # encrypt msg and send it with msg length
            data = self.sharedKey.encrypt(data.encode())
            # send length of data, encrypted data and Image data
            try:
                self.socket.send((str(len(data)).zfill(3)).encode())
                self.socket.send(data)
                self.socket.send(imageData)
            except Exception as e:
                print('client comm - sendImage', str(e))
                sys.exit("server is down, try again later")

    def close(self):
        """
        end main loop and close socket
        """
        self.is_running = False
        self.socket.close()
        self.recv_q.put("close")
