from Environment import Environment
from Tile import Tile
from RandomAgent import RandomAgent
from RefinedQApproxAgent import RefinedQApproxAgent as AgentQ
from AdvancedQAgent import AdvancedQAgent as AdvancedAgent
import numpy as np
from time import time
import GameConstants as game


#
last_debug = {}
# Init game environment
#board = Environment()

def play(board, agent, epochs = 10, _debug=last_debug, max_step=100, verbose=2):
    t_start = time()
    cumulated_reward = 0
    n_victories = 0
    cumulated_length = 0
    
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
        
        while not game_ended and t < max_step:
            # -- Beginning of our turn --
            # Observe current state
            state = board.get_visible_state(agent.identity)
            actions = board.get_possible_actions(agent.identity)
            
            agent.observe(state, reward, game_ended, actions)
            action = agent.act()
            
            state, reward, game_ended, debug = board.take_action(action, agent.identity)
            # -- End of our turn --
            
            if reward > 0:
                n_victories += 1
            cumulated_reward += reward
            _debug = debug
            t += 1
            # Other players' turn
            board.autoplay()
        
        if t >= max_step:
            reward = -10
        agent.observe(state, reward, game_ended, actions)
        
        if game_ended:
            cumulated_length += t
            #print(board.winner(), "won in", t, "steps")
            if i % 100 == 0 and i > 0 and verbose >= 3:
                print("game", i, "out of", epochs)
            if i % 1000 == 0 and i > 0 and verbose >= 2:
                print(i, "games played,", (epochs-i), "to go. Elapsed time :", (time() - t_start), "seconds. ETA :", (epochs - i) * (time()-t_start) / i)
                
    
    t_end = time()
    duration = t_end - t_start
    if verbose >= 1:
        print(epochs, "iterations finished after", duration, "seconds.\n -")
        print("cumulated reward :", cumulated_reward)
        print("avg length :", cumulated_length / (epochs + 0.0001))
        print("n victories :", n_victories)
        print("percent victories :", 100*(n_victories/(epochs + 0.001)))
    
    return n_victories
    
#ai = AdvancedAgent()
#play(Environment(), ai, epochs=100)

def export_Q_state(agent, filename):
    n_state, n_action = agent.Q.shape
    col_width = 12
    col_format = '{:12}' # '{:' + col_width + '}'
    sep = "  |  "
    
    with open(filename, 'w') as f:
        for s in range(n_state):
            res = agent.state_to_string(s)
            lines = res.split("\n")
            cols = ['{:30}'.format(l) for l in lines]
            cols = [[l] for l in cols]
            for a in range(n_action):
                t = agent.convert_action(a, to="name")
                v = agent.Q[s, a]
                to_append = [" " for _ in range(len(cols))]
                to_append[0] = t
                to_append[3] = v
                for i in range(len(cols)):
                    cols[i].append(to_append[i])
            for col in cols:
                col[0] = col[0].rjust(25, " ")
                for i in range(1, len(col)):
                    col[i] = col_format.format(col[i])
                f.write(sep.join(col))
                f.write("\n")
            f.write("\n")
    return
    
#export_Q_state(ai, 'test.txt')