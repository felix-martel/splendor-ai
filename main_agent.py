from Environment import Environment
from Tile import Tile
from RandomAgent import RandomAgent
from QApproxAgent import QApproxAgent as AgentQ
from BasicMonteCarloAgent import BasicMonteCarloAgent as AgentMC

# Constants
n_games = 10
max_step = 1000
last_debug = {}

# Init game environment
board = Environment()

# Start new game
player = board.get_player()
initial_state = board.state.visible(player)
initial_actions = board.get_possible_actions(player)

# Init agent
agent = AgentMC()
agent.new_game(player)
agent.observe(initial_state, 0, False, initial_actions)

# Start playing !
t = 0
reward = 0
while not board.game_ended() and t < max_step:
    # -- Beginning of our turn --
    # Observe current state
    state = board.state.visible()
    actions = board.get_possible_actions(agent.identity)

    print(board.GAME_ENDED,board.game_ended())    
    agent.observe(state, reward, False, actions)
    # Take action
    action = agent.act()    
    state, reward, game_ended, _debug = board.take_action(action, agent.identity)
    # -- End of our turn --
    
    last_debug = _debug
    t += 1
    # Other players' turn
    board.autoplay()

if board.game_ended():
    print("\n\n Game ended after", t, "steps")
    
#print("--- GAME RESULTS---")
#print("Ended after", t, "steps")
#print("Cumulative reward", game.get_total_reward(player))
#game.display_results()
 
    
    

