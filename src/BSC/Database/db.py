import time
import os.path
import sqlite3

#from BSC.Database.sql_v01_001 import db_up
from BSC.Database.sql_001 import db_up, db_down

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
                           ("XD", "mixed double")]
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
    # General information
    #============================================

    def GetAvailableReports(self):
        if self.verbose: print(f"INFO --- DB:GetAvailableReports --- getting available reports options")
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        res = cur.execute("SELECT name FROM sqlite_master WHERE type='view' and name like 'report%'")
        report_views = []
        for item in res.fetchall():
            report_views.append(item[0])
        con.close()
        if self.verbose: print(f"INFO --- DB:GetAvailableReports --- returing all available reports")
        return report_views

    def GetAvailableCategories(self):
        if self.verbose: print(f"INFO --- DB:GetAvailableCategories --- getting available categories")
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        res = cur.execute("SELECT * FROM categories")
        categories_data = res.fetchall()
        con.close()
        if self.verbose: print(f"INFO --- DB:GetAvailableCategories --- returing all data about categories")
        return categories_data

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

    def GetOrAddPlayer(self, name, category_id):
        #TODO this function is a mess and needs to be cleaned up
        if self.verbose: print(f"INFO --- DB:GetOrAddPlayer --- getting or adding player '{name}' to DB")
        result = None
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        res = cur.execute("SELECT * FROM players WHERE name = '" + name + "'")
        result = res.fetchone() #note to self, fetchone removes the content form the result variable res, likely same with fetchall
        if result is None:
            if self.verbose: print(f"INFO --- DB:GetOrAddPlayer --- player not found in db, creating a new entry")
            player_data = (name,)
            res = cur.execute("INSERT INTO players (name) VALUES (?)", player_data)
            res = cur.execute("SELECT id FROM players ORDER BY id DESC LIMIT 1")
            player_id = res.fetchone()[0]
            elo_data = (player_id, category_id, 1000,) #TODO initial elo value of 1000 should be some configuration file, and maybe even modifiable based on what leage new player starts in.
            cur.execute("INSERT INTO players_categories_elo (player_id, category_id, elo) VALUES (?,?,?)", elo_data)
            con.commit()
            res = cur.execute("SELECT p.id, p.name, pce.elo FROM players p JOIN players_categories_elo pce ON p.id = pce.player_id WHERE pce.category_id = " + category_id + " AND p.name = '" + name + "'")
            result = res.fetchone()
            con.close()
            if self.verbose: print(f"INFO --- DB:GetOrAddPlayer --- returning db player entry: '{result}'")
            return result
        player_id = str(result[0])
        res = cur.execute("SELECT * FROM players_categories_elo WHERE category_id = " + category_id + " AND player_id = " + player_id)
        result = res.fetchone() #note to self, fetchone removes the content form the result variable res, likely same with fetchall
        if result is None:
            if self.verbose: print(f"INFO --- DB:GetOrAddPlayer --- player found in db but no ELO for category id {category_id}, creating a new entry")
            elo_data = (player_id, category_id, 1000,) #TODO initial elo value of 1000 should be some configuration file, and maybe even modifiable based on what leage new player starts in.
            cur.execute("INSERT INTO players_categories_elo (player_id, category_id, elo) VALUES (?,?,?)", elo_data)
            con.commit()
            res = cur.execute("SELECT p.id, p.name, pce.elo FROM players p JOIN players_categories_elo pce ON p.id = pce.player_id WHERE pce.category_id = " + category_id + " AND p.name = '" + name + "'")
            result = res.fetchone()
            con.close()
            if self.verbose: print(f"INFO --- DB:GetOrAddPlayer --- returning db player entry: '{result}'")
            return result
        res = cur.execute("SELECT p.id, p.name, pce.elo FROM players p JOIN players_categories_elo pce ON p.id = pce.player_id WHERE pce.category_id = " + category_id + " AND p.name = '" + name + "'")
        result = res.fetchone()
        con.close()
        if self.verbose: print(f"INFO --- DB:GetOrAddPlayer --- returning db player entry: '{result}'")
        return result

    def GetPlayerWithELO(self, name, category_id):
        if self.verbose: print(f"INFO --- DB:GetPlayerWithELO --- getting or adding player '{name}' to DB")
        result = None
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        res = cur.execute("SELECT p.id, p.name, pce.elo FROM players p JOIN players_categories_elo pce ON p.id = pce.player_id WHERE pce.category_id = " + category_id + " AND p.name = '" + name + "'")
        result = res.fetchone() #note to self, fetchone removes the content form the result variable res, likely same with fetchall
        if result is None:
            if self.verbose: print(f"INFO --- DB:GetPlayerWithELO --- player name not found in db, creating a new entry with base ELO: 1000")
            player_data = (name,)
            res = cur.execute("INSERT INTO players (name) VALUES (?)", player_data)
            res = cur.execute("SELECT id FROM players ORDER BY id DESC LIMIT 1")
            player_id = res.fetchone()[0]
            elo_data = (player_id, category_id, 1000,) #TODO initial elo value of 1000 should be some configuration file, and maybe even modifiable based on what leage new player starts in.
            cur.execute("INSERT INTO players_categories_elo (player_id, category_id, elo) VALUES (?,?,?)", elo_data)
            con.commit()
            res = cur.execute("SELECT p.id, p.name, pce.elo FROM players p JOIN players_categories_elo pce ON p.id = pce.player_id WHERE pce.category_id = " + category_id + " AND p.name = '" + name + "'")
            result = res.fetchone()
        con.close()
        if self.verbose: print(f"INFO --- DB:GetPlayerWithELO --- returning db player entry: '{result}'")
        return result

    def GetPlayerELO(self, player_id, category_id):
        if self.verbose: print(f"INFO --- DB:GetPlayerELO --- getting ELO value for player id: '{player_id}'")
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        res = cur.execute("SELECT elo FROM players_categories_elo WHERE category_id = " + category_id + " AND player_id = '" + player_id + "'")
        player_elo = res.fetchone()[0]
        con.close()
        if self.verbose: print(f"INFO --- DB:GetPlayerELO --- returning ELO value: '{player_elo}'")
        return player_elo

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
        cur.execute("INSERT INTO games (match_id, game_count, compeditor_one_score, compeditor_two_score) VALUES(?,?,?,?)", data_in)
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
        cur.executemany("INSERT INTO players_games (player_id, game_id, compeditor_nbr) VALUES(?,?,?)", data_in_list)
        con.commit()
        con.close()

    def AddPlayerMatchRel_W_ELOUpdate(self, data_in_list, category_id):
        def addPlayerMatchRel(data_in):
            if self.verbose: print(f"INFO --- DB:AddPlayerMatchRel_W_ELOUpdate:addPlayerMatchRel --- adding player match relation to DB with ELO data: '{data_in}'")
            con = sqlite3.connect(self.db_name)
            cur = con.cursor()
            cur.executemany("INSERT INTO players_matches_elo_change (player_id, match_id, player_start_elo, player_elo_change) VALUES(?,?,?,?)", data_in)
            con.commit()
            con.close()

        def updatePlayersELO(data_in):
            if self.verbose: print(f"INFO --- DB:AddPlayerMatchRel_W_ELOUpdate:updatePlayersELO --- updating player ELO value with following data: '{data_in}'")
            con = sqlite3.connect(self.db_name)
            cur = con.cursor()
            cur.executemany("UPDATE players_categories_elo SET elo = ? WHERE category_id = ? AND player_id = ?", data_in)
            con.commit()
            con.close()

        data_in_list_for_players_ELO_update = []
        for data_in in data_in_list:
            player_id = data_in[0]
            new_ELO = data_in[2] + data_in[3]
            data_in_list_for_players_ELO_update.append((new_ELO, category_id, player_id,))

        addPlayerMatchRel(data_in_list)
        updatePlayersELO(data_in_list_for_players_ELO_update)


    #============================================
    # results reports printing to terminal
    #============================================

    def report_AllPlayersELOrank(self):
        print("\nFull list of players and their ELO ranked from highest to lowest rank per category:")
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        #query = """SELECT p.name, pce.elo, c.name, c.description
#FROM players p
#JOIN players_categories_elo pce ON p.id = pce.player_id
#JOIN categories c ON c.id = pce.category_id
#ORDER BY c.name, pce.elo DESC"""
        query = """SELECT * FROM report_EloStandings"""
        res = cur.execute(query)
        data_list = res.fetchall()
        con.close()
        category_name = ""
        category_desc = ""
        for item in data_list:
            if item[4] != category_name:
                category_name = item[4]
                category_desc = item[5]
                print(f"\tRanking on category '{category_name}', '{category_desc}':")
            print(f"Player: '{item[1]}' with ELO: '{item[2]}'")

    def report_AllPlayersELOrankOnCategory(self, category_id):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        res = cur.execute("SELECT name, description FROM categories where id = "+str(category_id))
        category_data = res.fetchone()
        print(f"\nFull list of players and their ELO ranked from highest to lowest rank in category: '{category_data[0]}', '{category_data[1]}'")
        query = """SELECT player_name, ELO
FROM report_EloStandings
WHERE category_id = """ + str(category_id)
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
        query = """SELECT * FROM report_TournamentResults
WHERE tournament_id = """ + str(tournament_id)
        res = cur.execute(query)
        data_list = res.fetchall()
        con.close()
        position = 0
        for item in data_list:
            position += 1
            print(f"'Position: '{position}': '{item[4]}' played '{item[5]}' games and won: '{item[6]} games'. Points For: '{item[7]}'; Points Against: '{item[8]}'; Points Difference: '{item[9]}'")


    #============================================
    # static site generators
    #============================================

    def ss_AllPlayersELOrank(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        query = """SELECT p.name, pce.elo, c.name, c.description
FROM players p
JOIN players_categories_elo pce ON p.id = pce.player_id
JOIN categories c ON c.id = pce.category_id
ORDER BY c.name, pce.elo DESC"""
        res = cur.execute(query)
        data_list = res.fetchall()
        con.close()

        category_name = ""
        category_desc = ""

        with open("table.html", "w") as out_file:
            for item in data_list:
                if item[2] != category_name:
                    if category_name != "":
                        out_file.write("\t</tbody>\n</table>\n")
                    category_name = item[2]
                    category_desc = item[3]
                    out_file.write(f"<p>Rankings for category: '{category_desc}'</p>\n")
                    out_file.write("<table class=\"table table-bordered table-striped\">\n")
                    out_file.write("\t<thead>\n\t\t<tr>\n\t\t\t<th>Player</th>\n\t\t\t<th>ELO</th>\n\t\t</tr>\n\t</thead>\n")
                    out_file.write("\t<tbody>\n")
                out_file.write(f"\t\t<tr>\n\t\t\t<td>{item[0]}</td>\n\t\t\t<td>{item[1]}</td>\n\t\t</tr>\n")
            out_file.write("\t</tbody>\n</table>\n")
            out_file.close()
