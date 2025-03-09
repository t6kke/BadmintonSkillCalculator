import sys
sys.path.append('../')

from BSC.PlayersAndTeams.teams import Team, createTeamMembersSet

#TODO this should include function 'convertGameTeamToTeam()' from main.py and part(or all) of the logic from teamhandler.py
class Handler():
    def __init__(self, raw_games_list, verbose=False):
        #main object variables
        self.verbose = verbose
        self.raw_games_list = raw_games_list
        self.result_games_list = []
        self.result_teams_list = []

        #temporary object variables, various functions need it after multiple levels and don't want to pass them through fuctions if not needed. They will be reset to base values within function logic.
        self.temp_existing_teams_sets_list = []
        self.temp_game_from_raw_games = {}
        self.temp_new_team = None

        #run object logic, should always be executed when object is created, currently don't see a reason why it should be separately called mulitple times with different values
        self.__run()


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


    #============================================
    # main wokflow functions
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
            new_game_dict = self.__TeamsFromDictToTeamsObj(teams_from_dictionary_list)
            self.result_games_list.append(new_game_dict)

    def __TeamsFromDictToTeamsObj(self, teams_from_dictionary_list):
        for team_str in teams_from_dictionary_list:
            if self.verbose: print(f"INFO --- Parsing raw team string: '{team_str}'")
            temp_player_set = createTeamMembersSet(team_str, True)
            self.temp_new_team = None
            if len(self.temp_existing_teams_sets_list) == 0:
                if self.verbose: print(f"DEBUG --- no existing teams yet --- team set being handled: '{temp_player_set}' --- addint team: '{team_str}'")
                self.__insertTeamToList(team_str)
            self.__inseringRestOfTeams(team_str, temp_player_set)
            new_game_dict = self.__createNewGameDictWithTeamObj(team_str, temp_player_set)
        if self.verbose: print(f"DEBUG --- new game dictionary for return value: '{new_game_dict}'")
        return new_game_dict

    def __inseringRestOfTeams(self, team_str, temp_player_set):
        for i in range(len(self.temp_existing_teams_sets_list)):
            if self.verbose: print(f"DEBUG --- existing teams check --- LOOP: '{i}' --- comparing: '{temp_player_set}' vs. '{self.temp_existing_teams_sets_list[i]}'\nDEBUG --- full set of existing teams: '{self.temp_existing_teams_sets_list}'")
            if temp_player_set not in self.temp_existing_teams_sets_list:
                if self.verbose: print(f"DEBUG --- adding new team: '{team_str}'")
                self.__insertTeamToList(team_str)
            else:
                if self.verbose: print(f"DEBUG --- existing team, nothing to do")

    def __createNewGameDictWithTeamObj(self, team_str, temp_player_set):
        new_game_dict = {}
        if self.temp_new_team == None:
            for i in range(len(self.result_teams_list)):
                if self.verbose: print(f"DEBUG --- looking for team object from existing list for new game dictionary --- LOOP: '{i}' --- comparing: '{temp_player_set}' vs '{self.result_teams_list[i].team_member_set}'")
                if temp_player_set == self.result_teams_list[i].team_member_set:
                    if self.verbose: print(f"DEBUG --- found the team from result list '{self.result_teams_list[i]}', using the object in the new game dictionary")
                    new_game_dict[self.result_teams_list[i]] = self.temp_game_from_raw_games[team_str]
                    break
        else:
            if self.verbose: print(f"INFO --- team was known: '{self.temp_new_team}', adding the object to dictionary")
            new_game_dict[self.temp_new_team] = self.temp_game_from_raw_games[team_str]
        return new_game_dict


    #============================================
    # general purpos internal functions
    #============================================
    def __insertTeamToList(self, team_str):
        self.temp_new_team = Team(team_str, 1000)
        self.result_teams_list.append(self.temp_new_team)
        self.temp_existing_teams_sets_list.append(self.temp_new_team.team_member_set)
