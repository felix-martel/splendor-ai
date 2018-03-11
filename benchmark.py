from Playground import play
import HeuristicAgent
from Utils import display_time
from Environment import Environment
from HeuristicAgent import HeuristicAgent
from RandomAgent import RandomAgent
from AdvancedQAgent import AdvancedQAgent
import numpy as np
from time import time
import GameConstants as game
import pickle
import math
import random

pretrained_set = np.array(pickle.load(open('trained-heuristic-data.pkl', 'rb')))
print("retrieved pre-trained set with dimension", pretrained_set.shape)

agentH = HeuristicAgent(train_set=pretrained_set, clf='mlp')
agentH_ridge = HeuristicAgent(train_set=pretrained_set, clf='ridge')
training_set = pretrained_set.copy()
np.random.shuffle(training_set)
n_samples = 7000
agentH_partial_ridge = HeuristicAgent(train_set=training_set[:n_samples,:], clf='ridge')
agentH_partial = HeuristicAgent(train_set=training_set[:n_samples, :], clf='mlp')
agentQ = AdvancedQAgent()
agentR = RandomAgent()

all_agents = [agentR, agentQ, agentH_ridge, agentH_partial_ridge, agentH, agentH_partial]
agents_name = ['R  ', 'Q  ', 'HR ', 'HRP', 'HM ', 'HMP']
comparison_matrix = np.zeros((len(agents_name), len(agents_name)))
 
def compare(a, b, n_games = 100, max_step=100, display_results=True):
    t_start = time()
    board = Environment()
    players = ['Player A', 'Player B']
    # Results
    victories_a = 0
    victories_b = 0
    diff_a = []
    diff_b = []
    diff = []
    rew_a = 0
    rew_b = 0
    
    for i in range(n_games):
        board.reset()
        
        # Start new game
        player_a = board.get_player(0)
        player_b = board.get_player(1)
        
        initial_state = board.state.visible()
        actions_a = board.get_possible_actions(player_a)
        actions_b = board.get_possible_actions(player_b)
        
        a.new_game(player_a, initial_state, actions_a)
        b.new_game(player_b, initial_state, actions_b)
        
        # Start playing !
        t = 0
        reward_a = 0
        reward_b = 0
        game_ended = False
        
        while not game_ended and t < max_step:
            # -- Beginning of A's turn --
            # Observe current state
            state = board.get_visible_state(a.identity)
            actions = board.get_possible_actions(a.identity)
            
            a.observe(state, reward_a, game_ended, actions)
            action = a.act()
            
            state, reward_a, game_ended, debug = board.take_action(action, a.identity)
            rew_a += reward_a
            # -- End of turn --
            
            # -- Beginning of B's turn --
            # Observe current state
            state = board.get_visible_state(b.identity)
            actions = board.get_possible_actions(b.identity)
            
            b.observe(state, reward_b, game_ended, actions)
            action = b.act()
            
            state, reward_b, game_ended, debug = board.take_action(action, b.identity)
            rew_b += reward_b
            # -- End of turn --
            
            # Other players' turn
            board.autoplay()
            
            t += 1
        
        if game_ended:
            winner_id = board.winner('pos')
            diff.append(a.identity.prestige - b.identity.prestige)
            if winner_id == 0:
                game.out("Player A won in", t, "steps. A scored", a.identity.prestige, "points, B scored", b.identity.prestige, "points.", verbose=1)
                victories_a += 1
                diff_a.append(a.identity.prestige - b.identity.prestige)
            elif winner_id == 1:
                game.out("Player B won in", t, "steps. A scored", a.identity.prestige, "points, B scored", b.identity.prestige, "points.", verbose=1)
                victories_b += 1
                diff_b.append(b.identity.prestige - a.identity.prestige)
            if i % 100 == 0 and i > 0:
                game.out("game", i, "out of", n_games, "score is", victories_a, "-", victories_b, verbose=0)
            if i % 1000 == 0 and i > 0:
                game.out(i, "games played,", (n_games-i), "to go. Elapsed time :", (time() - t_start), "seconds. ETA :", (n_games - i) * (time()-t_start) / i, verbose=0)
                
    
    t_end = time()
    duration = t_end - t_start
    # Results :
    
    wid = 0 if victories_a > victories_b else 1
    wname = players[wid]
    average_diff = sum(diff) / len(diff)
    if display_results:
        print(n_games, "iterations finished after", duration, "seconds.\n -")
        print("Winner :", wname)
        print(" -")
        print("A wins :", victories_a)
        print("B wins :", victories_b)
        print(" -")
        print("% A :", 100*(victories_a/(n_games)))
        print("% B :", 100*(victories_b/(n_games)))
        print("Average score dist between A and B:", average_diff)
        
    
    return victories_a, victories_b, diff_a, diff_b, average_diff
   
n_iter = 500
nb_of_wins = []
avg_score_diff = []
avg_win_score_diff = []
for opponent in [agentR, agentQ, agentH_ridge, agentH_partial_ridge, agentH_partial]:
    v, _, d, e, avd = compare(agentH, opponent, n_games=n_iter)
    nb_of_wins.append(100 * (v / n_iter))
    avg_score_diff.append(avd)
    avg_win_score_diff.append(100* (sum(d) / len(d)))

#
#n_iter = 1000
#for i in range(len(all_agents)):
#    for j in range(len(all_agents)):
#        if i == j:
#            comparison_matrix[i, j] = -1
#        else:
#            agentA = all_agents[i]
#            agentB = all_agents[j]
#            print("\nComparing", agents_name[i], "and", agents_name[j])
#            v_a, v_b, d_a, d_b = compare(agentA, agentB, n_games=n_iter)
#            comparison_matrix[i, j] = 100 * (v_a / n_iter)
#
#r = '   \t' + '  \t'.join(agents_name) + '\n'
#for i in range(len(all_agents)):
#    r += agents_name[i] + '  \t'
#    for j in range(len(all_agents)):
#        if i == j:
#            r += '  -  '
#        else:
#            r += "{0:.2f}".format(comparison_matrix[i, j])
#        r += '\t'
#    r += '\n'
#    
#print(r)
