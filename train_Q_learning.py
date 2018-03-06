from Environment import Environment
from Tile import Tile
from RandomAgent import RandomAgent
from RefinedQApproxAgent import RefinedQApproxAgent as AgentQ
from AdvancedQAgent import AdvancedQAgent as AdvancedAgent
import numpy as np
from time import time
import GameConstants as game
import pickle
import math

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

t_start = time()
# Constants
epochs = 5000
max_step = 50
last_debug = {}
cumulated_reward = 0
# Init game environment
board = Environment(adversarial=True)

# Init agent
agent = AdvancedAgent()
lengths = []
x = []
updates = []
plot = False
last_games = []
total_victories = 0
recent_victories = 0

if plot:
    import matplotlib.pyplot as plt
    
    plt.axis([0, epochs, 0, max_step+10])
    plt.ion()

for i in range(epochs):
    board.reset()
    
    # Start new game
    player = board.get_player()
    initial_state = board.state.visible()
    initial_actions = board.get_possible_actions(player)
    
    agent.new_game(player, initial_state, initial_actions)
    
    # Start playing !
    t = 0
    reward = 0
    game_ended = False
    assertion_errors = 0
    update = 0
    
    while not game_ended and t < max_step:
        # -- Beginning of our turn --
        # Observe current state
        state = board.get_visible_state(agent.identity)
        actions = board.get_possible_actions(agent.identity)
        
        agent.observe(state, reward, game_ended, actions)
        action = agent.act()
        
        state, reward, game_ended, _debug = board.take_action(action, agent.identity)
        # -- End of our turn --
        
        update += abs(agent.get_last_update())
        cumulated_reward += reward
        last_debug = _debug
        t += 1
        # Other players' turn
        board.autoplay()
    if t == max_step and reward <= 0:
        reward = -10
    agent.observe(state, reward, game_ended, actions)
    
    if agent.has_won():
       recent_victories += 1
       total_victories += 1

    if game_ended:
        if i % 10 == 0 and i > 0:
            last_games.append(recent_victories)
            recent_victories = 0
        if i % 100 == 0 and i > 0:
            print("game", i, "out of", epochs)
        if i % 1000 == 0 and i > 0:
            print(i, "games played,", (epochs-i), "to go. Elapsed time :", display_time(time() - t_start), "ETA :", display_time((epochs - i) * (time()-t_start) / i))
    
    lengths.append(t)
    updates.append(update)
    x.append(i)
    if plot:
        plt.scatter(x, lengths)
        plt.scatter(x, updates, color='r')
        plt.pause(0.001)

t_end = time()
duration = t_end - t_start
print(epochs, "iterations finished after", display_time(duration), "\n -")
print("cumulated reward :", cumulated_reward)
print("victories :", total_victories, "/", epochs)

def save_training(Q, filename):
    with open(filename, 'wb') as f:
        pickle.dump(Q, f)

def pause_training(filename):
    data = (agent, board, reward, t, game_ended, epochs)
    with open(filename, 'wb') as f:
        pickle.dump(data, f)
        

        

#save_training(agent.Q, 'q_30k.pkl')