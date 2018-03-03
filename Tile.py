import GameConstants as game

class Tile:
    def __init__(self, bonuses, prestige):
        self.bonuses = bonuses
        self.prestige = 3
        self.visiting = None
        
    def can_visit(self, player):
        for color in game.TOKEN_TYPES:
            if color in self.bonuses:
                if color not in player.bonuses or player.bonuses[color] < self.bonuses[color]:
                    return False
        return True