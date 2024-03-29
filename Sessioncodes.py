import threading
import time
import secrets
import base64


# class to work with session codes
class Session_codes:
    def __init__(self, expired_q):
        self.expired_q = expired_q
        self.codes = {}
        self.cleanseTime = 180
        threading.Thread(target=self._remove_expired).start()

    def _remove_expired(self):
        """
        Function checks dic of codes every two seconds, if there are codes who expired remove from dic and add to
        expired codes queue
        """
        while True:
            currTime = time.time()
            expired_ips = []

            for ip in self.codes.keys():
                createTime = self.codes[ip][1]
                if currTime - createTime > self.cleanseTime:
                    expired_ips.append(ip)
                    self.expired_q.put(ip)

            # remove expired_ips from dictionary
            for ip in expired_ips:
                del self.codes[ip]

            time.sleep(2)

    def createCode(self, ip: str) -> str:
        """
        Function creates a random string code that dosent exist in all codes and adds it to dic
        :param ip: ip of user whose code was created for (saved in dic with code)
        :return: code created
        """
        while True:
            newCode = base64.b64encode(secrets.token_bytes(6)).decode()
            if not self.checkCode(newCode):
                break

        self.codes[ip] = (newCode, time.time())
        return newCode

    def checkCode(self, code) -> bool:
        """
        Function checks if code gotten exists in dictionary of all codes
        :param code: code to check if in dic
        :return: True if code in codes dictionary, False otherwise
        """
        onlyCodes = [codeInfo[0] for codeInfo in self.codes.values()]
        return code in onlyCodes

    def code_from_ip(self, code) -> str:
        ip = None
        for ip_dic, code_time in self.codes.items():
            if code == code_time[0]:
                ip = ip_dic
                break
        return ip
