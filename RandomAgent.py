import GameConstants as game
from Agent import Agent
import random

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
        
    def new_game(self, player):
        self.identity = player
        self.nb_games += 1
        
    