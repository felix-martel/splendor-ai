from Environment import Environment
from Tile import Tile
from RandomAgent import RandomAgent
from RefinedQApproxAgent import RefinedQApproxAgent as AgentQ
import numpy as np
from time import time
import GameConstants as game

t_start = time()
# Constants
n_games = 10
max_step = 1000
last_debug = {}

# Init game environment
board = Environment()

# Init agent
agent = AgentQ()
# Init empirical R matrix
train_occurences = np.zeros_like(agent.R)
train_rewards = np.zeros_like(agent.R)

n_victories = 0
min_length = 1000
max_length = 0
cumulated_length = 0

for i in range(n_games):
    board.reset()
    
    # Start new game
    player = board.get_player()
    initial_state = board.state.visible()
    initial_actions = board.get_possible_actions(player)
    
    agent.new_game(player, initial_state, initial_actions)
    
    test_state(agent, initial_state, initial_actions)
    
    # Start playing !
    t = 0
    reward = 0
    game_ended = False
    assertion_errors = 0
    while not game_ended and t < max_step:
        # -- Beginning of our turn --
        # Observe current state
        state = board.state.visible()
        actions = board.get_possible_actions(agent.identity)    
        agent.observe(state, reward, game_ended, actions)
        action = agent.act()
        
        # Classify state, action
        s, a = agent.get_Q_coordinates()
        
        assertion_errors += test_state(agent, state, actions)
        
        state, reward, game_ended, _debug = board.take_action(action, agent.identity)
        # -- End of our turn --
        
        # Update matrices
        train_occurences[s, a] += 1
        if reward > 0:
            train_rewards[s, a] += 1
            n_victories += 1
        
        last_debug = _debug
        t += 1
        # Other players' turn
        board.autoplay()
    
    if game_ended:
        #print("\n\n Game ended after", t, "steps")
        min_length = min(min_length, t)
        max_length = max(max_length, t)
        cumulated_length += t
        if i % 10 == 0 and i > 0:
            print("game", i, "out of", n_games)
        if i % 1000 == 0 and i > 0:
            print(i, "games played,", (n_games-i), "to go. Elapsed time :", (time() - t_start), "seconds. ETA :" (n_games - i) * (time()-t_start) / i)
    
#print("--- GAME RESULTS---")
#print("Ended after", t, "steps")
#print("Cumulative reward", game.get_total_reward(player))
#game.display_results()

t_end = time()
duration = t_end - t_start
print(n_games, "iterations finished after", duration, "seconds.\n -")
if n_games > 0:
    print("# of assertion errors :", assertion_errors)
    print("Avg length of a game :", cumulated_length / n_games)
    print("Shortest game :", min_length)
    print("Longest game :", max_length)
    print("Nb of victories :", n_victories)

def get_argmax(a):
    return np.unravel_index(np.argmax(a), a.shape)
    
def compute_empirical_R(n_iter, train_occurences, train_rewards, threshold=0.01):
    assert train_occurences.shape == train_rewards.shape, "array shapes don't match"
    R = np.zeros_like(train_occurences)
    M, N = train_occurences.shape
    max_reward = np.max(train_rewards)
    
    for i in range(M):
        for j in range(N):
            if train_occurences[i, j] / n_iter <= threshold:
                R[i, j] = -1
            R[i, j] += 100 * ( (train_rewards[i, j] / max_reward)**2)
    
    print("min value :", np.min(R))
    print("max value :", np.max(R))
    return R
    
def print_nonzeros(mat, n_iter=n_games):
    M, N = mat.shape
    for i in range(M):
        for j in range(N):
            if mat[i, j] > 0:
                print("coords :", (i, j))
                print("value  :", mat[i,j])
                print("freq   :", mat[i, j]/n_iter)
                print(agent.get_transition_name(i, j))
    print("total :", np.count_nonzero(mat), "non-zero cells")
    return
    
def actions_summary(actions):
    summary = {act: 0 for act in game.POSSIBLE_ACTIONS}
    for action in actions:
        t = action['type']
        summary[t] += 1
    return summary
    
    def test_state(agent, state, actions, disp=False):
        errors = 0
        exp = agent.classify_state(state, to='dic')
        obs = actions_summary(actions)
        tests = {
            'reserve': 'can_reserve',
            'take_3': 'can_take_3',
            'take_2': 'can_take_2',
            'purchase': ['can_buy_prestige', 'can_buy_card']
        }
        for observed, expected in tests.items():
            if_condition = obs[observed] > 0
            if isinstance(expected, list):
                then_condition = sum([exp[cond] for cond in expected]) > 0
            else:
                then_condition = exp[expected]
            if not imply(if_condition, then_condition):
                if disp:
                    print("/!\ ASSERTION ERROR")
                    print("Problem with", observed)
                    print("state :", exp)
                    print("possible action :", obs)
                    print("\n")
                errors += 1
        return errors
            
    
def imply(p, q):
    return p or not q
    
def get_most_frequent_transition(train, agent):
    s, a = get_argmax(train)
    s = int(s)
    a = int(a)
    print(agent.get_transition_name(s, a))
    return agent.convert_state(s, to='dic'), agent.convert_action(a, to='name')
 
    
    

