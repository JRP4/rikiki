import random
from cards import Cards
from copy import deepcopy
from NE_bid_bot import (
    create_full_tree,
    find_nash_bids,
    modify_list,
    valid_card_finder,
    refine_choices
)
import time


def find_nash_scores(tree, bids):
    """
    Calculate Nash equilibrium scores for each node in the game tree.

    Args:
    tree (treelib.Tree): The game tree.
    bids (list): List of bids made by players.

    Returns:
    treelib.Tree: The tree with updated Nash equilibrium scores.
    """
    def calculate_score_difference(scores, player_id):
        """
        Calculate the difference between a player's score and others'.

        Args:
        scores (list): List of scores for all players.
        player_id (int): ID of the player to compare against.

        Returns:
        int: Sum of differences between player's score and others'.
        """
        player_score = scores[player_id]
        return sum(player_score - score for i, score in enumerate(scores)
                   if i != player_id)

    # Find the maximum depth in the tree
    max_depth = max(node.data["depth"] for node in tree.all_nodes())

    # Process nodes from bottom to top
    for depth in range(max_depth, 0, -1):
        # Find all nodes at the current depth
        nodes_at_depth = [node for node in tree.all_nodes()
                          if node.data["depth"] == depth]
        
        for node in nodes_at_depth:
            if depth == max_depth:
                # Calculate scores for leaf nodes
                node.data["minmax_score"] = [
                    10 + 2*b if p == b else -2*abs(b-p)
                    for p, b in zip(node.data["minmax_score"], bids)
                ]
            
            parent = tree.parent(node.identifier)
            # Skip if node is root (has no parent)
            if parent is None:
                continue
            
            siblings = tree.children(parent.identifier)
            if len(siblings) == 1:
                # If the parent has only one child, copy the minmax value
                parent.data["minmax_score"] = node.data["minmax_score"]
            else:
                # If there are multiple children, compare their minmax values
                player_id = siblings[0].data["player_id"]
                
                # Calculate the score difference for each sibling
                score_differences = [
                    calculate_score_difference(sibling.data["minmax_score"], player_id)
                    for sibling in siblings
                ]
                
                # Find the maximum score difference
                max_difference = max(score_differences)
                
                # Find all children with the maximum score difference
                best_children = [
                    sibling for sibling, diff in zip(siblings, score_differences)
                    if diff == max_difference
                ]
                
                # If there's more than one best child, choose randomly
                chosen_child = random.choice(best_children)
                parent.data["minmax_score"] = chosen_child.data["minmax_score"]

    return tree


def get_root_action_scores(tree):
    """
    Extract scores for each action from the root node of the tree.

    Args:
    tree (treelib.Tree): The game tree.

    Returns:
    dict: A dictionary mapping actions to their scores.
    """
    root = tree.root
    children = tree.children(root)
    return {node.tag: node.data['minmax_score'] for node in children}


def find_best_action(dictionaries):
    """
    Find the best action based on accumulated scores.

    Args:
    dictionaries (list): List of dictionaries containing action scores.

    Returns:
    dict: A dictionary of actions and their total scores.
    """
    def calculate_score(values):
        """
        Calculate the score for a set of values.

        Args:
        values (list): List of numeric values.

        Returns:
        int: Calculated score.
        """
        if len(values) < 2:
            return 0
        first = values[0]
        return sum(first - v for v in values[1:])

    all_scores = {}

    # Accumulate scores for each action across all dictionaries
    for d in dictionaries:
        for key, values in d.items():
            score = calculate_score(values)
            if key not in all_scores:
                all_scores[key] = score
            else:
                all_scores[key] += score

    if not all_scores:
        return None

    return all_scores


def find_best_action_overall(player_hand, trump, bidtree_root_properties,
                             history, my_bot, bots, p=0.2, nreps=1000):
    """
    Find the best action considering all possible scenarios.

    Args:
    player_hand (list): The player's current hand.
    trump (str): The trump suit.
    bidtree_root_properties (dict): Properties of the bidding tree root.
    history (list): History of played cards.
    my_bot (dict): Information about the current bot.
    bots (list): List of all bots in the game.
    p (float): Probability for bid modification.
    nreps (int): Number of Monte Carlo simulations.

    Returns:
    dict: A dictionary of actions and their scores.
    """
    n_players = len(bots)
    cards_played = [list(d.values()) for d in history]
    cards_played_list = [card for cards in cards_played for card in cards]

    # Extract relevant information from bots
    score = [bot['hands_won'] for bot in bots]
    bot_bids = [bot['aim_hands_won'] for bot in bots]
    starting_position = [bot['start_pos'] for bot in bots]
    starting_bot_id = [bot['bot_unique_id'] for bot in bots]

    # Sort bots information based on starting position
    zipped = list(zip(starting_position, bot_bids, starting_bot_id, score))
    sorted_zip = sorted(zipped)
    _, sorted_bot_bids, sorted_starting_bot_id, sorted_score = zip(*sorted_zip)

    my_bot_id = my_bot["bot_unique_id"]
    other_bots = list(sorted_starting_bot_id)
    other_bots.remove(my_bot_id)

    # Extract partial hands of other bots from history
    partial_hands = [[d.get(key) for d in history] for key in other_bots]
    refined_partial_hands = [[item for item in sublist if item is not None]
                             for sublist in partial_hands]

    outcomes_list = []

    for _ in range(nreps):
        # Deal cards to all opponents
        hands = Cards(excluded_cards=cards_played_list + player_hand)
        hands.shuffle()
        hands.deal(n_players - 1,
                   len(player_hand) + len(cards_played_list) // n_players)
        complete_hands = [a + b for a, b in zip(refined_partial_hands, hands.hands)]

        # Create our player's cards
        our_hand = player_hand + [d.get(my_bot_id) for d in history
                                  if d.get(my_bot_id) is not None]

        hand_size = len(our_hand)
        trimmed_complete_hands = Cards()
        trimmed_complete_hands.hands = [hand[:hand_size] for hand in complete_hands]

        player_id = my_bot["start_pos"]
        trimmed_complete_hands.hands.insert(player_id, our_hand)

        # Check if randomly generated hands are likely to have generated the bids
        tree = create_full_tree(n_players * hand_size, n_players,
                                trimmed_complete_hands, trump,
                                bidtree_root_properties)
        nash_tree_ofbids = find_nash_bids(tree)
        nash_outcome = nash_tree_ofbids.get_node("root").data["minmax_score"]

        comparison_bids = modify_list(list(sorted_bot_bids), p)
        # Only check modified bids as unmodified bids always sum to hand size
        if all(a == b for a, b in zip(comparison_bids, nash_outcome) if a != ''):
            
            trick_end = 1 if len(cards_played[-1]) == n_players else 0

            cards_played_path = ''.join(item for sublist in cards_played
                                        for item in sublist)

            depth = len(cards_played_list)
            if depth == 0:
                previous_winner = ''
                starting_suit = ''
            else:
                if history[-1] == {}:
                    previous_winner = my_bot_id
                    starting_suit = ''
                else:
                    previous_winner = list(history[-1].keys())[0]
                    starting_suit = cards_played[-1][0][-1]

            # Set up root properties for the card tree
            cardtree_root_properties = {
                'name': 'root' + cards_played_path,
                'score': list(sorted_score),
                'trick_end': trick_end,
                'player_id': (player_id - 1) % n_players,
                'starting_suit': starting_suit,
                'depth': depth,
                'cards_played_in_trick': cards_played[-1],
                'previous_trick_winner': previous_winner,
                'cards_played': cards_played,
                'minmax_score': []
            }

            # Calculate remaining cards for each player
            remaining_cards = Cards()
            remaining_cards.hands = [
                [item for item in sublist if item not in cards_played_list]
                for sublist in trimmed_complete_hands.hands
            ]

            # Create and analyze the card tree
            card_tree = create_full_tree(n_players * hand_size, n_players,
                                         remaining_cards, trump,
                                         cardtree_root_properties)
            nash_tree = find_nash_scores(card_tree, sorted_bot_bids)

            action_scores = get_root_action_scores(nash_tree)
            outcomes_list.append(action_scores)

    return find_best_action(outcomes_list)

# The following code is commented out as it appears to be example usage
# player_hand = ['10C', '4D']
# trump = 'H'
# history = [{'basic_bot_v2-2': '9C', 'basic_bot-1': '5C'},
#            {'basic_bot_v2-2': '8D', 'basic_bot-1': '2H'},
#            {'basic_bot-1': 'AC'}]
# bots = [{'bot_instance': '<bots.basic_bot.Bot object at 0x100fbc3d0>',
#          'bot_name': 'basic_bot', 'bot_unique_id': 'basic_bot-1',
#          'hands_won': 1, 'aim_hands_won': 2, 'score': -2, 'start_pos': 0,
#          'card_played': 'AC'},
#         {'bot_instance': '<bots.basic_bot_v2.Bot object at 0x101027d10>',
#          'bot_name': 'basic_bot_v2', 'bot_unique_id': 'basic_bot_v2-2',
#          'hands_won': 1, 'aim_hands_won': 1, 'score': -4, 'start_pos': 1,
#          'card_played': ''}]
# my_bot = {'bot_instance': "<bots.basic_bot_v2.Bot object at 0x100fe95d0>",
#           'bot_name': 'basic_bot_v2', 'bot_unique_id': 'basic_bot_v2-2',
#           'hands_won': 1, 'aim_hands_won': 1, 'score': -4, 'start_pos': 1,
#           'card_played': ''}
# bidtree_root_properties = {'name': 'root',
#                            'score': [0] * len(bots),
#                            'trick_end': 1,
#                            'player_id': len(bots) - 1,
#                            'starting_suit': '',
#                            'depth': 0,
#                            'cards_played_in_trick': [],
#                            'previous_trick_winner': 0,
#                            'cards_played': [],
#                            'minmax_score': []}

# t0 = time.time()
# best_action = find_best_action_overall(player_hand, trump,
#                                        bidtree_root_properties, history,
#                                        my_bot, bots, p=0.2, nreps=1000)
# t1 = time.time()
# print(t1 - t0)
# print(best_action)