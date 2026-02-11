#TODO analyze if k-factor values should be external, configuration file or maybe even some database entry.
K_FACTOR_DEFAULT = 48
K_FACTOR_MAP = {"l": [1, 12, 24, 36, 48],
                "h": [96, 84, 72, 60, 48]}


class SkillCalc():
    def __init__(self, output, verbose=False):
        self.verbose = verbose
        self.output = output
        self.k_factor = None

    def calculate(self, winning_team_obj, losing_team_obj):

        def scaleKFactor_ELOdiff(result, my_current_ELO, opponents_ELO):
            ELO_diff = my_current_ELO - opponents_ELO
            self.__scaleKFactor(result, ELO_diff)

        def scaleKFactor_ELOconfAndELOdiff(my_current_ELO_confidence, opponents_ELO_confidence, result, my_current_ELO, opponents_ELO):
            # 1. initial value based on my confidence
            # 2. if there is at least some confidence we want to care about opponets confidence and change
            # 3. if both confidences are high and close we should do standard scale

            # 1.
            self.k_factor = K_FACTOR_MAP.get("h")[my_current_ELO_confidence]
            self.output.write(self.verbose, "INFO", "SkillCalc:calculate", message=f"Initial K-Factor: '{self.k_factor}' based on my ELO confidence: '{my_current_ELO_confidence}'", player_id = player_id)
            # 2.
            if my_current_ELO_confidence > 2:
                self.k_factor = K_FACTOR_MAP.get("l")[opponents_ELO_confidence]
                self.output.write(self.verbose, "INFO", "SkillCalc:calculate", message=f"NEW K-Factor: '{self.k_factor}' based on opponents ELO confidence: '{opponents_ELO_confidence}'")
            # 3.
            conf_diff = abs(my_current_ELO_confidence - opponents_ELO_confidence)
            if my_current_ELO_confidence > 2 and conf_diff <= 1:
                ELO_diff = my_current_ELO - opponents_ELO
                self.__scaleKFactor(result, ELO_diff)
                self.output.write(self.verbose, "INFO", "SkillCalc:calculate", message=f"NEW K-Factor: '{self.k_factor}' since confidence values were close: '{my_current_ELO_confidence}', '{opponents_ELO_confidence}'")


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
                    expectation = 1/(1+10**((opponents_ELO - my_current_ELO) / 400))

                    # original: default k-factor scaling based on just ELO difference
                    #scaleKFactor_ELOdiff(result, my_current_ELO, opponents_ELO)

                    # new: confidence and difference based k-factor scaling
                    scaleKFactor_ELOconfAndELOdiff(my_current_ELO_confidence, opponents_ELO_confidence, result, my_current_ELO, opponents_ELO)

                    self.output.write(self.verbose, "INFO", "SkillCalc:calculate", message=f"Final K-Factor value used for ELO update: '{self.k_factor}'")
                    ELO_change_amount = self.k_factor*(result - expectation)
                    total_ELO_change = total_ELO_change + int(ELO_change_amount)
                total_ELO_change = int(total_ELO_change / len(opponent_team.team_members_set))
                self.output.write(self.verbose, "INFO", "SkillCalc:calculate", message=f"Starting ELO: '{my_current_ELO}' and final ammount of ELO change: '{total_ELO_change}'")
                resut_ELO_changes_dict[player_id] = total_ELO_change
        return resut_ELO_changes_dict

    def __scaleKFactor(self, win_status, ELO_diff):
        self.output.write(self.verbose, "INFO", "SkillCalc:__scaleKFactor", message=f"ELO difference: '{ELO_diff}'")
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
