import sqlite3


class Database_comm:
    def __init__(self):
        """

        """
        self.DBname = "Uelp_db.sql"
        self.conn = None
        self.curr = None
        self.loginTableName = "USERS"
        self.blacklistTableName = "MACS"
        self._create_db()

    def _create_db(self):
        """

        :return:
        """
        self.conn = sqlite3.connect(self.DBname)
        self.curr = self.conn.cursor()
        self.curr.execute(
            "CREATE TABLE IF NOT EXISTS " + self.loginTableName + "(username VARCHAR(25), password VARCHAR(32), PRIMARY "
                                                                  "KEY(username))")
        self.curr.execute(
            "CREATE TABLE IF NOT EXISTS " + self.blacklistTableName + "(mac VARCHAR(32), PRIMARY KEY(mac))")

        self.conn.commit()

    def _checkUser(self, username):
        """

        :param username:
        :return:
        """
        self.curr.execute("SELECT username FROM " + self.loginTableName + " WHERE username = ?", (username,))
        return self.curr.fetchone() is not None

    def addUser(self, username, password):
        """

        :param username:
        :param password:
        :return:
        """

        if self._checkUser(username):
            self
