import random
import numpy as np
import GameConstants as game
from PlayerData import PlayerData
from Card import Card
from Tile import Tile

class State:
    def __init__(self):
        # Game
        self.turn = 0
        self.current_player = 0
        self.TARGET_REACHED = False
        self.GAME_ENDED = False
        # Init to empty values
        self.cards = []
        self.tiles = []
        self.tokens = {}
        self.deck = []
        self.players = []
        # Real initialization here
        self.reset()
        
    def visible(self):
        '''
        Return the visible state, ie the "observation space" from which an agent has to take decisions
        '''
        return {
            'cards': self.cards,
            'tiles': self.tiles,
            'tokens': self.tokens,
            'deck': [(len(d) > 0) for d in self.deck]
        }
    
    def still_has_token(self, color):
        '''
        Check if there is still at least one token of color <color> on the board
        '''
        return self.tokens[color] > 0
        
    def reset(self, seed=None):
        '''
        Reset the state
        '''
        random.seed(seed)
        
        self._init_deck()
                
        # State
        self.turn = 0
        self.current_player = 0
        self.TARGET_REACHED = False
        self.GAME_ENDED = False
        print("State reset")
        
    def get_player(self, player_id):
        '''
        Retrieve the player from its id
        '''
        assert(player_id < game.NB_PLAYERS)
        return self.players[player_id]
        
    def step(self, action, player):
        '''
        Main function. Given an action <action> and a player <player>, it updates the state
        accordingly
        
        Input :
        <action> is a dict with two keys :
            - type : a string among <game.POSSIBLE_ACTIONS>
            - params : the parameters of the action. Its format depends on the type.
                - take_3 : list/iterable of three color names : [<color_1>, <color_2>, <color_3>]
                - take_2 : string, color name
                - reserve : origin and coordinate of the card
                    - ['from_table', (i, j)]
                    - ['from_deck', i]
                - purchase : origin and coordinate of the card
                    - ['from_table', (i, j)]
                    - ['from_hand', i]
        '''
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
        visiting_nobles = []
        for noble_id in range(len(self.tiles)):
            noble = self.tiles[noble_id]
            if noble.can_visit(player):
                visiting_nobles.append(noble)
        if len(visiting_nobles) > 0:
            player.choose_noble(self, visiting_nobles)
        
        # CHECK IF PLAYER HAS THE RIGHT AMOUNT OF TOKENS
        player.remove_extra_tokens(self)
        
        # CHECK IF PLAYER HAS WON
        if player.has_won():
            self.player_has_reached_target(player)
        
        self.current_player += 1
        if self.current_player == game.NB_PLAYERS:
            game.out("End of turn", self.turn)
            
            if self.TARGET_REACHED:
                self.GAME_ENDED = True
                game.out("-- END OF THE GAME --")
                return
            
            self.turn += 1
            self.current_player = 0            
            game.out("-- Starting turn", self.turn, "-- ")
        game.out(self.get_current_player().name, "now playing")
    
    def get_card_from_table(self, i, j):
        '''
        Get a Card object from its coordinates on the table
        '''
        old_card = self.cards[i][j]
        if len(self.deck[i]) > 0:
            new_card = self.get_card_from_deck(i)
        else:
            new_card = Card(empty=True)
        self.cards[i][j] = new_card
        
        return old_card

    def get_current_player(self):
        '''
        Get the Player object currently playing
        '''
        return(self.players[self.current_player])
        
    def get_card_from_deck(self, i):
        '''
        Retrieve and remove a Card object from one of the three decks
        '''
        return self.deck[i].pop()
        
    def get_step_reward(self, player):
        '''
        Get the reward of a player for the last turn
        - 100 if the player has reached the prestige target
        - -10 if another player has reached it before
        - 0 in any other case
        '''
        if player.has_won():
            return 100
        elif self.TARGET_REACHED:
            # Another player has won
            return -10
        else:
            return 0
            
    def get_tokens(self):        
        return game.get_tokens() 
        
    def get_cards(self, nb_players=4):
        cards = [Card(level, price, prestige, bonus) for level, price, prestige, bonus in game.get_cards()]
        l1 = [c for c in cards if c.level == 0]
        l2 = [c for c in cards if c.level == 1]
        l3 = [c for c in cards if c.level == 2]
        return l1, l2, l3
        
    def get_tiles(self):
        tiles = [Tile(bonus, prestige) for bonus, prestige in game.get_tiles()]
        return tiles
        
    def player_has_reached_target(self, player):
        '''
        This function is called when one of the player has reached the prestige target
        '''
        game.out(player.name, "has reached", player.prestige, "points. The game will end after the current turn is complete")
        self.TARGET_REACHED = True
        
    def print_deck(self):
        print("splendor - turn", self.turn, "- now playing : player", self.current_player)
        print("---------------------------------------------------------------------------")
        print("".join([str(t) for t in self.tiles]))
        for i in range(game.BOARD_X):
            print("\t".join([str(c) for c in self.cards[i]]))
        print(" - ".join([str(n)+" " + color for color, n in self.tokens.items()]))
        print("---------------------------------------------------------------------------")
        
    def _init_deck(self, nb_players=4):
        # Retrieve development cards
        l1, l2, l3 = self.get_cards()
        game.out("-- Initializing the game --")
        game.out("Nb of level-1 cards :", len(l1))
        game.out("Nb of level-2 cards :", len(l2))
        game.out("Nb of level-3 cards :", len(l3))
        
        random.shuffle(l1)
        random.shuffle(l2)
        random.shuffle(l3)
        # Set up the deck
        nb_reveal = game.BOARD_Y
        deck_1, column_1 = l1[:-nb_reveal], l1[-nb_reveal:]
        deck_2, column_2 = l2[:-nb_reveal], l2[-nb_reveal:]
        deck_3, column_3 = l3[:-nb_reveal], l3[-nb_reveal:]
        
        visible_cards = [column_1, column_2, column_3]
        
        # Tokens
        tokens = self.get_tokens()
        
        # Tiles
        nb_tiles = nb_players + 1
        tiles = self.get_tiles()
        tiles = random.sample(tiles, nb_tiles)
        
        # Declare attributes
        self.cards = visible_cards
        self.tiles = tiles
        self.tokens = tokens
        self.deck = [deck_1, deck_2, deck_3]
        self.players = [PlayerData(i) for i in range(game.NB_PLAYERS)]
        
        self.print_deck()