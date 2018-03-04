import GameConstants as game
from Utils import positive_part, subtract_tokens
import numpy as np
import random

class PlayerData:
    def __init__(self, i):
        self.bonuses = {
        'green': 0, 
        'blue': 0, 
        'red': 0, 
        'white': 0, 
        'black': 0, 
        'yellow': 0}
        self.tokens = {
        'green': 0, 
        'blue': 0, 
        'red': 0, 
        'white': 0, 
        'black': 0, 
        'yellow': 0}
        self.hand = []
        self.nobles = []
        self.prestige = 0
        self.name = "player_" + str(i)
        self.n_tokens = 0
        
    def __str__(self):
        rep = ["-- Player : " + self.name + " --"]
        rep.append("Prestige : " + str(self.prestige))
        rep.append("Tokens : " + game.tokens_to_str(self.tokens))
        rep.append("Bonus  : " + game.tokens_to_str(self.tokens))
        
        return "\n".join(rep)
        
    def rename(self, name):
        self.name = name
        
    def can_buy(self, card):
        '''
        Check if the player can buy the card <card>, using discounts and jokers
        '''
        missing_tokens = 0
        price = self.compute_discounted_price(card)
        for color, amount in price.items():
            if color == game.JOKER_COLOR:
                pass
            if self.tokens[color] < amount:
                missing_tokens += (amount - self.tokens[color])
        jokers = self.tokens['yellow']
        
        return(jokers >= missing_tokens)
        
    def take_tokens(self, state, tokens):
        '''
        Take tokens from the table.
        <tokens> should be a list of tuples (<token_color>, <token_quantity>)
        '''
        message = self.name + " took " + ", ".join([str(amount) + " " + color + " token(s)" for color, amount in tokens])
        
        for color, amount in tokens:
            state.tokens[color] -= amount
            self.tokens[color] += amount
            # Update total number of tokens
            self.n_tokens += amount
        
        game.out(message)

    def reserve_card(self, state, card):
        '''
        Take a card <card> and put it in the player's hand to reserve it. Only him/her can buy it from now on
        '''
        assert len(self.hand) < 3, ("Too many cards in hand for " + self.name)
        self.hand.append(card)
        game.out(self.name, "reserved the following card :", card)
        self.take_tokens(state, [(game.JOKER_COLOR, 1)])
        
        
    def buy_card(self, state, card):
        '''
        Buy the card <card>
        '''
        assert self.can_buy(card)
        
        # First pay for the mine...
        joker_color = game.JOKER_COLOR
        price = self.compute_discounted_price(card)
        for color, amount in price.items():
            if self.tokens[color] >= amount:
                # Enough tokens to pay directly
                self.pay(state, amount, color)
            else:
                # Else, use jokers
                normal_price = self.tokens[color]
                joker_price = amount - self.tokens[color]
                self.pay(state, normal_price, color)
                self.pay(state, joker_price, joker_color)

        # ...then receive bonuses and extra prestige             
        self.prestige += card.prestige
        self.bonuses[card.bonus] += 1
        game.out(self.name, "bought the following card :", card)

    def compute_discounted_price(self, card):
        '''
        If you hold bonuses, you have a discount on dvpt cards. This function computes and returns such discounted price
        '''
        discounted_price = game.get_empty_token_bag()
        for color, price in card.price.items():
            discounted_price[color] = positive_part(price - self.bonuses[color])
        return discounted_price
        
        discounted_price = subtract_tokens(card.price, self.bonuses)
        for color, price in discounted_price.items():
            # Forbid negative prices
            if price < 0:
                discounted_price[color] = 0
        return discounted_price
                    
    def pay(self, state, amount, color):
        '''
        Pay <amount> of <color> tokens
        '''
        if self.tokens[color] < amount:
            game.out("WARNING : the player", self.name, "tried to pay", amount, " ", color, "tokens but had only", self.tokens[color])
            game.out(self)
            amount = self.tokens[color]
        self.tokens[color] -= amount
        state.tokens[color] += amount
        
    def get_card_from_hand(self, i):
        '''
        Retrieve a Card from the hand of the player
        '''
        return self.hand[i]
        
    def pop_card_from_hand(self, i):
        '''
        Retrieve and remove a Card from the hand of the player
        '''
        return self.hand.pop(i)
    
    def remove_extra_tokens(self, state):
        '''
        If the player has currently more than <game.MAX_TOKEN_PER_PLAYER> (=10), then some of them are randomly removed and put back in the game
        '''
        n_tokens = sum([token_quantity for token, token_quantity in self.tokens.items()])
        if n_tokens > game.MAX_TOKEN_PER_PLAYER:
            n_tokens_to_remove = n_tokens - game.MAX_TOKEN_PER_PLAYER
            all_tokens = []
            [all_tokens.extend(nb*[color]) for color, nb in self.tokens.items()]
            random.shuffle(all_tokens)
            tokens_to_remove = all_tokens[:n_tokens_to_remove]
            for color in tokens_to_remove:
                self.pay(state, 1, color)
                
    def choose_noble(self, state, nobles_id):
        '''
        If several nobles can visit a player at the end of its turn, this functions chooses one randomly. If there is only one, then there's no choice.
        /!\  Here, <nobles> is a list of nobles' id, i.e. their index in <state.tiles>
        '''
        if len(nobles_id) == 1:
            noble_id =  nobles_id[0]
        else:
            game.out(self.name, "can be visited by", len(nobles_id), "nobles")
            noble_id = random.choice(nobles_id)
        self.get_noble_from_id(state, noble_id)
            
    def get_noble_from_id(self, state, noble_id):
        '''
        Take a noble tile from the table and gain prestige
        '''
        noble = state.tiles.pop(noble_id)
        self.nobles.append(noble)
        self.prestige += 3
        game.out(self.name, "has gained a noble", noble, "and now have", self.prestige, "prestige points")
    
    def has_won(self):
        '''
        Check if prestige is above the prestige target (=15)
        '''
        return (self.prestige >= game.PRESTIGE_TARGET)
            
            
    
            

        
    
    
                