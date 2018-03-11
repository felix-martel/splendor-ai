import GameConstants as game
from Agent import Agent
import random
import numpy as np
import Utils

from sklearn import linear_model, neural_network

class HeuristicAgent(Agent):
    def __init__(self, train=True, train_set=[], clf='ridge'):
        self.identity = None
        self.nb_victories = 0
        self.nb_games = 0
        self.next_action = {}
        self.gamma = 1
        self.initial_alpha = 0.05
        self.min_alpha = 0.005
        self.alpha_update_rate = 1 # pow(self.initial_alpha/self.min_alpha, 1/500)
        self.alpha = self.initial_alpha
        self.epsilon = 0.1
        self.state_space_x = [
            'low_prestige',
            'high_prestige',
            'can_buy_prestige',
            'can_buy_card',
            'can_reserve',
            'can_take_2',
            'can_take_3'
            
        ]
        self.training_phase = train
        self.is_trained = not train
        self.classifier = {
            'ridge': linear_model.RidgeCV(),
            'mlp': neural_network.MLPRegressor()        
        }[clf]
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
        
        self.state = {}
        self.actions = []  
        
        self.init_features()
        if len(train_set) > 0:
            self.load_training(train_set)
        
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
        
        low_prestige = player.prestige < 9
        high_prestige = player.prestige >= 12
        can_buy_card = sum([player.can_buy(card) for card in cards]) > 0
        can_buy_prestige = sum([card.grant_prestige(player, nobles) and player.can_buy(card) for card in cards]) > 0
        can_take_3 = sum([token_q>0 for token_q in token_quantities]) >= 3
        can_take_2 = sum([token_q>=game.MIN_TOKEN_FOR_TAKE_2 for token_q in token_quantities]) >= 2
        can_reserve = len(player.hand) < 3
        
        features = [
            low_prestige,
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
        
    def has_won(self):
        return self.identity.has_won()
    
    def get_transition_name(self, s, a):
        state = self.state_to_string(s)
        action = self.action_space[a]
        lines = state.split("\n")
        lines = [s.rjust(25, " ") for s in lines]
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
        
    def train(self, state, action, reward):
        self.state = state
        action_type = self.classify_action(action, to='name')
        output = self.get_entry(action, action_type)
        output['expected_gain'] = reward
        output['action_type'] = self.convert_action(action_type, to='id')
        
        self.add_entry(output)
        
    def predict(self, options_dic):
        options = []
        for fs in options_dic:
            new_entry = np.zeros(len(self.features))
            for feature, val in fs.items():
                if feature in self.features:
                    feature_index = self.features_index[feature]
                    new_entry[feature_index] = val
            options.append(new_entry)
        d = np.array(options)
        x = d[:, :-1]
        y = self.classifier.predict(x)
        return int(np.argmax(y))        
        
    def act(self):
        if self.training_phase:
            return random.choice(self.actions)
            
        option_space = []
        for action in self.actions:
            action_type = self.classify_action(action, to='name')
            output = self.get_entry(action, action_type)
            output['action_type'] = self.convert_action(action_type, to='id')
            option_space.append(output)
        
        best_action_index = self.predict(option_space)
        return self.actions[best_action_index]
        
    def load_training(self, d):
        self.data = d.copy()
        self.stop_training()
        
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
    
    def init_features(self):
        self.features = [
            'current_score',
            'best_adv_score',
            'nb_available_colors',
            'nb_full_available_colors',
            'hand_size',
            'hand_slot_gain',
            'current_step',
            'action_type',
            'prestige_gain',
            'bonus_gain',
            'card_gain',
            'token_loss',
            'free_slot_bonus',
            'allow_reserve_bonus',
            'fill_slot_malus',
            'unlock_prestige',
            'unlock_card',
            'over_max_token',
            'gold_token_gain',
            'can_buy_next_turn',
            'reserved_card_price',
            'expected_gain'
        ]
        self.features_index = {name: index for index, name in enumerate(self.features)}
        self.data = []
        
    def add_entry(self, fs):
        new_entry = np.zeros(len(self.features))
        for feature, val in fs.items():
            if feature in self.features:
                feature_index = self.features_index[feature]
                new_entry[feature_index] = val
        entry_pos = len(self.data)
        self.data.append(new_entry)
        return entry_pos
                
        
    def choose(self, action_set, action_type=None):
        if random.random() < self.epsilon:
            return random.choice(action_set)
        else:
            best_action = action_set[0]
            best_heuristic = self.heuristic(best_action, action_type)
            for i in range(1, len(action_set)):
                h = self.heuristic(action_set[i], action_type)
                if h > best_heuristic:
                    best_heuristic = h
                    best_action = action_set[i]
            return best_action
        
    def _heuristic_buy_prestige(self, action):
        comes_from_hand = action['params'][0] == 'from_hand'
        card_coords = action['params'][1]
        if not comes_from_hand:
            i, j = card_coords
        card = self.identity.hand[card_coords] if comes_from_hand else self.state['cards'][i][j]
        output = self.init_new_entry()
        # Free a slot in hand = extra bonus
        if comes_from_hand:
            output['hand_slot_gain'] = 1
            if len(self.identity.hand) == game.MAX_RESERVED_CARDS:
                output['allow_reserve_bonus'] = 1
                output['free_slot_bonus'] = 1
            else:
                output['free_slot_bonus'] = 1
        prestige_gain = card.prestige
        if len([n.prestige for n in self.state['tiles'] if card.unlock_noble(self.identity, n)]) > 0:
            prestige_gain += 3
        output['prestige_gain'] = prestige_gain
        output['token_loss'] = sum([amount for color, amount in self.identity.compute_discounted_price(card).items()])
        
        return output
        
    def _heuristic_take_3(self, action):
        color_list = action['params']
        output = self.init_new_entry()
        player_after = self.identity.duplicate()
        for color in color_list:
            player_after.tokens[color] += 1
        
        nb_can_buy = 0
        nb_can_buy_prestige = 0
        for card_list in self.state['cards']:
            for card in card_list:
                if player_after.can_buy(card):
                    if card.grant_prestige(player_after, self.state['tiles']):
                        nb_can_buy_prestige += 1
                    else:
                        nb_can_buy += 1
        n_tokens = sum([token_quantity for token, token_quantity in self.identity.tokens.items()])
        if n_tokens + 3 > 10:
            output['over_max_token'] = n_tokens-7
        output['unlock_card'] = nb_can_buy
        output['unlock_prestige'] = nb_can_buy_prestige       
        
        # Also : add a bonus if taking these tokens blocks another player
        
        return output
        
        
    def _heuristic_take_2(self, action):
        color = action['params']
        player_after = self.identity.duplicate()
        player_after.tokens[color] += 2
        output = self.init_new_entry()
        nb_can_buy = 0
        nb_can_buy_prestige = 0
        for card_list in self.state['cards']:
            for card in card_list:
                if player_after.can_buy(card):
                    if card.grant_prestige(player_after, self.state['tiles']):
                        nb_can_buy_prestige += 1
                    else:
                        nb_can_buy += 1
        n_tokens = sum([token_quantity for token, token_quantity in self.identity.tokens.items()])
        if n_tokens + 2 > 10:
            output['over_max_token'] = n_tokens-8
        output['unlock_card'] = nb_can_buy
        output['unlock_prestige'] = nb_can_buy_prestige
        # Also : add a bonus if taking these tokens blocks another player
        
        return output
        
    def _heuristic_do_nothing(self, action):
        output = self.init_new_entry()
        output['do_nothing_malus'] = 1000000
        return output
        
    def _heuristic_reserve(self, action):
        [card_origin, coords] = action['params']
        if card_origin == 'from_deck':
            return {}
        else:
            i, j = coords
        card = self.state['cards'][i][j]
        s = Utils.subtract_tokens(self.identity.compute_discounted_price(card), self.identity.tokens)
        s = [missing_amount for c, missing_amount in s.items() if missing_amount > 0]
        can_buy_next_turn = (len(s) == 0) or (len(s) == 1 and s[0] <= 2) or (len(s) <= 3 and sum([m<=1 for m in s])==len(s)) 
        price_malus = sum([amount for color, amount in self.identity.compute_discounted_price(card).items()])
        
        output = self.init_new_entry()
        output['hand_slot_gain'] = -1
        output['gold_token_gain'] = 1
        output['fill_slot_malus'] = 1
        output['can_buy_next_turn'] = 1 if can_buy_next_turn else 0
        output['reserved_card_price'] = price_malus
        
        return output
        
    def _heuristic_buy_card(self, action):
        comes_from_hand = action['params'][0] == 'from_hand'
        card_coords = action['params'][1]
        if not comes_from_hand:
            i, j = card_coords
        card = self.identity.hand[card_coords] if comes_from_hand else self.state['cards'][i][j]
        output = self.init_new_entry()
        # Free a slot in hand = extra bonus
        if comes_from_hand:
            output['free_slot_bonus'] = 1
            if len(self.identity.hand) == game.MAX_RESERVED_CARDS:
                output['allow_reserve_bonus'] = 1
        if sum([card.unlock_noble(self.identity, noble) for noble in self.state['tiles']]) > 0:
            output['unlock_prestige'] = 1
        output['prestige_gain'] = card.prestige
        output['card_gain'] = 1
        output['token_loss'] = sum([amount for color, amount in self.identity.compute_discounted_price(card).items()])
        
        return output
        
    def get_entry(self, action, action_type):
        if action_type == 'take_3':
            return self._heuristic_take_3(action)
        elif action_type == 'take_2':
            return self._heuristic_take_2(action)
        elif action_type == 'reserve':
            return self._heuristic_reserve(action)
        elif action_type == 'buy_card':
            return self._heuristic_buy_card(action)
        elif action_type == 'buy_prestige':
            return self._heuristic_buy_prestige(action)
        elif action_type == 'do_nothing':
            return self._heuristic_do_nothing(action)
        else:
            game.warning("/!\ Unknown action type in heuristic filtering", action)
            return {}
    
    def init_new_entry(self):
        token_quantities = [token_quantity for color, token_quantity in self.state['tokens'].items() if color != game.JOKER_COLOR]
        
        output = {}
        output['current_score'] = 15 - self.identity.prestige
        output['best_adv_score'] = min([15 - p['prestige'] for p in self.state['players']])
        output['nb_available_colors'] = sum([token_q>0 for token_q in token_quantities])
        output['nb_full_available_colors'] = sum([token_q>=game.MIN_TOKEN_FOR_TAKE_2 for token_q in token_quantities])
        output['hand_size'] = len(self.identity.hand)
        
        # sum([token_q>=game.MIN_TOKEN_FOR_TAKE_2 for token_q in token_quantities])
        return output
    
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
        
    def stop_training(self):
        self.training_phase = False
        self.is_trained = True
        train = np.array(self.data)
        x, y = train[:,:-1], train[:,-1]
        self.classifier = linear_model.RidgeCV()
        self.classifier.fit(x, y)
        
        
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

    def export_Q(self, filename):
        n_state, n_action = self.Q.shape
        col_format = '{:12}' # '{:' + col_width + '}'
        sep = "  |  "
        
        with open(filename, 'w') as f:
            for s in range(n_state):
                res = self.state_to_string(s)
                lines = res.split("\n")
                cols = ['{:30}'.format(l) for l in lines]
                cols = [[l] for l in cols]
                for a in range(n_action):
                    t = self.convert_action(a, to="name")
                    v = self.Q[s, a]
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