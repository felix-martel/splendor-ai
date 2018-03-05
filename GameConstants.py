from pickle import load
import numpy as np

TOKEN_TYPES = ['green', 'blue', 'red', 'white', 'black', 'yellow']
POSSIBLE_ACTIONS = ['take_3', 'take_2', 'reserve', 'purchase', 'do_nothing']
PLAYER_NAMES = ['Marco', 'Freddy', 'Satanas', 'Franck', 'Steve', 'Julia', 'Ed', 'Banco', 'Yuri', 'Mae', 'Bae', 'Christiana', 'Emma', 'La Folle', 'Oeil-de-cochon', 'Duende', "André", "Giselle"]

# -- RULES CONSTANTS -- #
# Board dimensions
BOARD_X, BOARD_Y = (3, 4)
DECK_SIZE = 3
NB_PLAYERS = 4
INCREMENTAL = False
VERBOSE = 1

MIN_TOKEN_FOR_TAKE_2 = 4
MAX_TOKEN_PER_PLAYER = 10
MAX_RESERVED_CARDS = 3


PRESTIGE_TARGET = 15

JOKER_COLOR = 'yellow'

# -- DATA & CARDS -- #
path_to_cards = 'serialized-cards.pkl'
path_to_tiles = 'serialized-tiles.pkl'

def get_cards():
    with open(path_to_cards, 'rb') as data:
        serialized_cards = load(data)
        return serialized_cards
    
def get_tiles():
    with open(path_to_tiles, 'rb') as data:
        serialized_tiles = load(data)
        return serialized_tiles

def get_tokens():
    tokens = {'green': 7, 'blue': 7, 'red': 7, 'white': 7, 'black': 7, 'yellow': 5}
    return tokens

# -- UTILITY FUNCTIONS -- #
def out(*args, verbose=1):
    display = VERBOSE >= verbose
    if display:
        print(*args)

def get_empty_token_bag():
    d = {}
    for col in TOKEN_TYPES:
        d[col] = 0
    return d
    
def list_to_dict(l):
    colors = ['white', 'black', 'blue', 'green', 'red', 'yellow']
    d = {}
    for i in len(l):
        d[colors[i]] = l[i]
    return(d)
    
def tokens_to_str(tokens):
    return " - ".join([str(n)+" " + color for color, n in tokens.items()])
    
def tokens_to_array(tokens):
    n = len(tokens)
    arr = np.zeros(n)
    for i, color in enumerate(TOKEN_TYPES):
        arr[i] = tokens[color]
    return arr

