from Environment import Environment
from Tile import Tile
from RandomAgent import RandomAgent
from QApproxAgent import QApproxAgent as AgentQ


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
print("Should be the same value", agent.classify_action(action), agent.action_space_inverted_index['buy_card_for_prestige'])
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
print("Should be the same value", agent.classify_action(action), agent.action_space_inverted_index['buy_card_for_noble'])
print("\n")