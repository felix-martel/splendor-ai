TOKEN_TYPES = ['green', 'blue', 'red', 'white', 'black', 'yellow']
POSSIBLE_ACTIONS = ['take_3', 'take_2', 'reserve', 'purchase']

# -- RULES CONSTANTS -- #
# Board dimensions
BOARD_X, BOARD_Y = (3, 4)

MIN_TOKEN_FOR_TAKE_2 = 4
MAX_TOKEN_PER_PLAYER = 10
MAX_RESERVED_CARDS = 3

DECK_SIZE = 3

NB_PLAYERS = 4

JOKER_COLOR = 'yellow'

# -- UTILITY FUNCTIONS -- #
VERBOSE = True
def out(*args):
    if VERBOSE:
        print(*args)
    