from Environment import Environment
from Tile import Tile
from RefinedQApproxAgent import RefinedQApproxAgent as AgentQ
from Card import Card
import GameConstants as game

# Init game environment
board = Environment()

# Start new game
player = board.get_player()
initial_state = board.state.visible()
initial_actions = board.get_possible_actions(player)

agent = AgentQ()
agent.identity = player
agent.state = initial_state

# -- CHECKS -- #
# buy_card
c0 = initial_state['cards'][0][0]
agent.identity.tokens = c0.price
action = {'type': 'purchase', 'params': ['from_table', (0, 0)]}
print("-- Check <buy_card> --")
print("Must be True :", agent.identity.can_buy(c0))
print("Action classified as <<", agent.action_space[agent.classify_action(action)], ">>")
print("Should be the same value", agent.classify_action(action), agent.action_space_inverted_index['buy_card'])
print("\n")

# buy_card_for_prestige
c1 = initial_state['cards'][0][1]
c1.prestige = 2
agent.identity.token = c1.price
action['params'][1] = (0,1)
print("-- Check <buy_card_for_prestige> --")
print("Must be true :", agent.identity.can_buy(c1))
print("Action classified as <<", agent.action_space[agent.classify_action(action)], ">>")
print("Should be the same value", agent.classify_action(action), agent.action_space_inverted_index['buy_prestige'])
print("\n")

# buy_card_for_noble
exp = {'green': 3, 'black': 3, 'white': 0, 'blue': 3, 'yellow': 0, 'red': 0}
has = {'green': 2, 'black': 3, 'white': 0, 'blue': 3, 'yellow': 0, 'red': 0}
c2 = initial_state['cards'][0][2]
c2.bonus = 'green'
c2.prestige = 0
noble = Tile(exp, 3)
initial_state['tiles'][0] = noble
agent.identity.bonuses = has
agent.identity.tokens = c2.price
action = {'type': 'purchase', 'params': ['from_table', (0, 2)]}
print("-- Check <buy_card_for_noble> --")
print("Must be true :", noble.can_visit(agent.identity))
print("Must be true :", agent.identity.can_buy(c2))
print("Action classified as <<", agent.action_space[agent.classify_action(action)], ">>")
print("Should be the same value", agent.classify_action(action), agent.action_space_inverted_index['buy_prestige'])
print("\n")

# take_3
initial_state['tokens'] = {'green': 7, 'black': 7, 'white': 7, 'blue': 7, 'yellow': 5, 'red': 7}
agent.identity.tokens = {'green': 0, 'black': 0, 'white': 0, 'blue': 0, 'yellow': 0, 'red': 0}
action = {'type': 'take_3', 'params': ['green', 'black', 'blue']}
print("-- Check <take_3> --")
print("Action classified as <<", agent.action_space[agent.classify_action(action)], ">>")
print("Should be the same value", agent.classify_action(action), agent.action_space_inverted_index['take_3'])
print("\n")

# take_2
initial_state['tokens'] = {'green': 7, 'black': 7, 'white': 7, 'blue': 7, 'yellow': 5, 'red': 7}
agent.identity.tokens = {'green': 0, 'black': 0, 'white': 0, 'blue': 0, 'yellow': 0, 'red': 0}
action = {'type': 'take_2', 'params': 'red'}
print("-- Check <take_2> --")
print("Action classified as <<", agent.action_space[agent.classify_action(action)], ">>")
print("Should be the same value", agent.classify_action(action), agent.action_space_inverted_index['take_2'])
print("\n")

# do_nothing
action = {'type': 'do_nothing', 'params': None}
print("-- Check <do_nothing> --")
print("Action classified as <<", agent.action_space[agent.classify_action(action)], ">>")
print("Should be the same value", agent.classify_action(action), agent.action_space_inverted_index['do_nothing'])
print("\n")

# reserve
action = {'type': 'reserve', 'params': ['from_table', (0, 0)]}
agent.identity.hand = []
print("-- Check <reserve> --")
print("Action classified as <<", agent.action_space[agent.classify_action(action)], ">>")
print("Should be the same value", agent.classify_action(action), agent.action_space_inverted_index['reserve'])
print("\n")

#
#
# -- CHECK STATE --
#
#
empty = {'green': 0, 'black': 0, 'white': 0, 'blue': 0, 'yellow': 0, 'red': 0}
low = {'green': 0, 'black': 0, 'white': 0, 'blue': 0, 'yellow': 0, 'red': 0}
med = {'green': 2, 'black': 2, 'white': 0, 'blue': 0, 'yellow': 0, 'red': 0}
high = {'green': 7, 'black': 7, 'white': 7, 'blue': 7, 'yellow': 5, 'red': 7}
full = high.copy()

agent.identity.bonuses = empty.copy()
# -- can_buy and can_buy prestige --
initial_state['cards'] = [
    [Card(level=0, price=med, prestige=0, bonus='red') for _ in range(game.BOARD_Y)],
    [Card(level=1, price=med, prestige=0, bonus='red') for _ in range(game.BOARD_Y)],
    [Card(level=2, price=med, prestige=0, bonus='red') for _ in range(game.BOARD_Y)],
]

print("-- Check <can_buy_card = FALSE> --")
agent.identity.tokens = low.copy()
agent.state = initial_state
s = agent.classify_state(initial_state, to='dic')
print("Should be same values", s['can_buy_card'], False)
print("\n")

print("-- Check <can_buy_card = TRUE> --")
agent.identity.tokens = high.copy()
s = agent.classify_state(initial_state, to='dic')
print("Should be same values", s['can_buy_card'], True)
print("\n")

initial_state['cards'] = [
    [Card(level=0, price=med, prestige=3, bonus='red') for _ in range(game.BOARD_Y)],
    [Card(level=1, price=med, prestige=3, bonus='red') for _ in range(game.BOARD_Y)],
    [Card(level=2, price=med, prestige=3, bonus='red') for _ in range(game.BOARD_Y)],
]

print("-- Check <can_buy_prestige = TRUE> --")
agent.identity.tokens = high.copy()
agent.state = initial_state
s = agent.classify_state(initial_state, to='dic')
print("Should be same values", s['can_buy_prestige'], True)
print("\n")

print("-- Check <can_buy_prestige = FALSE> --")
agent.identity.tokens = low.copy()
s = agent.classify_state(initial_state, to='dic')
print("Should be same values", s['can_buy_prestige'], False)
print("\n")

print("-- Check <can_reserve = TRUE> --")
agent.identity.hand = []
s = agent.classify_state(initial_state, to='dic')
print("Should be same values", s['can_reserve'], True)
print("\n")

print("-- Check <can_reserve = FALSE> --")
agent.identity.hand = [Card(0, high, 0, 'red') for _ in range(3)]
s = agent.classify_state(initial_state, to='dic')
print("Should be same values", s['can_reserve'], False)
print("\n")

print("-- Check <can_take_2 = TRUE> --")
agent.identity.tokens = empty.copy()
initial_state['tokens'] = full.copy()
s = agent.classify_state(initial_state, to='dic')
print("Should be same values", s['can_take_2'], True)
print("\n")

print("-- Check <can_take_2 = FALSE> --")
initial_state['tokens'] = empty.copy()
s = agent.classify_state(initial_state, to='dic')
print("Should be same values", s['can_take_2'], False)
print("\n")

print("-- Check <can_take_3 = TRUE> --")
agent.identity.tokens = empty.copy()
initial_state['tokens'] = full.copy()
s = agent.classify_state(initial_state, to='dic')
print("Should be same values", s['can_take_3'], True)
print("\n")

print("-- Check <can_take_2 = FALSE> --")
initial_state['tokens'] = empty.copy()
s = agent.classify_state(initial_state, to='dic')
print("Should be same values", s['can_take_3'], False)
print("\n")

print("-- Check <high_prestige = TRUE> --")
agent.identity.prestige = 12
s = agent.classify_state(initial_state, to='dic')
print("Should be same values", s['high_prestige'], True)
print("\n")

print("-- Check <high_prestige = FALSE> --")
agent.identity.prestige = 6
s = agent.classify_state(initial_state, to='dic')
print("Should be same values", s['high_prestige'], False)
print("\n")