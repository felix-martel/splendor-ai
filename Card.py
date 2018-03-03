import GameConstants as game

class Card:
    
    def __init__(self, price, prestige, bonus):
        self.price = price
        self.prestige = prestige
        self.bonus = bonus
        self.owner = None
        self.purchased = False
        self.reserved = False
  