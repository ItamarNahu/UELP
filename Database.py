import sqlite3

from SymmetricEncryption import AES_hash_cipher


# class to work with Database and tables of Uelp_db.sql
class Database_comm:
    def __init__(self):
        """
        builder function creates a new Database_comm object with table and database names
        """

        self.DBname = "Uelp_db.sql"
        self.conn = None
        self.curr = None
        self.loginTableName = "USERS"
        self.blacklistTableName = "MACS"
        self._create_db()

    def _create_db(self):
        """
        function creates new tables USERS and MACS if thy don't already exist
        """

        # connect to DB
        self.conn = sqlite3.connect(self.DBname)
        self.curr = self.conn.cursor()
        # create tables
        self.curr.execute(
            "CREATE TABLE IF NOT EXISTS " + self.loginTableName + "(username VARCHAR(25), password VARCHAR(32),"
                                                                  " PRIMARY KEY(username))")
        self.curr.execute(
            "CREATE TABLE IF NOT EXISTS " + self.blacklistTableName + "(mac VARCHAR(32), PRIMARY KEY(mac))")

        self.conn.commit()

    def _checkUser(self, username: str) -> bool:
        """
        function checks if username exists in USERS table
        :param username: username gotten from user
        :return: True if username exists in USERS and False otherwise
        """

        self.curr.execute("SELECT username FROM " + self.loginTableName + " WHERE username = ?", (username,))
        return self.curr.fetchone() is not None

    def addUser(self, username: str, password: str) -> bool:
        """
        function adds username and hashed password to USERS table if the username does not already exist
        :param username: username to add to USERS
        :param password: password to add to USERS
        :return: True if successfully added and False otherwise
        """

        # check if username already exists in table if it does not add it and his hashed password into USERS
        if len(username) < 26 and not self._checkUser(username):
            self.curr.execute("INSERT INTO " + self.loginTableName + " (username, password) VALUES (?, ?)",
                              (username, AES_hash_cipher.hash(password)))
            self.conn.commit()
            ans = True
        else:
            ans = False
        return ans

    def checkPassword(self, username: str, password: str) -> bool:
        """
        function checks if usernames password gotten exists in table
        :param username: username to check in USERS
        :param password: password to check in USERS
        :return: True if password of username gotten exists for username in USERS
         and False if username or password don't exist in USERS
        """
        if len(username) < 26 and self._checkUser(username):
            self.curr.execute("SELECT password FROM " + self.loginTableName + " WHERE username = ? and password = ?",
                              (username, AES_hash_cipher.hash(password)))
            ans = self.curr.fetchone() is not None
        else:
            ans = False
        return ans

    def macExists(self, mac: str) -> bool:
        """
        function checks if mac gotten exists in MACS table
        :param mac: mac to check if it's hash exists in MACS
        :return: True if exists False otherwise
        """

        self.curr.execute("SELECT mac FROM " + self.blacklistTableName + " WHERE mac = ?", (AES_hash_cipher.hash(mac),))
        return self.curr.fetchone() is not None

    def addBlackMac(self, mac: str) -> bool:
        """
        function checks if mac gotten exists in MACS and if dosen't adds it's hash
        :param mac: mac to add to MACS table
        :return: True if mac was added successfully added and False otherwise
        """

        if not self.macExists(mac):
            self.curr.execute("INSERT INTO " + self.blacklistTableName + " (mac) VALUES (?)",
                              (AES_hash_cipher.hash(mac),))
            self.conn.commit()
            ans = True
        else:
            ans = False
        return ans


if __name__ == '__main__':
    db = Database_comm()
    print(db.addBlackMac("64:00:6A:42:93:94"))
