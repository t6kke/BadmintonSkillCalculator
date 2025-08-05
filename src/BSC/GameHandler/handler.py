import sys
sys.path.append('../')

from BSC.PlayersAndTeams.players import Player
from BSC.PlayersAndTeams.teams import Team
from BSC.SkillCalculator.skillCalculator import SkillCalc

class Handler():
    def __init__(self, database_obj, verbose=False):
        self.verbose = verbose
        self.database_obj = database_obj

    def runGamesParser(self, raw_matches_list, tournament_id, category_id):
        converted_all_matches_list = [] #same list of matches list of dictionaries but content will be Teams objects that have set of player db_id-s

        players_obj_dict_in_tournament = {} #for not repeat checks of players in tournament. strcutre: 'db_id: player_obj'
        if self.verbose: print(f"INFO --- All matches list for parsing: '{raw_matches_list}'")
        if self.verbose: print(f"INFO --- Total nr of matches to parse: '{len(raw_matches_list)}'")
        i = 0
        for match in raw_matches_list:
            i = i + 1
            new_match_dict = {}
            if self.verbose: print(f"INFO --- Match nr: '{i}' --- Parsing raw match dictionary: '{match}'")
            for team, score in match.items():
                if self.verbose: print(f"INFO --- working on team: '{team}' that got '{score}' points")
                player_obj_list_for_team = []
                if "+" in team:
                    if self.verbose: print(f"DEBUG --- Detected '+' in the name, this is a team match and we need to split the players from the full team name")
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
                #if self.verbose: print(f"INFO --- creating new Team object with players: '{player_obj_list_for_team}'") #TODO fix printing problem
                team_obj = Team(player_obj_list_for_team)
                if self.verbose: print(f"INFO --- Team object: '{team_obj}' created")
                new_match_dict[team_obj] = score

            if self.verbose: print(f"INFO --- adding new match dictionary to converted matches list")
            converted_all_matches_list.append(new_match_dict)

        if self.verbose: print(f"INFO --- all matches are parsed, function midpoint before skill calculation and rest of DB entries")
        if self.verbose:
            print(f"INFO --- list of players in the tournament:")
            for p_id, p_obj in players_obj_dict_in_tournament.items():
                print(f"INFO --- player db id: '{p_id}', name: '{p_obj.player_name}', and ELO: '{p_obj.ELO}'")
            print(f"INFO --- list of converted games in the tournament with teams and scores:")
            i = 0
            for match in converted_all_matches_list:
                i = i + 1
                print(f"INFO --- match number: '{i}'")
                for team, score in match.items():
                    print(f"INFO --- team: '{team}' with score: '{score}'")

        print(f"Running ELO calculations...")
        skillCalculator = SkillCalc(players_obj_dict_in_tournament ,self.verbose)
        for match in converted_all_matches_list:
            #if self.verbose: print(f"INFO --- working with match: '{match}'") #TODO fix printing problem
            match_data_to_db = (tournament_id, category_id,)
            match_id = self.database_obj.AddMatch(match_data_to_db)

            game_nbr = 1 #TODO temp variable until scores are in a list and this tool needs to handle multi game matches

            game_data_to_db = (match_id, game_nbr, list(match.values())[0], list(match.values())[1],)
            game_id = self.database_obj.AddGame(game_data_to_db)

            #TODO analyze if players would be iterated over for the whole match so varaibles would not be needed
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
