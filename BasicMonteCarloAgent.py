import GameConstants as game
from Environment import Environment
from State import State
from Agent import Agent
from PlayerData import PlayerData
from Watch import Watch
import random
import operator
import numpy as np

Watch.globalWatch = Watch()
watch = Watch.globalWatch

class BasicMonteCarloAgent(Agent):
    def __init__(self):
        self.identity = None
        self.nb_victories = 0
        self.nb_games = 0
        self.nex_action = {}

        self.DEPTH = -1
        self.RECUSION = 100

        self.state = None
        self.all_actions = []
        self.actions = []
        self.scores = []
        

    def reconstructBoard(self):
        watch.loop()
        builtstate = State(False)
        watch.loop("empty_state")
        cards = list(builtstate.get_cards())
        
        # Set up the deck
        nb_reveal = game.BOARD_Y
        
        # Tiles
        nb_tiles = game.NB_PLAYERS + 1
        tiles = builtstate.get_tiles()
        tiles = random.sample(tiles, nb_tiles)
        
        # Declare attributes
        builtstate.cards = [c.copy() for c in self.state["cards"]]
        builtstate.tiles = self.state["tiles"].copy()
        builtstate.tokens = self.state["tokens"].copy()
        
        for l in range(0,3):
            for i in range(0,game.BOARD_Y):
                card = builtstate.cards[l][i]
                if(not(card.empty)):
                    cards[l].remove(card)

        watch.loop("card_copy")
        random.shuffle(cards[0])
        random.shuffle(cards[1])
        random.shuffle(cards[2])
        watch.loop("shuffle")

        selfplayer = self.state["self"].duplicate()
        builtstate.players = [selfplayer if i==self.state["position"] else PlayerData(i) for i in range(game.NB_PLAYERS)]
        k = 0
        for h in selfplayer.hand:
            cards[h.level].remove(h)
        for player in builtstate.players:
            p = (k-self.state["position"])%game.NB_PLAYERS
            if(p!=0): #Player isn't current player
                playerInfo = self.state["players"][p-1]
                player.hand = []
                for hLevel in playerInfo["hand"]:
                    player.hand.append(cards[hLevel].pop())
                #print(playerInfo["bonuses"].copy())
                player.bonuses = playerInfo["bonuses"].copy()
                player.tokens = playerInfo["tokens"].copy()
                player.prestige = playerInfo["prestige"]
                player.n_tokens = sum([token_quantity for token, token_quantity in player.tokens.items()])
                player.position = k
            k+=1
        watch.loop("player_copy")
        deck = self.state["deck"]
        builtstate.deck = [cards[i][:deck[i]] for i in range(0,3)]
        
        watch.loop("deck_copy")
        # State
        builtstate.turn = 0
        builtstate.current_player = self.state["position"]
        builtstate.TARGET_REACHED = False
        builtstate.GAME_ENDED = False

        board = Environment(builtstate)
        board.step = 0
        board.position = self.state["position"]

        watch.loop("board_end")
        return board

    def monte_carlo(self,action):
        NUMBER_OF_ITERATIONS = 1
        gv = game.VERBOSE
        game.VERBOSE = -10
        count = 0
        for i in range(0,NUMBER_OF_ITERATIONS):
            watch.loop("setup")
            if(self.single_monte_carlo(action)):
                count += 1
        game.VERBOSE = gv
        return count/NUMBER_OF_ITERATIONS

    def single_monte_carlo(self,action):
        board = self.reconstructBoard()
        k=0
        #print(board.state)
        watch.loop()
        while(not(board.state.GAME_ENDED)):
            #print(board.state)
            board.autoplay()
            if(board.state.GAME_ENDED):
                break
            if(k>50):
                return False
            k+=1
        watch.loop("autoplay")
        return board.state.get_player(self.state["position"]).has_won(board.state)

    def select_worthwhile_actions(self):
        self.actions = self.all_actions

    def find_next_action(self,state,actions):
        watch.start()
        self.state = state
        self.all_actions = actions
        self.select_worthwhile_actions()
        self.scores.clear()
        for action in self.actions:
            score = self.monte_carlo(action)
            self.scores.append((action,score))
        best = max(self.scores, key=operator.itemgetter(1))
        return best

    def observe(self, state, reward, done, actions):
        # Update the agent
        
        action = self.find_next_action(state,actions)
        self.next_action = action[0]
        game.out("Next action will be", self.next_action, "; monte carlo gives a score of", action[1])
    
    def act(self):
        # Return an action
        action = self.next_action
        game.out("Deciding to do", action)
        return action
    
    def observe_and_act(self, state, reward, done, actions):
        # Get current state
        self.next_action = self.next_action(state,actions)
        
        # Return an action
        action = self.next_action
        return action
        
    def new_game(self, player):
        self.identity = player
        self.nb_games += 1
        