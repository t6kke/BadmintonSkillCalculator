from BSC.PlayersAndTeams.players import Player

class Team():
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
