class SkillCalc:
    def __init__(self, verbose = False):
        self.verbose = verbose #TODO extend verbose information to stuff that might be relevant
        self.k_factor = 32 #TODO there should be 2 K-Factor variables, one for winner and one loser. when we have implemented ELO confidence value. example high ELO user will not lose a lot of points if new team with base/low ELO beats them
        self.team_one = None
        self.expected_for_one = 0
        self.result_for_one = 0
        self.team_two = None
        self.expected_for_two = 0
        self.result_for_two = 0
        self.winner = None

    def addTeams(self, team_one, team_two):
        self.team_one = team_one
        self.team_two = team_two

    def calculate(self, winner):
        self.__calculateExpectedScores()
        self.__determinResult(winner)
        self.__scaleKFactor()
        self.__calculateAndAssignNewRating()


    def __calculateExpectedScores(self):
        self.expected_for_one = 1/(1+10**((self.team_one.ELO - self.team_one.ELO) / 400))
        self.expected_for_two = 1/(1+10**((self.team_one.ELO - self.team_one.ELO) / 400))

    def __determinResult(self, winner):
        if winner == 1:
            self.result_for_one = 1
            self.result_for_two = 0
            self.winner = self.team_one
        elif winner == 2:
            self.result_for_one = 0
            self.result_for_two = 1
            self.winner = self.team_two

    def __scaleKFactor(self):
        ELO_diff = self.team_one.ELO - self.team_two.ELO
        if self.verbose:
            print("ELO difference:", ELO_diff)
        #TODO investigate can this if else logic be simplified
        if self.winner == self.team_one and ELO_diff > 0:
            # winner has higher ELO so k_factor has to scale down based on difference
            self.__KFactorDOWN(abs(ELO_diff))
        elif self.winner == self.team_one and ELO_diff < 0:
            # winner has lower ELO so k_factor has to scale up based on the difference
            self.__KFactorUP(abs(ELO_diff))
        elif self.winner == self.team_two and ELO_diff > 0:
            # winner has lower ELO so k_factor has to scale up based on the difference
            self.__KFactorUP(abs(ELO_diff))
        elif self.winner == self.team_two and ELO_diff < 0:
            # winner has higher ELO so k_factor has to scale down based on difference
            self.__KFactorDOWN(abs(ELO_diff))
        else:
            self.k_factor = 32
            return

    #TODO this K-Factor up and down scaling valuse logic should be external, maybe even configuration item.
    # if it is external configuration calculation and data should be connected to a set of configurations
    # for situations where this logic is changed and data already exists
    # then there should be decision to continue with new setup or to do recalculatiosn on old values as well.
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

    def __calculateAndAssignNewRating(self):
        if self.verbose: print(f"Using K-Factor value: '{self.k_factor}'")
        new_ELO_one = int(self.team_one.ELO + self.k_factor*(self.result_for_one - self.expected_for_one))
        new_ELO_two = int(self.team_two.ELO + self.k_factor*(self.result_for_two - self.expected_for_two))
        self.__assignNewRating(new_ELO_one, new_ELO_two)

    def __assignNewRating(self, new_ELO_one, new_ELO_two):
        if self.verbose:
            team_one = self.team_one
            team_two = self.team_two
            print(f"{team_one} played against {team_two} and winner was {repr(self.winner)}")
            print(f"{team_one} ELO was: {self.team_one.ELO}")
            print(f"{team_one} ELO new: {new_ELO_one}")
            print("Change:", new_ELO_one - self.team_one.ELO)
            print(f"{team_two} ELO was: {self.team_two.ELO}")
            print(f"{team_two} ELO new: {new_ELO_two}")
            print("Change:", new_ELO_two - self.team_two.ELO)
        self.team_one.ELO = new_ELO_one
        self.team_two.ELO = new_ELO_two


class SkillCalc_v2():
    def __init__(self, players_obj_dict, verbose = False):
        self.verbose = verbose #TODO extend verbose information to stuff that might be relevant
        self.k_factor = 32 #TODO there should be 2 K-Factor variables, one for winner and one loser. when we have implemented ELO confidence value. example high ELO user will not lose a lot of points if new team with base/low ELO beats them
        self.players_obj_dict = players_obj_dict

    def calculate(self, match):
        #TODO list
        # 1. calculated expected score for players in each player.
        # 2. need to assing winner/loser variables for final elo calculations
        # 3. for each player against each oponent player determin the ELO difference and modify k-factor accordingly
        # 4. ELO calculation for each player.
        # 5. return some logical data structure for new ELO values, expected output is the ammount ELO was changed, not the new ELO value

        t_one_p_one_id = list(list(match.keys())[0].team_members_set)[0]
        t_one_p_two_id = list(list(match.keys())[0].team_members_set)[1]
        t_two_p_one_id = list(list(match.keys())[1].team_members_set)[0]
        t_two_p_two_id = list(list(match.keys())[1].team_members_set)[1]

        # setp 1.
        current_ELO_for_t_one_p_one = self.players_obj_dict.get(t_one_p_one_id).ELO
        expectation_for_t_one_p_one = 1/(1+10**((current_ELO_for_t_one_p_one - current_ELO_for_t_one_p_one) / 400))

        current_ELO_for_t_one_p_two = self.players_obj_dict.get(t_one_p_two_id).ELO
        expectation_for_t_one_p_two = 1/(1+10**((current_ELO_for_t_one_p_two - current_ELO_for_t_one_p_two) / 400))

        current_ELO_for_t_two_p_one = self.players_obj_dict.get(t_two_p_one_id).ELO
        expectation_for_t_two_p_one = 1/(1+10**((current_ELO_for_t_two_p_one - current_ELO_for_t_two_p_one) / 400))

        current_ELO_for_t_two_p_two = self.players_obj_dict.get(t_two_p_two_id).ELO
        expectation_for_t_two_p_two = 1/(1+10**((current_ELO_for_t_two_p_two - current_ELO_for_t_two_p_two) / 400))

        # step 2.
        result_for_team_one = None
        result_for_team_two = None
        if list(match.values())[0] > list(match.values())[1]:
            result_for_team_one = 1
            result_for_team_two = 0
        else:
            result_for_team_one = 0
            result_for_team_two = 1

        # step 3.
        #TODO

        # step 4.
        #TODO

        # step 5.
        #TODO

    #TODO analyze if k-factor scaling values should be external configuration.
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
