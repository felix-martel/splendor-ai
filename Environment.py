import numpy as np
import matplotlib.pyplot as plt
import random
from State import State
import GameConstants as game


class Environment: 
    
    def __init__(self):
        self.state = State()
        
        print("New game")
    
    
    def reset(self):        
        self.state.reset()
        self.step = 0
        
        # State
        self.GAME_ENDED = False
        game.out("Environment reset")
        
        return(self.state.get_player(0))
    
    def get_step_reward(self, player):
        return self.state.get_step_reward(player)
    
    def take_action(self, action, player):
        # Updating state
        self.state.step(action, player)
        
        # Retrieving new observations
        state = self.state.visible()
        reward = self.get_step_reward(player)
        end = self.state.GAME_ENDED
        debug = {'full_state': self.state}
                
        self.step += 1
        return(state, reward, end, debug)
        
    def autoplay(self):
        for player_id in range(1, game.NB_PLAYERS):
            current_player = self.state.get_player(player_id)
            self.take_random_action(current_player)
    
    def take_random_action(self, player):
        action = self.get_random_action(player)
        self.take_action(action, player)
        
    def get_random_action(self, player):
        action = random.choice(self.get_possible_actions(player))
        return(action)
        
    def get_possible_actions(self, player):
        actions = []
        # First type : take_3
        take_3 = game.POSSIBLE_ACTIONS[0]        
        n = len(game.TOKEN_TYPES)
        for i in range(n):
            color_1 = game.TOKEN_TYPES[i]
            if self.state.still_has_token(color_1):
                for j in range(i, n):
                    color_2 = game.TOKEN_TYPES[j]
                    if self.state.still_has_token(color_2):
                        for k in range(j, n):
                            color_3 = game.TOKEN_TYPES[k]
                            if self.state.still_has_token(color_3):
                                new_action = {
                                    'type': take_3,
                                    'params': [color_1, color_2, color_3]
                                }
                                actions.append(new_action)
        
        # Second type : take_2
        take_2 = game.POSSIBLE_ACTIONS[1]
        for color in game.TOKEN_TYPES:
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
           
        
        return(actions)
       
       
  


       

      
    