class RawMatch():
    def __init__(self, category, league, team_one, team_one_status, team_one_scores, team_two, team_two_status, team_two_scores):
        self.category = category
        self.league = league
        self.team_one = team_one
        self.team_one_status = team_one_status
        self.team_one_scores = team_one_scores
        self.team_two = team_two
        self.team_two_status = team_two_status
        self.team_two_scores = team_two_scores

    def GetMatchString(self):
        result_dict = {}
        result_dict[self.team_one] = self.team_one_scores
        result_dict[self.team_two] = self.team_two_scores
        return result_dict
