#TODO currently not used, implement in the future where team members are player objects
class Player():
    def __init__(self, player_name, ELO):
        self.player_name = player_name
        self.ELO = ELO

    def information(self):
        return f'Player: \'{self.player_name}\' --- ELO: {self.ELO}'

    def __str__(self):
        return self.player_name

    def __repr__(self):
        return self.player_name
