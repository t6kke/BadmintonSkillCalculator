import sys
sys.path.append('../')

from BSC.PlayersAndTeams.teams import Team, createTeamMembersSet
from BSC.PlayersAndTeams.players import Player
from BSC.PlayersAndTeams.teams import Team_v2
from BSC.SkillCalculator.skillCalculator import SkillCalc
from BSC.SkillCalculator.skillCalculator import SkillCalc_v2

class Handler():
    def __init__(self, raw_games_list, database_obj, tournament_id, category_id, verbose=False):
        # main object variables
        self.verbose = verbose
        self.raw_games_list = raw_games_list
        self.database_obj = database_obj
        self.tournament_id = tournament_id
        self.category_id = category_id
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
        converted_all_matches_list = [] #same list of games list of dictionaries but content will be Teams objects that have set of player db_id-s

        players_obj_dict_in_tournament = {} #for not repeat checks of players in tournament. strcutre: 'db_id: player_obj'
        if self.verbose: print(f"INFO --- All games list for parsing: '{self.raw_games_list}'")
        if self.verbose: print(f"INFO --- Total nr of games to parse: '{len(self.raw_games_list)}'")
        i = 0
        for game in self.raw_games_list:
            i = i + 1
            new_game_dict = {}
            if self.verbose: print(f"INFO --- Game nr: '{i}' --- Parsing raw game dictionary: '{game}'")
            new_game_dict_wObjects = {} #same kind of dictionary structure but Teams instead of being just a string is a Team object that consists of Player db_id in a set() data type
            for team, score in game.items():
                if self.verbose: print(f"INFO --- working on team: '{team}' that got '{score}' points")
                player_obj_list_for_team = []
                if "+" in team:
                    if self.verbose: print(f"DEBUG --- Detected '+' in the name, this is a team game and we need to split the players from the full team name")
                    player_str_list = team.split("+")
                    for player in player_str_list:
                        #TODO content of this for loop likely can be separate function since this should be reusable for single player tournaments
                        if self.verbose: print(f"DEBUG --- team is split into players: '{player_str_list}' and working on player '{player}'")
                        player_db_entry = self.database_obj.GetPlayer(player.strip())
                        player_exists = False
                        if player_db_entry[0] in players_obj_dict_in_tournament:
                            if self.verbose: print(f"INFO --- player exists in the tournament players list, using entry there to add to the team list for Team object")
                            player_exists = True
                            player_obj_list_for_team.append(players_obj_dict_in_tournament.get(player_db_entry[0]))
                        if player_exists == False:
                            if self.verbose: print(f"DEBUG --- player obj not yet created and not in the current tournament players list")
                            player_obj = Player(player_db_entry[0], player_db_entry[1], player_db_entry[2])
                            if self.verbose: print(f"DEBUG --- created new player object: '{player_obj}'")
                            players_obj_dict_in_tournament[player_obj.db_id] = player_obj
                            player_obj_list_for_team.append(player_obj)
                            if self.verbose: print(f"DEBUG --- player object added to the current tournament players list and also added to a list for Team object")
                else:
                    if self.verbose: print(f"DEBUG --- Only single name detected in team area, must be singles tournament")
                    #TODO do the single player handling the same way it's done for doubles
                #if self.verbose: print(f"INFO --- creating new Team_v2 object with players: '{player_obj_list_for_team}'") #TODO fix printing problem
                team_obj = Team_v2(player_obj_list_for_team)
                if self.verbose: print(f"INFO --- Team object: '{team_obj}' created")
                new_game_dict[team_obj] = score

            if self.verbose: print(f"INFO --- adding new game dictionary to converted games list")
            converted_all_matches_list.append(new_game_dict)

        if self.verbose: print(f"INFO --- all games are parsed, function midpoint before skill calculation and rest of DB entries")
        if self.verbose:
            print(f"INFO --- list of players in the tournament:")
            for p_id, p_obj in players_obj_dict_in_tournament.items():
                print(f"INFO --- player db id: '{p_id}', name: '{p_obj.player_name}', and ELO: '{p_obj.ELO}'")
            print(f"INFO --- list of converted games in the tournament with teams and scores:")
            i = 0
            for game in converted_all_matches_list:
                i = i + 1
                print(f"INFO --- game number: '{i}'")
                for team, score in game.items():
                    print(f"INFO --- team: '{team}' with score: '{score}'")

        print(f"Running ELO calculations...")
        skillCalculator = SkillCalc_v2(players_obj_dict_in_tournament ,self.verbose)
        for match in converted_all_matches_list:
            #if self.verbose: print(f"INFO --- working with match: '{match}'") #TODO fix printing problem
            match_data_to_db = (self.tournament_id, self.category_id,)
            match_id = self.database_obj.AddMatch(match_data_to_db)

            game_nbr = 1 #TODO temp variable until scores are in a list and this tool needs to handle multi game matches

            game_data_to_db = (match_id, game_nbr, list(match.values())[0], list(match.values())[1],)
            game_id = self.database_obj.AddGame(game_data_to_db)

            #TODO analyze if players would be iterated over for the whole game so varaibles would not be needed
            t_one_p_one_id = list(list(match.keys())[0].team_members_set)[0]
            t_one_p_two_id = list(list(match.keys())[0].team_members_set)[1]
            t_two_p_one_id = list(list(match.keys())[1].team_members_set)[0]
            t_two_p_two_id = list(list(match.keys())[1].team_members_set)[1]
            players_games_rel_to_db = [(t_one_p_one_id, game_id, "1"),
                                       (t_one_p_two_id, game_id, "1"),
                                       (t_two_p_one_id, game_id, "2"),
                                       (t_two_p_two_id, game_id, "2")]
            self.database_obj.AddPlayerGameRel(players_games_rel_to_db)

            if self.verbose: print(f"INFO --- running ELO calculation for the match")
            elo_results_dict = skillCalculator.calculate(match)
            if self.verbose: print(f"INFO --- results of ELO calculation: '{elo_results_dict}'")
            players_matches_rel_wELOupdate_to_db = [(t_one_p_one_id, match_id, players_obj_dict_in_tournament.get(t_one_p_one_id).ELO, elo_results_dict.get(t_one_p_one_id)),
                                                    (t_one_p_two_id, match_id, players_obj_dict_in_tournament.get(t_one_p_two_id).ELO, elo_results_dict.get(t_one_p_two_id)),
                                                    (t_two_p_one_id, match_id, players_obj_dict_in_tournament.get(t_two_p_one_id).ELO, elo_results_dict.get(t_two_p_one_id)),
                                                    (t_two_p_two_id, match_id, players_obj_dict_in_tournament.get(t_two_p_two_id).ELO, elo_results_dict.get(t_two_p_two_id)),]
            self.database_obj.AddPlayerMatchRel_W_ELOUpdate(players_matches_rel_wELOupdate_to_db)

            if self.verbose: print(f"INFO --- updating player object ELO value with updated data")
            for player_id, player_obj in players_obj_dict_in_tournament.items():
                if self.verbose: print(f"INFO --- updating ELO for player: '{player_obj}'")
                player_obj.ELO = self.database_obj.GetPlayerELO(str(player_id))





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
