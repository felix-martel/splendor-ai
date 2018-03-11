import GameConstants as game

class Card:
    
    def __init__(self, level=None, price=None, prestige=None, bonus=None, empty=False):
        if price != None:
            self.price = price.copy()
        else:
            self.price = price
        self.prestige = prestige
        self.bonus = bonus
        self.level = level
        self.empty = empty
        # Useless
    
    def __str__(self):
        if(self.empty):
            return "[empty card]"
        a = [self.bonus]
        b = [self.prestige]
        c = ["".join([str(v) for k, v in self.price.items()])]
        return str(a) + str(b) + str(c)
    
    def __eq__(self,other):
        return ((self.price == other.price) and (self.prestige == other.prestige) and (self.bonus == other.bonus) and (self.level == other.level) or (self.empty == True)) and (self.empty == other.empty)

    def is_empty(self):
        return self.empty
        
    def grant_prestige(self, player, nobles):
        if self.is_empty():
            return False
        
        if self.prestige > 0:
            return True
        else:
            return sum([self.unlock_noble(player, noble) for noble in nobles]) > 0
        
    def unlock_noble(self, player, noble):
        if self.is_empty():
            return False
        
        unlock = True
        for color in game.TOKEN_TYPES:
            current = player.bonuses[color]
            if self.bonus == color:
                current += 1
            expected = noble.bonuses[color]
            if expected > current:
                unlock = False
                break
        return unlock

def list_to_dict(l):
    colors = ['white', 'black', 'blue', 'green', 'red']
    d = {}
    for i in range(len(l)):
        d[colors[i]] = l[i]
    d['yellow'] = 0
    return(d)
        
def prod_to_bonus(n):
    colors = ['white', 'black', 'blue', 'green', 'red', 'yellow']
    return colors[n]
    
def mine_to_card(mine):
    price = list_to_dict(mine.gems)
    prestige = mine.victoryPoints
    bonus = prod_to_bonus(mine.produces)
    level = mine.tier - 1
    return level, price, prestige, bonus
    
def get_color(i):
    colors = ['white', 'black', 'blue', 'green', 'red', 'yellow']
    return(colors[i])
    
def noble_to_tile(noble):
    bonuses = list_to_dict(noble.gems)
    prestige = noble.victoryPoints    
    
    return bonuses, prestige
    
def convert_bonus(card):
    bonus = ""
    for k, v in card.bonus.items():
        if v > 0:
            bonus = k
            break
    card.bonus = bonus
    
def split_cards(cards):
    l1, l2, l3 = [], [], []
    for c in cards:
        if c.level == 1:
            l1.append(c)
        elif c.level == 2:
            l2.append(c)
        elif c.level == 3:
            l3.append(c)
    return l1, l2, l3
