class SkillCalc():
    def __init__(self, players_obj_dict, output, verbose=False):
        self.verbose = verbose #TODO extend verbose information to stuff that might be relevant
        self.output = output
        self.k_factor = 32 #TODO there should be 2 K-Factor variables, one for winner and one loser. when we have implemented ELO confidence value. example high ELO player will not lose a lot of points if new team with base/low ELO beats them
        self.players_obj_dict = players_obj_dict

    def calculate(self, match):
        resut_ELO_changes_dict = {}
        for i in range(len(match)):
            team = list(match.keys())[i]
            result = self.__getWinStatus(match, team)
            for player_id in team.team_members_set:
                current_ELO = self.players_obj_dict.get(player_id).ELO
                expectation = 1/(1+10**((current_ELO - current_ELO) / 400))
                opposing_team = list(match.keys())[i-1]
                total_ELO_change = 0
                for oppoent_id in opposing_team.team_members_set:
                    ELO_diff = current_ELO - self.players_obj_dict.get(oppoent_id).ELO
                    self.__scaleKFactor(result, ELO_diff)
                    ELO_change = self.k_factor*(result - expectation)
                    total_ELO_change = total_ELO_change + int(ELO_change)
                resut_ELO_changes_dict[player_id] = total_ELO_change
        return resut_ELO_changes_dict

    def __scaleKFactor(self, win_status, ELO_diff):
        self.output.write(self.verbose, "SkillCalc:__scaleKFactor", None, message=f"ELO difference: '{ELO_diff}'")
        #TODO investigate can this if else logic be simplified
        if win_status == 1 and ELO_diff > 0:
            # I win and have higher ELO so k_factor has to scale down based on difference
            self.__KFactorDOWN(abs(ELO_diff))
        elif win_status == 1 and ELO_diff < 0:
            # I win and have lower ELO so k_factor has to scale up based on the difference
            self.__KFactorUP(abs(ELO_diff))
        elif win_status == 0 and ELO_diff > 0:
            # I win and have lower ELO so k_factor has to scale up based on the difference
            self.__KFactorUP(abs(ELO_diff))
        elif win_status == 0 and ELO_diff < 0:
            # I win and have higher ELO so k_factor has to scale down based on difference
            self.__KFactorDOWN(abs(ELO_diff))
        else:
            # default just in case
            self.k_factor = 32

    #TODO analyze if k-factor scaling values should be external, configuration file or maybe even some database entry.
    def __KFactorUP(self, ELO_diff):
        if ELO_diff > 200:
            self.k_factor = 70
        elif ELO_diff <= 200 and ELO_diff > 100:
            self.k_factor = 52
        elif ELO_diff <= 100 and ELO_diff > 20:
            self.k_factor = 40
        elif ELO_diff <= 20 and ELO_diff > 0:
            self.k_factor = 32

    def __KFactorDOWN(self, ELO_diff):
        if ELO_diff > 200:
            self.k_factor = 2
        elif ELO_diff <= 200 and ELO_diff > 100:
            self.k_factor = 12
        elif ELO_diff <= 100 and ELO_diff > 20:
            self.k_factor = 24
        elif ELO_diff <= 20 and ELO_diff > 0:
            self.k_factor = 32

    def __getWinStatus(self, match, team):
        result = None
        match_copy = match.copy()
        my_score = match_copy.pop(team)
        opponent_score = match_copy.get(next(iter(match_copy))) #TODO find a better way to get the other teams score from dictionary
        if my_score > opponent_score:
            result = 1
        else:
            result = 0
        #print(my_score, opponent_score, result)
        return result
