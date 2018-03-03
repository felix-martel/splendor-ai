import GameConstants as game

class Tile:
    def __init__(self, bonuses, prestige):
        self.bonuses = bonuses
        self.prestige = 3
        
    def __str__(self):
        a = ["n"]
        b = [self.prestige]
        c = ["".join([str(v) for k, v in self.bonuses.items()])]
        return str(a) + str(b) + str(c)
        
    def can_visit(self, player):
        for color in game.TOKEN_TYPES:
            if color in self.bonuses:
                if color not in player.bonuses or player.bonuses[color] < self.bonuses[color]:
                    return False
        return True