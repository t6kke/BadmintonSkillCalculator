#TODO analyze if k-factor values should be external, configuration file or maybe even some database entry.
K_FACTOR_DEFAULT = 32
K_FACTOR_MAP = {"l": [1, 8, 16, 24, 32],
                "h": [72, 56, 48, 40, 32]}


class SkillCalc():
    def __init__(self, output, verbose=False):
        self.verbose = verbose #TODO extend verbose information
        self.output = output
        self.k_factor = None

    def calculate(self, winning_team_obj, losing_team_obj):
        resut_ELO_changes_dict = {}
        teams = [losing_team_obj, winning_team_obj]
        for i in range(len(teams)):
            result = i
            team = teams[i]
            opponent_team = teams[i-1]
            for player_id in team.team_members_set:
                my_current_ELO = team.team_members_dict.get(player_id).ELO
                my_current_ELO_confidence = team.team_members_dict.get(player_id).ELO_confidence_level
                total_ELO_change = 0
                for oppoent_id in opponent_team.team_members_set:
                    opponents_ELO = opponent_team.team_members_dict.get(oppoent_id).ELO
                    opponents_ELO_confidence = opponent_team.team_members_dict.get(oppoent_id).ELO_confidence_level
                    expectation = 1/(1+10**((my_current_ELO - opponents_ELO) / 400))

                    #k-factor scaling
                    #1. initally set up k-factor based on my current ELO confidence
                    self.k_factor = K_FACTOR_MAP.get("h")[my_current_ELO_confidence]
                    #2. if we have some level of confidence we want we care if there is confidence in oppoents ELO
                    if my_current_ELO_confidence > 2:
                        self.k_factor = K_FACTOR_MAP.get("l")[opponents_ELO_confidence]
                    #3. if the elo confidence is similar we should do scaling based on difference
                    if my_current_ELO_confidence > 2 and abs(my_current_ELO_confidence - opponents_ELO_confidence) == 1:
                        ELO_diff = my_current_ELO - opponents_ELO
                        self.__scaleKFactor(result, ELO_diff)

                    ELO_change_amount = self.k_factor*(result - expectation)
                    total_ELO_change = total_ELO_change + int(ELO_change_amount)
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
            self.k_factor = K_FACTOR_DEFAULT


    def __KFactorUP(self, ELO_diff):
        if ELO_diff > 200:
            self.k_factor = K_FACTOR_MAP.get("h")[1]
        elif ELO_diff <= 200 and ELO_diff > 120:
            self.k_factor = K_FACTOR_MAP.get("h")[1]
        elif ELO_diff <= 120 and ELO_diff > 60:
            self.k_factor = K_FACTOR_MAP.get("h")[2]
        elif ELO_diff <= 60 and ELO_diff > 20:
            self.k_factor = K_FACTOR_MAP.get("h")[3]
        elif ELO_diff <= 20 and ELO_diff > 0:
            self.k_factor = K_FACTOR_MAP.get("h")[4]

    def __KFactorDOWN(self, ELO_diff):
        if ELO_diff > 200:
            self.k_factor = K_FACTOR_MAP.get("l")[0]
        elif ELO_diff <= 200 and ELO_diff > 120:
            self.k_factor = K_FACTOR_MAP.get("l")[1]
        elif ELO_diff <= 120 and ELO_diff > 60:
            self.k_factor = K_FACTOR_MAP.get("l")[2]
        elif ELO_diff <= 60 and ELO_diff > 20:
            self.k_factor = K_FACTOR_MAP.get("l")[3]
        elif ELO_diff <= 20 and ELO_diff > 0:
            self.k_factor = K_FACTOR_MAP.get("l")[4]
