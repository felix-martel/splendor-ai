import GameConstants as game
from Agent import Agent
import random
import numpy as np

class RefinedQApproxAgent(Agent):
    def __init__(self):
        self.identity = None
        self.nb_victories = 0
        self.nb_games = 0
        self.current_state_id = -1
        self.previous_state_id = -1
        self.last_action_id = -1
        self.next_action = {}
        self.gamma = 1
        self.alpha = 0.1
        self.epsilon = 0.1
        self.state_space_x = [
            'high_prestige',
            'can_buy_prestige',
            'can_buy_card',
            'can_reserve',
            'can_take_2',
            'can_take_3'
            
        ]
        self.state_space_y = [0, 1] # 0: few, 1: some, 2: a lot
        self.state_space, self.state_space_inverted_index = self.build_state_space()
#        self.state_space_inverted_index = self.build_inverted_index(self.state_space)
        
        self.action_space = [
            'buy_prestige',
            'buy_card',
            'reserve',
            'take_3',
            'take_2',
            'do_nothing'
        ]
        self.action_space_inverted_index = self.build_inverted_index(self.action_space)
        self.nb_actions = len(self.action_space)
        self.nb_states = len(self.state_space)
        
        self.last_Q_update = 0
        self.Q = np.ones((self.nb_states, self.nb_actions))
        self.Q[:,5] = 0.05
        self.R = np.ones((self.nb_states, self.nb_actions))
        
        self.state = {}
        self.actions = []
        
    def update_Q(self, s, a, r, next_s):
        '''
        Update Q depending on reward <r>
        Q(s, a) <- (1-alpha) * Q(s, a) + alpha * (r + gamma * max_a' Q(s', a'))
        '''
        max_Q = np.max(self.Q[next_s, :])
        old_Q = self.Q[s, a]
        new_Q = (1-self.alpha)*self.Q[s, a] + self.alpha * (r + self.gamma * max_Q)
        self.last_Q_update = new_Q - old_Q
        self.Q[s, a] = new_Q
        
    def get_last_update(self):
        return self.last_Q_update
        
        
    def possible_transition(self, state, action):
        # Convert action object to string
        if 'type' in action:
            action = action['type']
            
        if action == 'do_nothing':
            return True
        elif action in ['buy_card', 'buy_prestige', 'reserve', 'take_3', 'take_2']:
            return state['can_' + action]
        else:
            game.warning("/!\ Unknown action type :", action)
            return False
        
    def classify_action(self, action, to='id'):
        action_type = action['type']
        params = action['params']
        [take_3, take_2, reserve, purchase, do_nothing] = game.POSSIBLE_ACTIONS
        classification = ''
        if action_type in [take_3, take_2, reserve, do_nothing]:
            classification = action_type
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
            
            if card.prestige > 0:
                classification = 'buy_prestige'
            else:
                # Check for noble
                get_visit = False
                for noble in self.state['tiles']:
                    if noble.can_visit(player_after_action):
                        get_visit = True
                        break
                if get_visit:
                    classification = 'buy_prestige'
                else:
                    classification = 'buy_card'
        else:
            classification = 'do_nothing'
        action = self.convert_action(classification, to=to)
        return action
    
    def convert_action(self, action, to='id'):
        if isinstance(action, str):
            cur = 'name'
        elif isinstance(action, int):
            cur = 'id'
        else:
            game.warning('/!\ Unknown action type')
            return
        
        if cur == to:
            return action
            
        if cur == 'id' and to == 'name':
            return self.action_space[action]
        elif cur == 'name' and to == 'id':
            return self.action_space_inverted_index[action]
        else:
            game.warning('/!\ Unknown action type')
            return
        
    def build_inverted_index(self, li):
        index = {}
        for i, el in enumerate(li):
            index[el] = i
        return index
        
    def classify_state(self, state, to='id'):
        player = self.identity
        cards = [card for card_column in state['cards'] for card in card_column] + player.hand
        token_quantities = [token_quantity for color, token_quantity in state['tokens'].items() if color != game.JOKER_COLOR]
        nobles = state['tiles']
        
        high_prestige = player.prestige >= 12
        can_buy_card = sum([player.can_buy(card) for card in cards]) > 0
        can_buy_prestige = sum([card.grant_prestige(player, nobles) and player.can_buy(card) for card in cards]) > 0
        can_take_3 = sum([token_q>0 for token_q in token_quantities]) >= 3
        can_take_2 = sum([token_q>=game.MIN_TOKEN_FOR_TAKE_2 for token_q in token_quantities]) >= 2
        can_reserve = len(player.hand) < 3
        
        features = [
            high_prestige,
            can_buy_prestige,
            can_buy_card,
            can_reserve,
            can_take_3,
            can_take_2
        ]
        state_reduced = []
        for i in range(len(self.state_space_x)):
            if features[i]:
                state_reduced.append(1)
            else:
                state_reduced.append(0)

        output_state = self.convert_state(state_reduced, to=to)
        return output_state
        
    def get_current_state_id(self):
        return self.current_state_id
        
    def get_next_action_id(self):
        return self.last_action_id
        
    def get_Q_coordinates(self):
        return self.get_current_state_id(), self.get_next_action_id()
    
    def get_transition_name(self, s, a):
        state = self.state_to_string(s)
        action = self.action_space[a]
        lines = state.split("\n")
        lines[2] += " ------> " + action
        return "\n".join(lines)
         
    def state_to_string(self, state):
        state = self.convert_state(state, to='dic')
        res = []
        for feature, value in state.items():
            res.append(feature + " : " + str(value).upper())
        return "\n".join(res)
        
        
    def observe(self, state, reward, done, actions):
        # Update the agent
        if state['self'] != None:
            self.identity = state['self']
        self.state = state
        self.actions = actions
        
        # Update Q
        self.previous_state_id = self.current_state_id
        self.current_state_id = self.classify_state(state, to='id')
        self.update_Q(self.previous_state_id, self.last_action_id, reward, self.current_state_id)
    
    def act_old(self):
        # Return an action
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        actions_by_type = {action_id: [] for action_id in range(len(self.action_space))}
        for action in self.actions:
            a = self.classify_action(action, to='id')
            actions_by_type[a].append(action)
        
        s = self.get_current_state_id()
        rank_action_types = np.flip(np.argsort(self.Q[s,:]), axis=0)
        rank = 0
        next_action_type = rank_action_types[rank]
        possible_actions = actions_by_type[next_action_type]
        while len(possible_actions) == 0:
            rank += 1
            if rank == len(rank_action_types):
                possible_actions = [{'type': 'do_nothing', 'params': None}]
            else:
                next_action_type = rank_action_types[rank]
                possible_actions = actions_by_type[next_action_type]
        
        action = self.choose(possible_actions, next_action_type)
        self.next_action = action
        game.out("Deciding to do", action)
        return action
        
    def act(self):
        actions_by_type = {action_id: [] for action_id in range(len(self.action_space))}
        for action in self.actions:
            a = self.classify_action(action, to='id')
            actions_by_type[a].append(action)
        
        s = self.get_current_state_id()
        actions = self.Q[s,:].copy()       
        
        next_action_type = self.softmax_policy(actions)
        possible_actions = actions_by_type[next_action_type]
        while len(possible_actions) == 0:
            actions[next_action_type] = 0
            next_action_type = self.softmax_policy(actions)
            possible_actions = actions_by_type[next_action_type]
        action = self.choose(possible_actions, next_action_type)
        
        self.last_action_id = next_action_type
        
        self.next_action = action
        game.out("Deciding to do", action)
        return action
        
    def softmax_policy(self, actions):        
        p = normalize(actions)
        f = square #square
        p = f(p)
        p = normalize(p)
        return sample_from_distrib(p)
        
    def epsilon_greedy_policy(self, actions):
        if random.random() < self.epsilon:
            return random.randint(0, len(actions) - 1)
        else:
            return np.argmax(actions)
        
        
    def choose(self, action_set, action_type=None):
        return random.choice(action_set)
    
    def observe_and_act(self, state, reward, done, actions):
        # Get current state
        self.observe(state, reward, done, actions)
        
        # Return an action
        action = self.act()
        self.next_action = action
        return action
        
    def new_game(self, player, state, actions):
        self.identity = player
        self.state = state
        self.actions = actions
        
        self.current_state_id = self.classify_state(state, to='id')
        self.previous_state_id = self.current_state_id
        self.nb_games += 1
        
    def state_id_to_list(self, state_id):
        '''
        19 --> 010011 --> [0, 1, 0, 0, 1, 1]
        '''
#        bin_format = '0' + len(self.state_space_x) + 'b'
#        bin_string = format(state_id, bin_format)
        return [x == '1' for x in format(state_id, '0' + str(len(self.state_space_x)) + 'b')]
        
    def state_id_to_dic(self, state_id):
        '''
        19 --> 010011 --> [0, 1, 0, 0, 1, 1]--> {state_feature_0: 0, state_feature_1: 1, state_feature_2: 0, ...}
        '''
        return self.state_list_to_dic(self.state_id_to_list(state_id))        
        
    def state_list_to_id(self, state_list):
        '''
        [0, 1, 0, 0, 1, 1]  --> 010011 --> int(010011) = 19
        '''
        output_str = ''.join([str(i) for i in state_list])
        return int(output_str, base=2)
        
    def state_list_to_dic(self, state_list):
        '''
        [0, 1, 0, 0, 1, 1] --> {state_feature_0: 0, state_feature_1: 1, state_feature_2: 0, ...}
        '''
        return {name: (state_list[i] == 1) for i, name in enumerate(self.state_space_x)}

    def state_dic_to_list(self, state_dic):
        '''
        {state_feature_0: 0, state_feature_1: 1, state_feature_2: 0, ...} --> [0, 1, 0, ...]
        '''
        return [int(state_dic[feature_name]) for feature_name in self.state_space_x]
        
    def convert_state(self, state, to='id'):
        if isinstance(state, tuple):
            state = list(state)
        if isinstance(state, str):
            state = int(state)
        
        if isinstance(state, int):
            cur = 'id'
        elif isinstance(state, dict):
            cur = 'dic'
        elif isinstance(state, list):
            cur = 'list'
        else:
            game.warning("/!\ Invalid state format", state)
            return
        if cur == to:
            return state
        
        if cur == 'id':
            if to == 'list': 
                return self.state_id_to_list(state)
            elif to == 'dic': 
                return self.state_id_to_dic(state)
        elif cur == 'dic':
            if to == 'list': 
                return self.state_dic_to_list(state)
            elif to == 'id': 
                return self.state_dic_to_id(state)
        elif cur == 'list':
            if to == 'id': 
                return self.state_list_to_id(state)
            elif to == 'dic': 
                return self.state_list_to_dic(state)
                
    def build_state_space(self):
        n = len(self.state_space_x)
        m = len(self.state_space_y)
        size = m**n
        state_space = np.zeros(size, dtype=int)
        inverted_index = {tuple(self.state_id_to_list(s)): s for s in state_space}
        return state_space, inverted_index

        
def normalize(l):
    l = l.copy()
    m = min(l)
    if m < 0:
        l = [el + m for el in l]
    s = sum(l)
    if s == 0:
        return l
    else:
        return [(el/s) for el in l]
        
def square(l):
    return [x**2 for x in l]
    
def identity(l):
    return l
    
def sample_from_distrib(l):
    r = random.random()
    c = 0
    for i, x in enumerate(l):
        c += x
        if r < c:
            return i
    return len(l) - 1
        
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