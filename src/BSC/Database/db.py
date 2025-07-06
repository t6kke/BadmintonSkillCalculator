import os.path
import sqlite3

#from BSC.Database.sql_v01_001 import db_up
from BSC.Database.sql_v02_001 import db_up

class DB():
    def __init__(self, db_name, verbose=False):
        self.verbose = verbose #TODO verbose variable check needs to be implemented to class funciton print statements
        self.db_name = db_name
        self.con = None
        self.cur = None
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

        is_ok = self.__validateDatabase()

    def __createDB(self):
        self.con = sqlite3.connect("db_test.db")
        self.cur = self.con.cursor()

    def __createTables(self):
        for table, sql in db_up.items():
            print("DEBUG --- Creating table:", table)
            self.cur.execute(sql)
        self.con.commit()

    def __validateDatabase(self):
        res = self.cur.execute("SELECT * FROM sqlite_master")
        for item in res.fetchall():
            if item[0] == "table":
                if item[1] not in db_up.keys() and item[1] != "sqlite_sequence": print("DEBUG --- found table that is not not part of ERD") #TODO maybe handle this somehow if extra table is found

                #TODO not sure if content check is actually needed
                has_content = self.__checkTableContent(item[1])
                if has_content:
                    print("DEBUG --- found table: '"+item[1]+"' that has content")
                else:
                    print("DEBUG --- found table: '"+item[1]+"' that is empty")

    def __checkTableContent(self, table_name):
        res = self.cur.execute("SELECT * FROM " + table_name + " LIMIT 10")
        if res.fetchone() is None:
            return False
        return True

    def closeConnection(self):
        self.con.close()

