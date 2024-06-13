import random

class Bot(object):
    """
    Basic computer player. Chooses a bid and card according to some basic rules.
    """

    def __init__(self):
        self.name = "basic_bot_v2"

    # the bid value is the number of trumps plus the number of face cards and aces (provided they are not trumps)
    def get_bid(self, current_round_size, bots, trump, cards,hells_bridge,my_bot_details):
        card_suits=[card[-1] for card in cards]
        cards_nontrumps= [card for card in cards if not card.endswith(trump)]
        card_values = [card[:-1] for card in cards_nontrumps]
        values = {"2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "J":11, "Q":12, "K":13, "A":14}
        return sum([suit==trump for suit in card_suits])+sum([values[card]>10 for card in card_values])
    
    def play_card(self, current_round_size, bots, trump, cards, history, total_bid, valid_cards, my_bot_details):
        return random.choice(valid_cards)