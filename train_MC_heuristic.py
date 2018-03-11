from Environment import Environment
from Tile import Tile
from RandomAgent import RandomAgent
from HeuristicAgent import HeuristicAgent
import numpy as np
from time import time
import GameConstants as game
import pickle
import math
from Utils import display_time
import copy


def MonteCarlo_estimate(board, action, n_train=15, max_step=45):
    J = 0
    #agent = RandomAgent()
    
    base_board = copy.deepcopy(board)
    player = base_board.get_player()
    s, r, done, _ = base_board.take_action(action, player)
    
    for episode in range(n_train):
        simulated_board = copy.deepcopy(base_board)
        player = simulated_board.get_player()
        step = 0
        while not done and step < max_step:
            action = simulated_board.get_random_action(player)
            _, r, done, _ = simulated_board.take_action(action, player)
            simulated_board.autoplay()
            step += 1
        final_score = 0
        if done and player.has_won():
            final_score = 10
        elif not done and player.prestige - simulated_board.get_best_adversary_score():
            final_score = 2
        
        J += final_score
        #print("end of episode", episode, "-", step, "simulated")
            
    return J / n_train

t_start = time()
# Constants
epochs = 20
max_step = 50
last_debug = {}
cumulated_reward = 0
# Init game environment
board = Environment()

# Init agent
agent = HeuristicAgent(train=True)
lengths = []
x = []
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
    
    while not game_ended and t < max_step:
        # -- Beginning of our turn --
        # Observe current state
        state = board.get_visible_state(agent.identity)
        actions = board.get_possible_actions(agent.identity)
        
        agent.observe(state, reward, game_ended, actions)
        
        best_action = {}
        best_estimate = -100
        for a_index, action in enumerate(actions):
            score = MonteCarlo_estimate(board, action)
            #print("end of MC estimation", a_index, "with score", score)
            agent.train(state, action, score)
            if score > best_estimate:
                best_action = action
                best_estimate = score
        
        
        #action = agent.act()        
        state, reward, game_ended, _debug = board.take_action(best_action, agent.identity)
        # -- End of our turn --
        
        cumulated_reward += reward
        last_debug = _debug
        t += 1
        # Other players' turn
        board.autoplay()
        #print("end of step", t, "- agent did", best_action)
    if t == max_step and reward <= 0:
        reward = -10
    agent.observe(state, reward, game_ended, actions)
    
    if agent.has_won():
       recent_victories += 1
       total_victories += 1

    if game_ended:
        print("game", i, "ended")
        print("-")
        if i % 10 == 0 and i > 0:
            print("current % victories :", 10*(recent_victories), "%")
            last_games.append(recent_victories)
            recent_victories = 0
        if i % 100 == 0 and i > 0:
            print("game", i, "out of", epochs)
        if i % 1000 == 0 and i > 0:
            print(i, "games played,", (epochs-i), "to go. Elapsed time :", display_time(time() - t_start), "ETA :", display_time((epochs - i) * (time()-t_start) / i))
    
    lengths.append(t)
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
