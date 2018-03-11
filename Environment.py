import numpy as np
import matplotlib.pyplot as plt
import random
from State import State
import GameConstants as game
from Utils import get_subsets


class Environment: 
    
    def __init__(self, adversarial=True):
        self.state = State(adversarial=adversarial)
        self.step = 0
        self.GAME_ENDED = False
        
        game.out("New game")
    
    
    def reset(self):        
        self.state.reset()
        self.step = 0
        
        # State
        self.GAME_ENDED = False
        game.out("Environment reset")
        
        return(self.get_player())
    
    def get_step_reward(self, player):
        return self.state.get_step_reward(player)
    
    def take_action(self, action, player):
        # Updating state
        self.state.step(action, player)
        
        # Retrieving new observations

        end = self.state.TARGET_REACHED
        debug = {'full_state': self.state}
        state = self.state.visible(player)
        reward = self.get_step_reward(player)
                
        self.step += 1
        return(state, reward, end, debug)
        
    def autoplay(self):
        for player_id in range(self.state.current_player+1, game.NB_PLAYERS):
            current_player = self.state.get_player(player_id)
            self.take_random_action(current_player)
    
    def take_random_action(self, player):
        action = self.get_random_action(player)
        self.take_action(action, player)
        
    def get_random_action(self, player):
        action = random.choice(self.get_possible_actions(player))
        return(action)
        
    def get_player(self, player_id = 0):
        return self.state.get_player(player_id)
        
    def get_visible_state(self,player):
        return self.state.visible(player)
        
    def winner(self, how='name'):
        if how == 'name':
            return self.state.winner_name
        elif how == 'pos':
            return self.state.winner_id
        else:
            return self.state.winner
        
    def get_best_adversary_score(self):
        leaderboard = [(p.position, p.prestige) for p in self.state.players]
        leaderboard.sort(key=lambda x: -x[1])
        if leaderboard[0][0] == 0:
            return leaderboard[1][1]
        else:
            return leaderboard[0][1]

    def get_possible_actions(self, player):
        actions = []
        # First type : take_3
        take_3 = game.POSSIBLE_ACTIONS[0]
        # Retrieve list of tokens minus the yellow ones (they cannot be picked)
        allowed_tokens = game.TOKEN_TYPES.copy()
        allowed_tokens.remove(game.JOKER_COLOR)
        available_tokens = set()
        # Check if there's still available tokens of each color
        for color in allowed_tokens:
            if self.state.still_has_token(color):
                available_tokens.add(color)
        # Get all 3-tuples of available tokens
        all_token_tuples = get_subsets(available_tokens, 3)
        # Add them to the list of possible actions
        for token_tuple in all_token_tuples:
            new_action = {
                'type': take_3,
                'params': token_tuple
            }
            actions.append(new_action)
        
        # Second type : take_2
        take_2 = game.POSSIBLE_ACTIONS[1]
        for color in allowed_tokens:
            if self.state.tokens[color] >= game.MIN_TOKEN_FOR_TAKE_2:
                new_action = {
                    'type': take_2,
                    'params': color
                }
                actions.append(new_action)
        
        # Third type : reserve
        reserve = game.POSSIBLE_ACTIONS[2]
        if len(player.hand) < game.MAX_RESERVED_CARDS:
            # Pick a reserved cards from the middle of the table
            for i in range(game.BOARD_X):
                for j in range(game.BOARD_Y):
                    if self.state.cards[i][j].is_empty():
                        break
                    new_action = {
                        'type': reserve,
                        'params': ['from_table', (i, j)]
                        }
                    actions.append(new_action)
            # Pick a card from the deck
            for i in range(game.DECK_SIZE):
                if len(self.state.deck[i]) > 0:
                    new_action = {
                        'type': reserve,
                        'params': ['from_deck', i]
                    }
                    actions.append(new_action)
        
        # Fourth : buy a dvpt card
        purchase = game.POSSIBLE_ACTIONS[3]
        for i in range(game.BOARD_X):
            for j in range(game.BOARD_Y):
                if self.state.cards[i][j].is_empty():
                    break
                card = self.state.cards[i][j]
                if player.can_buy(card):
                    new_action = {
                        'type': purchase,
                        'params': ['from_table', (i, j)]
                    }
                    actions.append(new_action)
        for i in range(len(player.hand)):
            card = player.hand[i]
            if player.can_buy(card):
                new_action = {
                    'type': purchase,
                    'params': ['from_hand', i]
                }
                actions.append(new_action)
                
        # Else: do nothing
        if len(actions) == 0:
            do_nothing = game.POSSIBLE_ACTIONS[4]
            new_action = {
                'type': do_nothing,
                'params': None
                }
            actions.append(new_action)
           
        
        return(actions)
       
       
  


       

      
    