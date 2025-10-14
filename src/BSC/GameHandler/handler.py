import sys
sys.path.append('../')

from BSC.PlayersAndTeams.players import Player
from BSC.PlayersAndTeams.teams import Team
from BSC.SkillCalculator.skillCalculator import SkillCalc

class Handler():
    def __init__(self, database_obj, output,verbose=False):
        self.verbose = verbose
        self.output = output
        self.database_obj = database_obj

    def runGamesParser(self, raw_matches_list, tournament_id, category_id):
        converted_all_matches_list = [] #same list of matches list of dictionaries but content will be Teams objects that have set of player db_id-s
        players_obj_dict_in_tournament = {} #for not repeat checks of players in tournament. strcutre: 'db_id: player_obj'

        def playerParser(player):
            player_db_entry = self.database_obj.GetOrAddPlayer(player.strip(), str(category_id))
            player_exists = False
            if player_db_entry[0] in players_obj_dict_in_tournament:
                self.output.write(self.verbose, "INFO", None, message=f"player exists in the tournament players list, using entry there to add to the team list for Team object")
                player_exists = True
                player_obj_list_for_team.append(players_obj_dict_in_tournament.get(player_db_entry[0]))
            if player_exists == False:
                self.output.write(self.verbose, "DEBUG", None, message=f"player obj not yet created and not in the current tournament players list")
                player_obj = Player(player_db_entry[0], player_db_entry[1], player_db_entry[2])
                self.output.write(self.verbose, "DEBUG", None, message=f"created new player object: '{player_obj}'")
                players_obj_dict_in_tournament[player_obj.db_id] = player_obj
                player_obj_list_for_team.append(player_obj)
                self.output.write(self.verbose, "DEBUG", None, message=f"player object added to the current tournament players list and also added to a list for Team object")

        self.output.write(self.verbose, "INFO", None, message=f"All matches list for parsing: '{raw_matches_list}'")
        self.output.write(self.verbose, "INFO", None, message=f"Total nr of matches to parse: '{len(raw_matches_list)}'")
        i = 0
        for match in raw_matches_list:
            i = i + 1
            new_match_dict = {}
            self.output.write(self.verbose, "INFO", None, match_number=i, message=f"Parsing raw match dictionary: '{match}'")
            for team, score in match.items():
                self.output.write(self.verbose, "INFO", None, message=f"working on team: '{team}' that got '{score}' points")
                player_obj_list_for_team = []
                if "+" in team:
                    self.output.write(self.verbose, "DEBUG", None, message=f"Detected '+' in the name, this is a team match and we need to split the players from the full team name")
                    player_str_list = team.split("+")
                    for player in player_str_list:
                        self.output.write(self.verbose, "DEBUG", None, message=f"team is split into players: '{player_str_list}' and working on player '{player}'")
                        playerParser(player)
                else:
                    self.output.write(self.verbose, "DEBUG", None, message=f"Only single name detected in team area, must be singles tournament")
                    playerParser(team)
                #if self.verbose: print(f"INFO --- creating new Team object with players: '{player_obj_list_for_team}'") #TODO fix printing problem
                team_obj = Team(player_obj_list_for_team)
                self.output.write(self.verbose, "INFO", None, message=f"Team object: '{team_obj}' created")
                new_match_dict[team_obj] = score

            self.output.write(self.verbose, "INFO", None, message=f"adding new match dictionary to converted matches list")
            converted_all_matches_list.append(new_match_dict)

        self.output.write(self.verbose, "INFO", None, message=f"all matches are parsed, function midpoint before skill calculation and rest of DB entries")
        if self.verbose:
            self.output.write(self.verbose, "INFO", None, message=f"list of players in the tournament:")
            for p_id, p_obj in players_obj_dict_in_tournament.items():
                self.output.write(self.verbose, "INFO", None, message=f"player db id: '{p_id}', name: '{p_obj.player_name}', and ELO: '{p_obj.ELO}'")
            self.output.write(self.verbose, "INFO", None, message=f"list of converted games in the tournament with teams and scores:")
            i = 0
            for match in converted_all_matches_list:
                i = i + 1
                self.output.write(self.verbose, "INFO", None, message=f"match number: '{i}'")
                for team, score in match.items():
                    self.output.write(self.verbose, "INFO", None, message=f"team: '{team}' with score: '{score}'")

        self.output.write(False, "INFO", None, message=f"Running ELO calculations...")
        skillCalculator = SkillCalc(players_obj_dict_in_tournament, self.output, self.verbose)
        for match in converted_all_matches_list:
            #if self.verbose: print(f"INFO --- working with match: '{match}'") #TODO fix printing problem
            match_data_to_db = (tournament_id, category_id,)
            match_id = self.database_obj.AddMatch(match_data_to_db)

            game_nbr = 1 #TODO temp variable until scores are in a list and this tool needs to handle multi game matches

            game_data_to_db = (match_id, game_nbr, list(match.values())[0], list(match.values())[1],)
            game_id = self.database_obj.AddGame(game_data_to_db)

            self.output.write(self.verbose, "INFO", None, message=f"running ELO calculation for the match")
            elo_results_dict = skillCalculator.calculate(match)
            self.output.write(self.verbose, "INFO", None, message=f"results of ELO calculation: '{elo_results_dict}'")

            players_games_rel_to_db = []
            players_matches_rel_wELOupdate_to_db = []
            compeditor_nbr = 0
            for team, score in match.items():
                compeditor_nbr = compeditor_nbr + 1
                for player_id in team.team_members_set:
                    players_games_rel_to_db.append((player_id, game_id, compeditor_nbr))
                    players_matches_rel_wELOupdate_to_db.append((player_id, match_id, players_obj_dict_in_tournament.get(player_id).ELO, elo_results_dict.get(player_id)))

            self.database_obj.AddPlayerGameRel(players_games_rel_to_db)
            self.database_obj.AddPlayerMatchRel_W_ELOUpdate(players_matches_rel_wELOupdate_to_db, category_id)

            self.output.write(self.verbose, "INFO", None, message=f"updating player object ELO value with updated data")
            for player_id, player_obj in players_obj_dict_in_tournament.items():
                self.output.write(self.verbose, "INFO", None, message=f"updating ELO for player: '{player_obj}'")
                player_obj.ELO = self.database_obj.GetPlayerELO(str(player_id), str(category_id))
