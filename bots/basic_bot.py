import random

class Bot(object):
    """
    Basic computer player. Chooses a bid of 1 and a random card in the 'valid_cards' array.
    """

    def __init__(self):
        self.name = "basic_bot"

    def get_bid(self, current_round_size, bots, trump, cards,hells_bridge,my_bot_details):
        return 1
    
    def play_card(self, current_round_size, bots, trump, cards, history, total_bid, valid_cards, my_bot_details):
        return random.choice(valid_cards)