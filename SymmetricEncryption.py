import base64
from Cryptodome.Cipher import AES
from Cryptodome import Random
import hashlib
from Cryptodome.Util.Padding import pad, unpad


# class to work with AES encryption and hash
class AES_hash_cipher:
    def __init__(self, key: str):
        """
        builder function to create a new object of AES_hash_cipher with a key
        :param key: key to use for both sides
        """
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw: bytes) -> bytes:
        """
        method encrypts raw data gotten with AES encryption of key
        :param raw: data to encrypt
        :return: encoded encrypted data
        """

        raw = pad(raw, AES.block_size)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc: bytes) -> str:
        """
        method decrypts encrypted data gotten with AES decryption of key
        :param enc: encoded encrypted data
        :return: encoded decrypted data
        """

        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        return unpad(cipher.decrypt(enc[AES.block_size:]), AES.block_size).decode('utf-8')

    @staticmethod
    def hash(data: str) -> bytes:
        """
        method gets data and uses SHA-256 to return it's hash
        :param data: data to use hash function on
        :return: encoded hashed data
        """

        return hashlib.sha256(data.encode()).digest()
