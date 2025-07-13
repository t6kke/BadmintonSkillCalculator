from BSC.PlayersAndTeams.players import Player

class Team():
    def __init__(self, team_name, db_obj, ELO):
        self.team_name = team_name
        self.ELO = ELO
        self.database_obj = db_obj
        self.games_played = 0
        self.victories_count = 0
        self.team_member_set = createTeamMembersSet(self.team_name, self.database_obj)

    def information(self):
        return f'Team: \'{self.team_name}\' --- ELO: {self.ELO} --- played: {self.games_played} game(s) --- won {self.victories_count} game(s)'

    def __str__(self):
        return self.team_name

    def __repr__(self):
        return self.team_name

# function needed also outside Team class so makes sense to have it here as a standalone function
def createTeamMembersSet(team_str, db_obj, verbose=False):
    #TODO in the future individual players will be created as player objects and be part of the set of the team.
    if verbose: print(f"DEBUG --- parsing team string: '{team_str}' for creating player set")
    names = team_str.split("+")
    if verbose: print(f"DEBUG --- player one: '{names[0].rstrip()}' and player two '{names[1].lstrip()}'")
    result_set = set()
    for name in names:
        user = Player(name.strip())
        user.GetOrCreatePlayerDBobj(db_obj)
        result_set.add(user)
    print(result_set, type(result_set))
    #result_set = {names[0].rstrip(), names[1].lstrip()}
    if verbose: print(f"DEBUG --- final set to return: '{result_set}'")
    return result_set



#new Team object, just intended for holding list of player objects in set data structure. Set is specifically used since order is not inportant for comparison between teams.
class Team_v2():
    def __init__(self, player_obj_list):
        self.team_members_set = set()
        self.__fillTeamMebersSet(player_obj_list)

    def __str__(self):
        return f"Team object with '{type(self.team_members_set)}' type and player DB ID values of: '{str(self.team_members_set)}'"

    def __repr__(self):
        return self.team_members_set

    def __fillTeamMebersSet(self, player_obj_list):
        for player_obj in player_obj_list:
            self.team_members_set.add(player_obj.db_id)
