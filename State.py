import random
import numpy as np
import GameConstants as game
import PlayerData, Card

class State:
    def __init__(self):
        self.reset()
        
    def visible(self):
        return {
            'cards': self.cards,
            'tiles': self.tiles,
            'tokens': self.tokens,
            'deck': [(len(d) > 0) for d in self.deck]
        }
    
    def still_has_token(self, color):
        return self.tokens[color] > 0
        
    def reset(self, seed=None):
        random.seed(seed)
        
        self._init_deck()
                
        # State
        self.turn = 0
        self.current_player = 0
        self.GAME_ENDED = False
        print("State reset")
        
    def get_player(self, player_id):
        assert(player_id < game.NB_PLAYERS)
        return self.players[player_id]
        
    def step(self, action, player):
        [TAKE_3, TAKE_2, RESERVE, PURCHASE] = game.POSSIBLE_ACTIONS
        action_type = action['type']
        params = action['params']
        
        if action_type == TAKE_3:
            tokens = [(color, 1) for color in params]
            player.take_tokens(self, tokens)
            
        elif action_type == TAKE_2:
            tokens = [(params, 2)]
            player.take_tokens(self, tokens)
            
        elif action_type == RESERVE:
            [origin, params] = params
            if origin == 'from_table':
                i, j = params
                card = self.get_card_from_table(i, j)
                player.reserve_card(self, card)
                
            elif origin == 'from_deck':
                i = params
                card = self.get_card_from_deck(i)
                player.reserve_card(self, card)
                
        elif action_type == PURCHASE:
            [origin, params] = params
            if origin == 'from_table':
                i, j = params
                card = self.get_card_from_table(i, j)
                player.buy_card(self, card)
            elif origin == 'from_hand':
                i = params
                card = player.pop_card_from_hand(i)
                player.buy_card(self, card)
        
        # CHECK WHOSE NOBLES ARE VISITING
        
        # CHECK IF PLAYER HAS THE RIGHT AMOUNT OF TOKENS
        
        
        self.current_player += 1
        if self.current_player == game.NB_PLAYERS:
            game.out("End of turn", self.turn)
            
            self.turn += 1
            self.current_player = 0            
            game.out("-- Starting turn", self.turn, "-- ")
        game.out("Player", self.current_player, "now playing")
    
    def get_card_from_table(self, i, j):
        old_card = self.cards[i][j]
        if len(self.deck[i]) > 0:
            new_card = self.get_card_from_deck(i)
        else:
            new_card = Card(empty=True)
        self.cards[i][j] = new_card
        
        return old_card

    def get_current_player(self):
        return(self.players[self.current_player])
        
    def get_card_from_deck(self, i):
        return self.deck[i].pop()
            
    def _build_token_list(self, nb_players=4):
        colors = {
        'green': 7, 
        'blue': 7, 
        'red': 7, 
        'white': 7, 
        'black': 7, 
        'yellow': 5}
        #tokens = np.concatenate([np.full(nb, color) for color, nb in colors.items()])
        
        return colors 
        
    def _build_card_list(self, nb_players=4):
        level_1 = np.full(40, 'level_1')
        level_2 = np.full(30, 'level_2')
        level_3 = np.full(20, 'level_3')
        return level_1, level_2, level_3
        
    def _build_tile_list(self, nb_players=4):
        tiles = np.full(10, 'noble_tile')
        return tiles
        
    def _init_deck(self, nb_players=4):
        # Retrieve development cards
        l1, l2, l3 = self._build_card_list() 
        l1 = random.shuffle(l1)
        l2 = random.shuffle(l2)
        l3 = random.shuffle(l3)
        # Set up the deck
        nb_reveal = 4
        deck_1, column_1 = l1[:-nb_reveal], l1[-nb_reveal:]
        deck_2, column_2 = l2[:-nb_reveal], l2[-nb_reveal:]
        deck_3, column_3 = l3[:-nb_reveal], l3[-nb_reveal:]
        
        visible_cards = [column_1, column_2, column_3]
        
        # Tokens
        tokens = self._build_token_list()
        
        # Tiles
        nb_tiles = nb_players + 1
        tiles = self._build_tile_list()
        tiles = random.sample(tiles, nb_tiles)
        
        # Declare attributes
        self.cards = visible_cards
        self.tiles = tiles
        self.tokens = tokens
        self.deck = [deck_1, deck_2, deck_3]
        self.players = [PlayerData(i) for i in range(game.NB_PLAYERS)]