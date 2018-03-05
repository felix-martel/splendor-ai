import GameConstants as game
from Agent import Agent
import random
import numpy as np

class QApproxAgent(Agent):
    def __init__(self):
        self.identity = None
        self.nb_victories = 0
        self.nb_games = 0
        self.nex_action = {}
        self.gamma = 1
        self.alpha = 0.1
        self.state_space_x = [
            'prestige',
            'remaining_nobles',
            'owned_tokens',
            'buyable_cards',
            'available_tokens'
            
        ]
        self.state_space_y = [0, 1, 2] # 0: few, 1: some, 2: a lot
        self.state_space = self.build_state_space(self.state_space_x, self.state_space_y)
        self.state_space_inverted_index = self.build_inverted_index(self.state_space)
        
        self.action_space = [
            'buy_card_for_noble', 
            'buy_card_for_prestige',
            'buy_card',
            'reserve_card',
            'take_3',
            'take_2',
            'do_nothing'
        ]
        
        
        
        self.action_space_inverted_index = self.build_inverted_index(self.action_space)
        self.nb_actions = len(self.action_space)
        self.nb_states = len(self.state_space)
        
        self.Q = np.zeros((self.nb_states, self.nb_actions))
        self.R = np.zeros((self.nb_states, self.nb_actions))
        
        self.state = {}
        self.actions = []
        
    def classify_action(self, action):
        action_type = action['type']
        params = action['params']
        [take_3, take_2, reserve, purchase, do_nothing] = game.POSSIBLE_ACTIONS
        classification = ''
        if action_type == take_3:
            classification = 'take_3'
        elif action_type == take_2:
            classification = 'take_2'
        elif action_type == reserve:
            classification = 'reserve_card'
        elif action_type == purchase:
            origin, coord = params
            if origin == 'from_hand':
                i = coord
                card = self.identity.hand[i]
            else:
                i, j = coord
                card = self.state['cards'][i][j]
            player_after_action = self.identity.duplicate()
            player_after_action.bonuses[card.bonus] += 1
            player_after_action.prestige += card.prestige
            
            # Check for noble
            get_visit = False
            for noble in self.state['tiles']:
                if noble.can_visit(player_after_action):
                    get_visit = True
                    break
            if get_visit:
                classification = 'buy_card_for_noble'
            elif card.prestige > 0:
                classification = 'buy_card_for_prestige'
            else:
                classification = 'buy_card'
        else:
            classification = 'do_nothing'
        return self.action_space_inverted_index[classification]
        
    def init(self, player, state, actions):
        self.identity = player
        self.state = state
        self.actions = actions
        
    def build_inverted_index(self, li):
        index = {}
        for i, el in enumerate(li):
            index[el] = i
        return index
        
    def classify_state(self, state):
        player = self.identity
        prestige = player.prestige
        remaining_nobles = len(state['tiles'])
        nb_tokens = sum([amount for c, amount in player.tokens.items()])
        can_buy_card = sum([player.can_buy(card) for card_column in state['cards'] for card in card_column])
        nb_available_tokens = sum([amount for t, amount in state['tokens'].items() if t != game.JOKER_COLOR])
        features = [
            prestige,
            remaining_nobles,
            nb_tokens,
            can_buy_card,
            nb_available_tokens
        ]
        bounds = {
            'prestige': (6, 12),
            'remaining_nobles': (2, 4),
            'owned_tokens': (4, 7),
            'buyable_cards': (3, 6),
            'available_tokens': (7, 28)    
        }
        state_reduced = []
        for i, feature in enumerate(self.state_space_x):
            m, M = bounds[feature]
            if features[i] < m:
                state_reduced.append(0)
            elif features[i] >= M:
                state_reduced.append(2)
            else:
                state_reduced.append(1)
        state_reduced = tuple(state_reduced)
        return state_reduced
        
    def get_current_space(self):
        return self.classify_state(self.state)
        
    def build_state_space(self, x, y):
        n = len(x)
        m = len(y)
        # Output should be of size m**n
        return build_recursive_list([[]], n, m)
    
    def get_transition_name(self, s, a):
        state = self.state_space[s]
        action = self.action_space[a]
        state = self.state_to_string(state)
        lines = state.split("\n")
        lines[2] += " ------> " + action
        return "\n".join(lines)
         
    def state_to_string(self, state):
        sep = "|"
        r_width = 9
        l_width = 18
        names = ['few', 'some', 'lots of']
        res = []
        for i, el in enumerate(state):
            res.append(sep + names[el].rjust(r_width, " ") + " " + self.state_space_x[i].ljust(l_width, " ") + sep)
        return "\n".join(res)
        
        
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
        
    def new_game(self, player, state, actions):
        self.identity = player
        self.state = state
        self.actions = actions
        self.nb_games += 1
        
def build_recursive_list(li, n, m):
    if n == 0:
        return [tuple(l) for l in li]
    else:
        glob = []
        for j in range(m):
            copied_li = [l.copy() for l in li]
            for l in copied_li:
                l.append(j)
            glob = glob + copied_li
        return build_recursive_list(glob, n-1, m)