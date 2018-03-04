import GameConstants as game
from itertools import combinations

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
