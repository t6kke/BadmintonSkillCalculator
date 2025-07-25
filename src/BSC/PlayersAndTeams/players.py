import time

class Player():
    def __init__(self, db_id, player_name, ELO):
        self.db_id = db_id
        self.player_name = player_name
        self.ELO = ELO

    def information(self):
        return f'Player: \'{self.player_name}\' --- ELO: {self.ELO} --- db_id: {self.db_id}'

    def __str__(self):
        return self.player_name

    def __repr__(self):
        return self.db_id
