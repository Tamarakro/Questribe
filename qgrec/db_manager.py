import sqlite3
from uuid import uuid4
from .constants import RESOURCES_DIR


DB_URL = f"{RESOURCES_DIR}/db.sqlite"


class DB:
    @staticmethod
    def init():
        conn = None

        try:
            conn = sqlite3.connect(DB_URL)

            create_query = """CREATE TABLE IF NOT EXISTS Users(
                id TEXT NOT NULL,
                fname TEXT NOT NULL,
                lname TEXT NOT NULL,
                uname TEXT NOT NULL,
                password TEXT NOT NULL,
                lang TEXT NOT NULL
            )"""

            cursor = conn.cursor()
            cursor.execute(create_query)
            conn.commit()
            conn.close()

        except Exception as e:
            if conn:
                conn.close()

            raise Exception(str(e))

    @staticmethod
    def saveuser(fname, lname, uname, password, lang):
        conn = None

        try:
            conn = sqlite3.connect(DB_URL)
            create_query = """INSERT INTO Users VALUES(?,?,?,?,?, ?)"""
            vals = (str(uuid4()), fname, lname, uname, password, lang)
            cursor = conn.cursor()
            cursor.execute(create_query, vals)
            conn.commit()
            conn.close()
        except Exception as e:
            if conn:
                conn.close()
            raise Exception(str(e))

    @staticmethod
    def getuser(uname):
        conn = None

        try:
            conn = sqlite3.connect(DB_URL)
            select_query = """SELECT * FROM Users WHERE uname = ?"""
            cursor = conn.cursor()
            res = cursor.execute(select_query, (uname,))

            users = []
            for val in res:
                users.append(val)
            conn.close()

            if users:
                return users[0]
            return users

        except Exception as e:
            if conn:
                conn.close()
            raise Exception(str(e))
