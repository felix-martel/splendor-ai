
class Agent:
    def __init__(self):
        self.identity = None
        self.nb_victories = 0
        self.nb_games = 0
        
    def observe(self, state, reward, done, actions):
        # Update the agent
        pass
    
    def act(self):
        # Return an action
        action = None
        return action
    
    def observe_and_act(self, state, reward, done, actions):
        # Get current state
    
        # Return an action
        action = None
        return action
        
    def new_game(self, player):
        self.identity = player
        self.nb_games += 1
        
    