import time
import os.path
import sqlite3

#from BSC.Database.sql_v01_001 import db_up
from BSC.Database.sql_v02_001 import db_up, db_down

class DB():
    def __init__(self, db_name, verbose=False, clear_db=False):
        self.verbose = verbose #TODO verbose variable check needs to be implemented to class funciton print statements
        self.clear_db = clear_db
        self.db_name = db_name
        self.__validateAndInitalize()

    def __validateAndInitalize(self):
        new_db = False
        if self.verbose: print("INFO --- database file name: ", self.db_name)
        if os.path.isfile("./"+self.db_name) == False:
            print("INFO --- DB file does not exists, creating new one")
            new_db = True

        self.__createDB()
        if new_db:
            self.__createTables()
        elif self.clear_db:
            if self.verbose: print("INFO --- 'clear_db' flag is set so first dropping all tables and creating them again")
            self.__DEV_ClearDB()
            self.__createTables()

        is_ok = self.__validateDatabase()

    def __createDB(self):
        con = sqlite3.connect(self.db_name)
        con.close()

    def __createTables(self):
        categories_data = [("MS", "men singles"),
                           ("WS", "women singles"),
                           ("MD", "men double"),
                           ("WD", "women double"),
                           ("XD", "mixed double")
                           ]
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        for table, sql in db_up.items():
            print("DEBUG --- Creating table:", table)
            cur.execute(sql)
        cur.executemany("INSERT INTO categories (name, description) VALUES(?,?)", categories_data)
        con.commit()
        con.close()

    def __validateDatabase(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        res = cur.execute("SELECT * FROM sqlite_master")
        for item in res.fetchall():
            if item[0] == "table":
                if item[1] not in db_up.keys() and item[1] != "sqlite_sequence": print("DEBUG --- found table that is not not part of ERD") #TODO maybe handle this somehow if extra table is found

                #TODO not sure if content check is actually needed
                has_content = self.__checkTableContent(cur, item[1])
                if has_content:
                    print("DEBUG --- found table: '"+item[1]+"' that has content")
                else:
                    print("DEBUG --- found table: '"+item[1]+"' that is empty")
        con.close()

    def __checkTableContent(self, cur, table_name):
        res = cur.execute("SELECT * FROM " + table_name + " LIMIT 10")
        if res.fetchone() is None:
            return False
        return True

    def __DEV_ClearDB(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        for table, sql in db_down.items():
            print("DEBUG --- Dropping table:", table)
            cur.execute(sql)
        con.commit()
        con.close()

    def GetPlayer(self, name):
        result = None
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        #print("get or create user/player name: " + name)
        res = cur.execute("SELECT * FROM users WHERE name = '" + name +"'")
        result = res.fetchone() #note to self, fetchone removes the content form the result variable res, likely same with fetchall
        if result is None:
            print("no player in db, creating new one")
            data = (name, 1000)
            res = cur.execute("INSERT INTO users (name, elo) VALUES (?,?)", data)
            con.commit()
            res = cur.execute("SELECT * FROM users WHERE name = '" + name +"'")
            result = res.fetchone()
        con.close()
        #time.sleep(5)
        return result
