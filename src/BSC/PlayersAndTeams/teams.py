#TODO team members should be separate player objects
class Team():
    def __init__(self, team_name, ELO):
        self.team_name = team_name
        self.ELO = ELO
        self.games_played = 0
        self.victories_count = 0
        self.team_member_set = set()
        self.__createMeberSet()

    def information(self):
        return f'Team: \'{self.team_name}\' --- ELO: {self.ELO} --- played: {self.games_played} game(s) --- won {self.victories_count} game(s)'

    def __createMeberSet(self):
        #normalize
        names = self.team_name.replace(" ", "").split("+")
        self.team_member_set.add(names[0])
        self.team_member_set.add(names[1])

    def __str__(self):
        return self.team_name

    def __repr__(self):
        return self.team_name
