import sys
sys.path.append('../')

from BSC.PlayersAndTeams.teams import Team, createTeamMembersSet
from BSC.PlayersAndTeams.players import Player
from BSC.PlayersAndTeams.teams import Team_v2
from BSC.SkillCalculator.skillCalculator import SkillCalc

class Handler():
    def __init__(self, raw_games_list, database_obj, verbose=False):
        # main object variables
        self.verbose = verbose
        self.raw_games_list = raw_games_list
        self.database_obj = database_obj
        self.result_games_list = []
        self.result_teams_list = []

        # temporary object variables, various functions need it after multiple levels and don't want to pass them through fuctions if not needed. They will be reset to base values within function logic.
        self.temp_existing_teams_sets_list = []
        self.temp_game_from_raw_games = {}
        self.temp_new_team = None
        self.temp_game_dict = {}

        # Run inital object logic, should always be executed when object is created.
        # it parses the raw games dictionaries, extracts the teams strings and creates teams objects,
        # makes sure that duplicates are not created. Recreates the game dictionary using the team objects
        # instead of the original team string.
        #
        # Currently don't see a reason why it should be separately called mulitple times.
        # Maybe in the future if games data is extracted multiple times and then added
        # multiple times into this object the __run() function needs to be executed again.
        # But this will create more problems. Something to resolve in the future if needed.
        #self.__run()
        self.__run_NEW()


    #============================================
    # public functions
    #============================================
    def getGamesList(self):
        if len(self.result_games_list) == 0:
            raise Exception("No games found")
        if self.verbose: print(f"INFO --- returning: '{self.result_games_list}'")
        return self.result_games_list

    def getTeamsList(self):
        if len(self.result_teams_list) == 0:
            raise Exception("No teams found")
        if self.verbose: print(f"INFO --- returning: '{self.result_teams_list}'")
        return self.result_teams_list

    def calculateScore(self):
        if len(self.result_games_list) == 0:
            raise Exception("no games found exception")
        if self.verbose: print(f"INFO --- running ELO calculations for games: '{self.result_games_list}'")
        for game in self.result_games_list:
            if self.verbose: print(f"INFO --- handling game: '{game}'")
            team1 = list(game)[0]
            team2 = list(game)[1]
            if game.get(team1) > game.get(team2):
                if self.verbose: print(f"INFO --- game winner was: '{team1}'")
                self.__runCalculations(team1, team2, 1)
            else:
                if self.verbose: print(f"INFO --- game winner was: '{team2}'")
                self.__runCalculations(team1, team2, 2)

    def reportFullGamesList(self):
        print(f"\nAllTeams:\n'{self.result_games_list}'") #TODO make it look better

    def reportFullTeamsList(self):
        print(f"\nAllTeams:\n'{self.result_teams_list}'") #TODO make it look better

    def reportCalculationsResult(self):
        print("\nFinal resutls:")
        for team in self.result_teams_list:
            print(team.information())
        #TODO make the print out list to be in DESC order


    #============================================
    # new initiation wokflow functions
    #============================================
    def __run_NEW(self):
        #TODO print statments here eventually need to be changed to be behind verbose check or if needed actual results.
        converted_all_games_list = [] #same list of games list of dictionaries but content will be Teams objects that have set of player db_id-s

        players_obj_dict_in_tournament = {} #for not repeat checks of players in tournament. strcutre: 'db_id: player_obj'
        if self.verbose: print(f"INFO --- Raw games list for parsing: '{self.raw_games_list}'")
        for game in self.raw_games_list:
            if self.verbose: print(f"INFO --- Parsing raw game dictionary: '{game}'")
            print("Working on game:", game)
            new_game_dict_wObjects = {} #same kind of dictionary structure but Teams instead of being just a string is a Team object that consists of Player db_id in a set() data type
            for team, score in game.items():
                print(team, score)
                if "+" in team:
                    print("we have team with multiple members, need to split into multiple players")
                    player_str_list = team.split("+")
                    player_obj_list_for_team = []
                    for player in player_str_list:
                        player_db_entry = self.database_obj.GetPlayer(player.strip())
                        player_exists = False
                        if player_db_entry[0] in players_obj_dict_in_tournament:
                            player_exists = True
                            player_obj_list_for_team.append(players_obj_dict_in_tournament.get(player_db_entry[0]))
                        if player_exists == False:
                            player_obj = Player(player_db_entry[0], player_db_entry[1], player_db_entry[2])
                            players_obj_dict_in_tournament[player_obj.db_id] = player_obj
                            player_obj_list_for_team.append(player_obj)
                    for player_obj in player_obj_list_for_team:
                        print("player in the list for team obj:", player_obj)
                    #TODO fill the team object and put it into the new game data
                else:
                    print("singles player, singles tournament")
                    #TODO do the single player handling as for others
        for p_id, p_obj in players_obj_dict_in_tournament.items():
            print(p_id, p_obj.player_name, p_obj.ELO)

            #TODO list of players is used to compile a team object to validate new or existing team

            #TODO for next DB entries steps
            #TODO game(s) needs to be stored into db
            #TODO players and games relation entrie needs to be done
            #TODO matches entrie needs to be done but it requires tournament entri and categories entry beforehand.





    #============================================
    # initiation wokflow functions
    # outdated from prototype v3
    #============================================
    def __run(self):
        if self.verbose: print(f"INFO --- Raw games list for parsing: '{self.raw_games_list}'")
        for game in self.raw_games_list:
            if self.verbose: print(f"INFO --- Parsing raw game dictionary: '{game}'")
            self.temp_existing_teams_sets_list = []
            self.temp_game_from_raw_games = game
            for t in self.result_teams_list: #creating existing teams list for duplicate check
                self.temp_existing_teams_sets_list.append(t.team_member_set)
            teams_from_dictionary_list = self.temp_game_from_raw_games.keys()
            game_dict = self.__TeamsFromDictToTeamsObj(teams_from_dictionary_list)
            self.result_games_list.append(game_dict)

    def __TeamsFromDictToTeamsObj(self, teams_from_dictionary_list):
        self.temp_game_dict = {}
        print(teams_from_dictionary_list)
        for team_str in teams_from_dictionary_list:
            print(team_str)
            if self.verbose: print(f"INFO --- Parsing raw team string: '{team_str}'")
            temp_player_set = createTeamMembersSet(team_str, self.database_obj, self.verbose)
            self.temp_new_team = None
            if len(self.temp_existing_teams_sets_list) == 0:
                if self.verbose: print(f"DEBUG --- no existing teams yet --- team set being handled: '{temp_player_set}' --- adding team: '{team_str}'")
                self.__insertTeamToList(team_str)
            self.__inseringRestOfTeams(team_str, temp_player_set)
            self.temp_game_dict = self.__createNewGameDictWithTeamObj(team_str, temp_player_set)
        if self.verbose: print(f"DEBUG --- new game dictionary for return value: '{self.temp_game_dict}'")
        return self.temp_game_dict

    def __inseringRestOfTeams(self, team_str, temp_player_set):
        for i in range(len(self.temp_existing_teams_sets_list)):
            if self.verbose: print(f"DEBUG --- existing teams check --- LOOP: '{i}' --- comparing: '{temp_player_set}' vs. '{self.temp_existing_teams_sets_list[i]}'\nDEBUG --- full set of existing teams: '{self.temp_existing_teams_sets_list}'")
            if temp_player_set not in self.temp_existing_teams_sets_list:
                if self.verbose: print(f"DEBUG --- adding new team: '{team_str}'")
                self.__insertTeamToList(team_str)
            else:
                if self.verbose: print(f"DEBUG --- existing team, nothing to do")

    def __createNewGameDictWithTeamObj(self, team_str, temp_player_set):
        if self.temp_new_team == None:
            for i in range(len(self.result_teams_list)):
                if self.verbose: print(f"DEBUG --- looking for team object from existing list for new game dictionary --- LOOP: '{i}' --- comparing: '{temp_player_set}' vs '{self.result_teams_list[i].team_member_set}'")
                if temp_player_set == self.result_teams_list[i].team_member_set:
                    if self.verbose: print(f"DEBUG --- found the team from result list '{self.result_teams_list[i]}', using the object in the new game dictionary")
                    self.temp_game_dict[self.result_teams_list[i]] = self.temp_game_from_raw_games[team_str]
                    break
        else:
            if self.verbose: print(f"INFO --- team was known: '{self.temp_new_team}', adding the object to dictionary")
            self.temp_game_dict[self.temp_new_team] = self.temp_game_from_raw_games[team_str]
        return self.temp_game_dict


    #============================================
    # general purpos internal functions for initial run
    #============================================
    def __insertTeamToList(self, team_str):
        if self.verbose: print(f"INFO --- creating team object from string '{team_str}' and adding it to the result teams list")
        self.temp_new_team = Team(team_str, self.database_obj, 1000)
        self.result_teams_list.append(self.temp_new_team)
        self.temp_existing_teams_sets_list.append(self.temp_new_team.team_member_set)


    #============================================
    # game result calculation functions
    #============================================

    def __runCalculations(self, team1, team2, winner):
        team_one = None
        team_two = None
        for team in self.result_teams_list:
            if team == team1:
                team_one = team
            elif team == team2:
                team_two = team
        if team_one == None or team_two == None:
            raise Exception("Team(s) missing excpetion")
        if winner == 1:
            team_one.victories_count += 1
        elif winner == 2:
            team_two.victories_count += 1
        skillCalculator = SkillCalc(self.verbose)       # somewhat basic self built ELO calculator
        skillCalculator.addTeams(team_one, team_two)
        skillCalculator.calculate(winner)
        self.__incrementGameCount(team_one, team_two)

    def __incrementGameCount(self, team_one, team_two):
        if self.verbose: print(f"INFO --- incrementing teams total played games count")
        team_one.games_played += 1
        team_two.games_played += 1
