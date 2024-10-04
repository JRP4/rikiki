from NE_bid_bot import find_bid
from NE_card_bot import find_best_action_overall
import random


class Bot(object):
    """
    Nash Equilibrium bot. Creates a decision tree of all possible outcomes
    for a given hand and finds the Nash Equilibrium.
    Uses a Monte Carlo method to simulate lots of possible hands to get a bid.
    """

    def __init__(self):
        """
        Initialize the Nash Equilibrium bot.
        """
        self.name = "NE_bot"

    def get_bid(self, current_round_size, bots, trump, cards,
                hells_bridge, my_bot_details):
        """
        Determine the optimal bid for the current hand.

        Args:
        current_round_size (int): The number of cards in the current round.
        bots (list): List of all bots in the game.
        trump (str): The trump suit.
        cards (list): The bot's current hand.
        hells_bridge (bool): Whether the game is in Hells Bridge mode.
        my_bot_details (dict): Details about this bot.

        Returns:
        int: The optimal bid for the current hand.
        """
        # Extract the bids made by other bots
        aim_hands_win_list = [bot['aim_hands_won'] for bot in bots]
        
        if not hells_bridge:
            # Standard bidding process for normal game mode
            n_players = len(bots)
            
            # Set up root properties for the bidding tree
            root_properties = {
                'name': 'root',
                'score': [0] * n_players,
                'trick_end': 1,
                'player_id': n_players - 1,
                'starting_suit': '',
                'depth': 0,
                'cards_played_in_trick': [],
                'previous_trick_winner': 0,
                'cards_played': [],
                'minmax_score': []
            }
            
            # Use Monte Carlo simulation to find the optimal bid
            element_count = find_bid(cards, aim_hands_win_list, trump,
                                     my_bot_details["start_pos"],
                                     root_properties)
            
            # Choose the most common bid from the simulations
            most_common_bid = max(element_count, key=element_count.get)
            return most_common_bid
        else:
            # In Hells Bridge mode, always bid 1
            return 1
    
    def play_card(self, current_round_size, bots, trump, cards, history,
                  total_bid, valid_cards, my_bot_details):
        """
        Decide which card to play in the current round.

        Args:
        current_round_size (int): The number of cards in the current round.
        bots (list): List of all bots in the game.
        trump (str): The trump suit.
        cards (list): The bot's current hand.
        history (list): History of played cards.
        total_bid (int): Total bid for the current round.
        valid_cards (list): List of valid cards that can be played.
        my_bot_details (dict): Details about this bot.

        Returns:
        str: The card to play.
        """
        # If there's only one valid card, play it
        if len(valid_cards) == 1:
            return valid_cards[0]
        else:
            n_players = len(bots)
            
            # Set up root properties for the bidding tree
            bidtree_root_properties = {
                'name': 'root',
                'score': [0] * n_players,
                'trick_end': 1,
                'player_id': n_players - 1,
                'starting_suit': '',
                'depth': 0,
                'cards_played_in_trick': [],
                'previous_trick_winner': 0,
                'cards_played': [],
                'minmax_score': []
            }
            
            # Use Monte Carlo simulation to find the best action
            action_dictionary = find_best_action_overall(
                cards, trump, bidtree_root_properties, history,
                my_bot_details, bots
            )
            
            if action_dictionary is None:
                # If no simulations were appropriate, choose a random valid card
                best_action = random.choice(valid_cards)
            else:
                # Choose the action with the highest score
                best_action = max(action_dictionary, key=action_dictionary.get)
            
            return best_action