from random import shuffle

#class for shuffling and dealing a standard deck of cards
class Cards:
    def __init__(self):
        # suits are labelled according to the first letter in the suit of a standard deck of cards
        values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        suits = ['H', 'S', 'C', 'D']
        # the + in the line below performs a concatenation of strings, hence outputs is 'AH', '4D', etc.
        self.deck = [j + i for j in values for i in suits]

    def shuffle(self):
        shuffle(self.deck)

    def deal(self, n_players,size):
        # function for dealing cards, input the number of players and the number of card they should each recieve.
        self.hands = [self.deck[i::n_players][:size] for i in range(0, n_players)]
        # trump is decided by suit of card at the 'top of the deck' after shuffling
        if n_players*size<52:
            self.trump=self.deck[n_players*size][-1]
        else:
            #if all the cards have been dealt there is no trump suit
            self.trump="None"
        