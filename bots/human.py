class Bot(object):
    """
    Human player. The bid and card to play is decided by a person manually inputting the value when prompted.
    """
    def __init__(self):
        self.name = "human"

    def get_bid(self, current_round_size, bots, trump, cards,hells_bridge,my_bot_details):
        print("### choose the bid ###")
        if hells_bridge==True:
            print("hells bridge")
        
        print("names: {}".format([bot["bot_unique_id"] for bot in bots]))
        print("Previous bids: {}".format([bot["aim_hands_won"] for bot in bots]))
        print("cards: {}".format(cards))
        print("trump: {}".format(trump))
        bid=input("Enter your bid: ")
        return bid
    
    def play_card(self, current_round_size, bots, trump, cards,history,total_bid,valid_cards,my_bot_details):
        print("### choose the card to play next ###")
        print("cards: {}".format(cards))
        print("valid_cards: {}".format(valid_cards))
        print("trump: {}".format(trump))
        print("names: {}".format([bot["bot_unique_id"] for bot in bots]))
        print("bids: {}".format([bot["aim_hands_won"] for bot in bots]))
        print("hands_won: {}".format([bot["hands_won"] for bot in bots]))
        print("cards_played: {}".format([bot["card_played"] for bot in bots]))
        card=input("Enter your card: ")
        return card
