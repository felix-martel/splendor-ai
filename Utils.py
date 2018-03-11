import GameConstants as game
from itertools import combinations
import math

def positive_part(x):
    return x if x > 0 else 0
    

def get_subsets(li, size=3):
    return set(combinations(li, size))
    
def subtract_tokens(tokens_a, tokens_b):
    '''
    Compute tokens_a - token_b ie for all color in colors, tokens_a[color] - tokens_b[color]
    '''
    result = game.get_empty_token_bag()
    for color in result:
        result[color] = tokens_a[color] - tokens_b[color]
    return result

def display_time(t):
    if t < 60:
        t = math.floor(t*100) / 100
        return str(t) + "s"
    elif t < 3600:
        m = int(math.floor(t)) // 60
        s = math.floor(t - 60 * m)
        return str(m) + "mn, " + str(s) + "s"
    else:
        h = int(math.floor(t)) // 3600
        m = t - h * 3600
        return str(h) + "h, " + display_time(m)