import GameConstants as game
from Agent import Agent
import random

minimal_action_set = [{'type': 'do_nothing', 'params': None}]


class RandomAgent(Agent):
    def __init__(self):
        self.identity = None
        self.nb_victories = 0
        self.nb_games = 0
        self.nex_action = {}
        
    def observe(self, state, reward, done, actions):
        # Update the agent
        self.next_action = random.choice(actions)
        game.out("Next action will be", self.next_action)
    
    def act(self):
        # Return an action
        action = self.next_action
        game.out("Deciding to do", action)
        return action
    
    def observe_and_act(self, state, reward, done, actions):
        # Get current state
        self.next_action = random.choice(actions)
        
        # Return an action
        action = self.next_action
        return action
        
    def new_game(self, player, state={}, actions=minimal_action_set):
        self.identity = player
        self.nb_games += 1
        self.next_action = random.choice(actions)
        
    