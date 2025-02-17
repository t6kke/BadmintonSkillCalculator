from skillcalc import SkillCalc

class TeamHandler:
    def __init__(self, all_teams_list, verbose = False):
        self.verbose = verbose #TODO extend verbose information to stuff that might be relevant
        self.teams_list = all_teams_list

    #TODO analyze should I make teams here or in the main function and pass them into here
    #TODO cannot handle teams name swaps over tournaments only here, games data needs to be changed to not be name but actual team object.
    def addTeam(self, team_name, ELO = 1000):
        temp_existing_teams = []
        for item in self.teams_list:
            temp_existing_teams.append(repr(item)) #TODO find a better way to handle if team is enterd or not
        if team_name not in temp_existing_teams:
            new_team = Team(team_name, ELO)
            self.teams_list.append(new_team)

    def calculateScore(self, team1, team2, winner):
        team_one = None
        team_two = None
        for team in self.teams_list:
            if repr(team) == team1:
                team_one = team
            elif repr(team) == team2:
                team_two = team
        if team_one == None or team_two == None:
            raise Exception("Team(s) missing excpetion")
        if winner == 1:
            team_one.victories_count += 1
        elif winner == 2:
            team_two.victories_count += 1
        skillCalculator = SkillCalc(self.verbose) # somewhat basic self built ELO calculator, maybe will replace it with some external library
        skillCalculator.addTeams(team_one, team_two)
        skillCalculator.calculate(winner)
        self.__incrementGameCount(team_one, team_two)

    def reportTeamData(self):
        print("List of teams:", self.teams_list, "\n")
        for team in self.teams_list:
            print(team.information())

    def __incrementGameCount(self, team_one, team_two):
        team_one.games_played += 1
        team_two.games_played += 1


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
