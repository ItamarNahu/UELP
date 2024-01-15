from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


# class to work with Asymmetric RSA encryption
class RSA_cipher:

    def __init__(self):
        """
        builder function to create a new object of RSA_cipher with RSA private and public keys
        """
        self.privateKey = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        self.publicKey = self.privateKey.public_key()

    @staticmethod
    def encrypt(data: str, public_key_str: str) -> bytes:
        """
        method to encrypt data with a RSA public key
        :param data: data to encrypt
        :param public_key_str: String representation of an RSA public key
        :return: encrypted data in bytes
        """
        try:
            # Convert string representation to RSA public key
            public_key = serialization.load_pem_public_key(public_key_str.encode(), backend=default_backend())

            # Encrypt the message with the public key
            enc = public_key.encrypt(data.encode(), padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                                 algorithm=hashes.SHA256(), label=None))
        except Exception as e:
            print(e)
            print("The given String key does not match the RSA public key format")
        else:
            return enc

    def decrypt(self, enc_data: bytes) -> str:
        """
        method to decrypt, encrypted data gotten using the private key of the class
        :param enc_data: data encrypted using the public key
        :return: decrypted data as string
        """
        try:
            # Decrypt the message with the private key
            decrypted_data = self.privateKey.decrypt(enc_data,
                                                     padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                                  algorithm=hashes.SHA256(), label=None))
        except Exception as e:
            print(e)
            print("The given encrypted data does not match RSA key size")
        else:
            return decrypted_data.decode()

    def get_string_key(self):
        """
        method gets a string representation of the public key
        :return: String representation of the public key
        """
        # Get the string representation of the public key
        stringkey = self.publicKey.public_bytes(encoding=serialization.Encoding.PEM,
                                                format=serialization.PublicFormat.SubjectPublicKeyInfo).decode()

        return stringkey
