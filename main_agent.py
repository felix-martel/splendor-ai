from Environment import Environment
from RandomAgent import RandomAgent

# Constants
n_games = 10
max_step = 1000
last_debug = {}

# Init game environment
game = Environment()

# Start new game
player = game.get_player()
initial_state = game.state.visible()
initial_actions = game.get_possible_actions(player)

# Init agent
agent = RandomAgent()
agent.new_game(player)
agent.observe(initial_state, 0, False, initial_actions)

# Start playing !
t = 0
reward = 0
game_ended = False
while not game_ended and t < max_step:
    # -- Beginning of our turn --
    # Observe current state
    state = game.state.visible()
    actions = game.get_possible_actions(agent.identity)    
    agent.observe(state, reward, game_ended, actions)
    # Take action
    action = agent.act()    
    state, reward, game_ended, _debug = game.take_action(action, agent.identity)
    # -- End of our turn --
    
    last_debug = _debug
    t += 1
    # Other players' turn
    game.autoplay()

if game_ended:
    print("\n\n Game ended after", t, "steps")
    
#print("--- GAME RESULTS---")
#print("Ended after", t, "steps")
#print("Cumulative reward", game.get_total_reward(player))
#game.display_results()
