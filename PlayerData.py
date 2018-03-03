import GameConstants as game

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
        self.prestige = 0
        self.name = "player_" + i
        self.n_tokens = 0
        
    def can_buy(self, card):
        missing_tokens = 0
        price = card.price
        for color, amount in price.items():
            if self.tokens[color] < amount:
                missing_tokens = missing_tokens + (self.tokens[color] - amount)
        jokers = self.tokens['yellow']
        
        return(jokers >= missing_tokens)
        
    def take_tokens(self, state, tokens):
        message = self.name + " took " + ", ".join([amount + " " + color + " token(s)" for color, amount in tokens])
        
        for color, amount in tokens:
            state.tokens[color] -= amount
            self.tokens[color] += amount
            # Update total number of tokens
            self.n_tokens += amount
        
        game.out(message)

    def reserve_card(self, card):
        assert len(self.hand) < 3, ("Too many cards in hand for " + self.name)
        self.hand.append(card)
        
    def buy_card(self, state, card):
        assert self.can_buy(card)
              
        joker_color = game.JOKER_COLOR
        price = card.price
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
                    
    def pay(self, state, amount, color):
        self.tokens[color] -= amount
        state.tokens[color] += amount
        
    def get_card_from_hand(self, i):
        return self.hand[i]
        
    def pop_card_from_hand(self, i):
        return self.hand.pop(i)
    
            

        
    
    
                