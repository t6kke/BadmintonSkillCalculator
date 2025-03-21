#TODO team members should be separate player objects
class Team():
    def __init__(self, team_name, ELO):
        self.team_name = team_name
        self.ELO = ELO
        self.games_played = 0
        self.victories_count = 0
        self.team_member_set = createTeamMembersSet(self.team_name)

    def information(self):
        return f'Team: \'{self.team_name}\' --- ELO: {self.ELO} --- played: {self.games_played} game(s) --- won {self.victories_count} game(s)'

    def __str__(self):
        return self.team_name

    def __repr__(self):
        return self.team_name

# function needed also outside Team class so makes sense to have it here as a standalone function
def createTeamMembersSet(team_str, verbose=False):
    #TODO in the future individual players will be created as player objects and be part of the set of the team.
    if verbose: print(f"DEBUG --- parsing team string: '{team_str}' for creating player set")
    names = team_str.split("+")
    if verbose: print(f"DEBUG --- player one: '{names[0].rstrip()}' and player two '{names[1].lstrip()}'")
    result_set = {names[0].rstrip(), names[1].lstrip()}
    if verbose: print(f"DEBUG --- final set to return: '{result_set}'")
    return result_set
