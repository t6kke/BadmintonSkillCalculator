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


    #============================================
    # initialization functions
    #============================================

    def __validateAndInitalize(self):
        new_db = False
        if self.verbose: print("INFO --- database file name: ", self.db_name)
        if os.path.isfile("./"+self.db_name) == False:
            if self.verbose: print("INFO --- DB --- DB file does not exists, creating new one")
            new_db = True

        self.__createDB()
        if new_db:
            self.__createTables()
        elif self.clear_db:
            if self.verbose: print("INFO --- DB --- 'clear_db' flag is set so first dropping all tables and creating them again")
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
            if self.verbose: print(f"DEBUG --- DB --- Creating table: '{table}'")
            cur.execute(sql)
        if self.verbose: print(f"DEBUG --- DB --- adding default categories to db: '{categories_data}'")
        cur.executemany("INSERT INTO categories (name, description) VALUES(?,?)", categories_data)
        con.commit()
        con.close()

    def __validateDatabase(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        res = cur.execute("SELECT * FROM sqlite_master")
        for item in res.fetchall():
            if item[0] == "table":
                if item[1] not in db_up.keys() and item[1] != "sqlite_sequence": print("WARNING --- DB --- found table that is not not part of ERD") #TODO maybe handle this somehow if extra table is found

                #TODO not sure if content check is actually needed
                has_content = self.__checkTableContent(cur, item[1])
                if has_content:
                    if self.verbose: print("DEBUG --- DB --- found table: '"+item[1]+"' that has content")
                else:
                    if self.verbose: print("DEBUG --- DB --- found table: '"+item[1]+"' with no data")
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
            if self.verbose: print(f"DEBUG --- DB --- Dropping table: '{table}'")
            cur.execute(sql)
        con.commit()
        con.close()


    #============================================
    # functions for adding data to database
    #============================================

    def AddTournament(self, data_in):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("INSERT INTO tournaments (name) VALUES(?)", data_in)
        res = cur.execute("SELECT id FROM tournaments ORDER BY id DESC LIMIT 1")
        tournament_id = res.fetchone()[0]
        con.commit()
        con.close()
        return tournament_id

    def GetOrAddCategory(self, category_name, category_description):
        category_id = None
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        res = cur.execute("SELECT id FROM categories WHERE name = '" + category_name +"'")
        category_id = res.fetchone()
        if category_id is None:
            if self.verbose: print("INFO --- DB:GetOrAddCategory --- category does not exist in db, creating new one")
            data_in = (category_name, category_description, )
            cur.execute("INSERT INTO categories (name, description) VALUES(?,?)", data_in)
            con.commit()
            res = cur.execute("SELECT id FROM categories WHERE name = '" + category_name +"'")
            category_id = res.fetchone()
        con.close()
        return category_id[0]

    def GetPlayer(self, name):
        if self.verbose: print(f"INFO --- DB:GetPlayer --- getting or adding player '{name}' to DB")
        result = None
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        res = cur.execute("SELECT * FROM users WHERE name = '" + name +"'")
        result = res.fetchone() #note to self, fetchone removes the content form the result variable res, likely same with fetchall
        if result is None:
            if self.verbose: print(f"INFO --- DB:GetPlayer --- player name not found in db, creating a new entry with base ELO: 1000")
            data = (name, 1000) #TODO initial elo value of 1000 should be some configuration file, and maybe even modifiable based on what leage new player starts in.
            res = cur.execute("INSERT INTO users (name, elo) VALUES (?,?)", data)
            con.commit()
            res = cur.execute("SELECT * FROM users WHERE name = '" + name +"'")
            result = res.fetchone()
        con.close()
        if self.verbose: print(f"INFO --- DB:GetPlayer --- returning db player entry: '{result}'")
        return result

    def GetPlayerELO(self, user_id):
        if self.verbose: print(f"INFO --- DB:GetPlayerELO --- getting ELO value for player id: '{user_id}'")
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        res = cur.execute("SELECT elo FROM users WHERE id = '" + user_id +"'")
        user_elo = res.fetchone()[0]
        con.close()
        if self.verbose: print(f"INFO --- DB:GetPlayerELO --- returning ELO value: '{user_elo}'")
        return user_elo

    def AddMatch(self, data_in):
        if self.verbose: print(f"INFO --- DB:AddMatch --- adding match to DB with data: '{data_in}'")
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("INSERT INTO matches (tournament_id, category_id) VALUES(?,?)", data_in)
        con.commit()
        res = cur.execute("SELECT id FROM matches ORDER BY id DESC LIMIT 1")
        match_id = res.fetchone()[0]
        con.close()
        if self.verbose: print(f"INFO --- DB:AddMatch --- returning match id: '{match_id}'")
        return match_id

    def AddGame(self, data_in):
        if self.verbose: print(f"INFO --- DB:AddGame --- adding game to DB with data: '{data_in}'")
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("INSERT INTO games (match_id, game_count, player_one_score, player_two_score) VALUES(?,?,?,?)", data_in)
        con.commit()
        res = cur.execute("SELECT id FROM games ORDER BY id DESC LIMIT 1")
        game_id = res.fetchone()[0]
        con.close()
        if self.verbose: print(f"INFO --- DB:AddGame --- returning game id: '{game_id}'")
        return game_id

    def AddPlayerGameRel(self, data_in_list):
        if self.verbose: print(f"INFO --- DB:AddPlayerGameRel --- adding player game relation for the whole match for all players with data: '{data_in_list}'")
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.executemany("INSERT INTO users_games (users_id, games_id, comp_nbr) VALUES(?,?,?)", data_in_list)
        con.commit()
        con.close()

    def AddPlayerMatchRel_W_ELOUpdate(self, data_in_list):
        def addPlayerMatchRel(data_in):
            if self.verbose: print(f"INFO --- DB:AddPlayerMatchRel_W_ELOUpdate:addPlayerMatchRel --- adding player match relation to DB with ELO data: '{data_in}'")
            con = sqlite3.connect(self.db_name)
            cur = con.cursor()
            cur.executemany("INSERT INTO users_matches_elo_change (users_id, matches_id, user_start_elo, user_elo_change) VALUES(?,?,?,?)", data_in)
            con.commit()
            con.close()

        def updateUsersELO(data_in):
            if self.verbose: print(f"INFO --- DB:AddPlayerMatchRel_W_ELOUpdate:updateUsersELO --- updating users ELO value with following data: '{data_in}'")
            con = sqlite3.connect(self.db_name)
            cur = con.cursor()
            cur.executemany("UPDATE users SET elo = ? WHERE id = ?", data_in)
            con.commit()
            con.close()

        data_in_list_for_users_ELO_update = []
        for data_in in data_in_list:
            user_id = data_in[0]
            new_ELO = data_in[2] + data_in[3]
            data_in_list_for_users_ELO_update.append((new_ELO, user_id,))

        addPlayerMatchRel(data_in_list)
        updateUsersELO(data_in_list_for_users_ELO_update)


    #============================================
    # results reports printing to terminal
    #============================================

    def report_AllUsersELOrank(self):
        print("\nFull list of players and their ELO ranked from highest to lowest rank:")
        query = "SELECT name, elo FROM users ORDER BY elo DESC"
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        res = cur.execute(query)
        data_list = res.fetchall()
        con.close()
        for item in data_list:
            print(f"Player: '{item[0]}' with ELO: '{item[1]}'")

    def report_TournamentResult(self, tournament_id):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        res = cur.execute("SELECT name FROM tournaments where id = "+str(tournament_id))
        print(f"\nEnd statistics and final ELO ranking from tournament: '{res.fetchone()[0]}'")
        query = """SELECT DISTINCT u.name, u.elo, statistics.nbr_matches, statistics.victories
FROM matches m
JOIN users_matches_elo_change um ON m.id = um.matches_id
JOIN users u ON u.id = um.users_id
JOIN (
SELECT
u.id,
u.name,
count(g.id) as nbr_matches,
SUM(IIF(CASE ug.comp_nbr WHEN '1' THEN g.player_one_score ELSE g.player_two_score END > CASE ug.comp_nbr WHEN '1' THEN g.player_two_score ELSE g.player_one_score END, 1, 0)) victories
FROM users u
JOIN users_games ug ON u.id = ug.users_id
JOIN games g ON ug.games_id = g.id
JOIN matches m ON m.id = g.match_id
WHERE m.tournament_id = """ + str(tournament_id) + """ group by u.name
) statistics ON statistics.id = u.id
ORDER BY u.elo DESC"""
        res = cur.execute(query)
        data_list = res.fetchall()
        con.close()
        for item in data_list:
            print(f"Player: '{item[0]}' with final ELO: '{item[1]}' played '{item[2]}' games and won: '{item[3]} games'")
