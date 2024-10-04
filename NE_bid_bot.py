import random
from cards import Cards
from copy import deepcopy
import treelib
import time

def valid_card_finder(hand, starting_suit, excluded_cards=None):
    """
    Find valid cards to play based on the starting suit and excluded cards.

    Args:
    hand (list): The player's hand.
    starting_suit (str): The suit of the first card played in the trick.
    excluded_cards (list): Cards that have already been played.

    Returns:
    list: Valid cards that can be played.
    """
    if excluded_cards is None:
        excluded_cards = []
    
    # Flatten the excluded_cards list
    flat_excluded_cards = [card for sublist in excluded_cards for card in sublist]
    
    # Find valid cards of the starting suit
    valid_cards = [card for card in hand if card[-1] == starting_suit and card not in flat_excluded_cards]
    
    # If no valid cards of the starting suit, allow any card
    if not valid_cards:
        valid_cards = [card for card in hand if card not in flat_excluded_cards]
    
    return valid_cards

def pick_winner_of_hand(played_cards, trump):
    """
    Determine the winning card of a trick.

    Args:
    played_cards (list): Cards played in the trick.
    trump (str): The trump suit.

    Returns:
    int: Index of the winning card in played_cards.
    """
    current_winner = played_cards[0]
    values = {"2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "J":11, "Q":12, "K":13, "A":14}

    for card in played_cards[1:]:
        # Compare cards of the same suit
        if card[-1] == current_winner[-1] and values[card[:-1]] > values[current_winner[:-1]]:
            current_winner = card
        # Trump card beats non-trump
        elif current_winner[-1] != trump and card[-1] == trump:
            current_winner = card
    
    return played_cards.index(current_winner)

def refine_choices(played_cards, valid_cards, trump):
    """
    Refine the choice of cards to play based on the current trick state.

    Args:
    played_cards (list): Cards already played in the trick.
    valid_cards (list): Valid cards that can be played.
    trump (str): The trump suit.

    Returns:
    list: Refined list of cards to choose from.
    """
    values = {"2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "J":11, "Q":12, "K":13, "A":14}
    
    if not played_cards or len(valid_cards) == 1:
        return valid_cards
    else:
        current_winner = played_cards[pick_winner_of_hand(played_cards, trump)]
        
        # If we can't win, play the lowest card
        if pick_winner_of_hand([current_winner] + valid_cards, trump) == 0:
            card_values = [values[card[:-1]] for card in valid_cards]
            min_value = card_values.index(min(card_values))
            return [valid_cards[min_value]]
        else:
            # We might win, so keep all options open
            return valid_cards

def create_full_tree(max_depth, n_players, hands, trump, root_properties):
    """
    Create a full game tree for the current game state.

    Args:
    max_depth (int): Maximum depth of the tree.
    n_players (int): Number of players in the game.
    hands (Cards): Current hands of all players.
    trump (str): The trump suit.
    root_properties (dict): Properties of the root node.

    Returns:
    treelib.Tree: The full game tree.
    """
    player_ids = list(range(n_players))
    
    def build_tree(tree, parent_id, current_depth):
        if current_depth >= max_depth:
            return
        
        node = tree.get_node(parent_id)
        
        # Determine the next player
        player_id = (node.data["player_id"] + 1) % n_players if node.data["trick_end"] == 0 else node.data["previous_trick_winner"]
        
        hand = hands.hands[player_ids[player_id]]

        possible_children = valid_card_finder(hand, node.data['starting_suit'], excluded_cards=node.data["cards_played"])
        refined_possible_children = refine_choices(node.data["cards_played_in_trick"], possible_children, trump)

        for child_value in refined_possible_children:
            child_properties = deepcopy(node.data)
            child_properties.update({
                'name': child_value,
                'player_id': player_id,
                'depth': node.data['depth'] + 1
            })

            child_identifer = node.identifier + child_value

            # Handle new trick
            if child_properties['trick_end'] == 1:
                child_properties.update({
                    'starting_suit': child_value[-1],
                    'trick_end': 0,
                    'cards_played_in_trick': []
                })
            
            child_properties['cards_played_in_trick'].append(child_value)

            # Handle end of trick
            if len(child_properties['cards_played_in_trick']) == n_players:
                child_properties['trick_end'] = 1
                child_properties['cards_played'].append(child_properties['cards_played_in_trick'])

                # Determine trick winner and update scores
                winning_position = pick_winner_of_hand(child_properties['cards_played_in_trick'], trump)
                winning_player = (child_properties['player_id'] + winning_position + 1) % n_players
                child_properties['score'][winning_player] += 1
                child_properties['previous_trick_winner'] = winning_player

            if child_properties['depth'] == max_depth:
                child_properties['minmax_score'] = deepcopy(child_properties['score'])
            
            tree.create_node(child_properties['name'], child_identifer, parent=node.identifier, data=child_properties)
            build_tree(tree, child_identifer, current_depth + 1)

    tree = treelib.Tree()
    tree.create_node("Root", "root", data=root_properties)
    build_tree(tree, "root", root_properties['depth'])
    return tree

def print_tree(tree):
    """
    Print the tree structure.

    Args:
    tree (treelib.Tree): The tree to be printed.
    """
    output = tree.show(stdout=False)
    print(output.decode('utf-8') if isinstance(output, bytes) else output)

def find_nash_bids(tree):
    """
    Find Nash equilibrium bids in the game tree.

    Args:
    tree (treelib.Tree): The game tree.

    Returns:
    treelib.Tree: The tree with Nash equilibrium bids.
    """
    max_depth = max(node.data["depth"] for node in tree.all_nodes())
    
    # Process nodes from bottom to top
    for depth in range(max_depth, -1, -1):
        nodes_at_depth = [node for node in tree.all_nodes() if node.data["depth"] == depth]
        
        for node in nodes_at_depth:
            parent = tree.parent(node.identifier)
            if parent is None:
                continue
            
            siblings = tree.children(parent.identifier)
            
            if len(siblings) == 1:
                parent.data["minmax_score"] = node.data["minmax_score"]
            else:
                player_id = siblings[0].data["player_id"]
                best_value = max(sibling.data["minmax_score"][player_id] for sibling in siblings)
                
                # Find all children with the best value
                best_children = [sibling for sibling in siblings 
                                 if sibling.data["minmax_score"][player_id] == best_value]
                
                # Randomly choose among best children
                chosen_child = random.choice(best_children)
                parent.data["minmax_score"] = chosen_child.data["minmax_score"]
    return tree

def modify_list(input_list, p):
    """
    Modify a list of bids to introduce some randomness.

    Args:
    input_list (list): List of bids.
    p (float): Probability of modifying each bid.

    Returns:
    list: Modified list of bids.
    """
    result = []
    for index, item in enumerate(input_list):
        if item == '':
            result.append(item)
        else:
            # Higher chance of modification for the last item
            current_p = 2 * p if index == len(input_list) - 1 else p
            
            if random.random() < current_p:
                # Randomly increase or decrease the bid
                result.append(item + 1 if random.random() < 0.5 else max(0, item - 1))
            else:
                result.append(item)
    return result

def find_bid(player_hand, previous_bids, trump, player_id, root_properties, p=0.2, nreps=1000):
    """
    Find the optimal bid for the current player.

    Args:
    player_hand (list): The player's hand.
    previous_bids (list): Bids made by other players.
    trump (str): The trump suit.
    player_id (int): The current player's ID.
    root_properties (dict): Properties of the root node.
    p (float): Probability for bid modification.
    nreps (int): Number of Monte Carlo simulations.

    Returns:
    dict: A dictionary of possible bids and their frequencies.
    """
    n_players = len(previous_bids)
    hand_size = len(player_hand)
    outcomes_list = []

    for _ in range(nreps):
        # Simulate opponents' hands
        hands = Cards(excluded_cards=player_hand)
        hands.shuffle()
        hands.deal(n_players - 1, hand_size)

        player_position = sum([bid != '' for bid in previous_bids])
        hands.hands.insert(player_id, player_hand)

        # Create and analyze the game tree
        tree = create_full_tree(n_players * hand_size, n_players, hands, trump, root_properties)
        nash_tree = find_nash_bids(tree)
        nash_outcome = nash_tree.get_node("root").data["minmax_score"]

        # Compare with previous and modified bids
        comparison_bids = modify_list(previous_bids, p)
        if all(a == b for a, b in zip(previous_bids, nash_outcome) if a != '') or \
           all(a == b for a, b in zip(comparison_bids, nash_outcome) if a != ''):
            outcomes_list.append(nash_outcome)

    # Count bid frequencies
    player_elements = [sublist[player_position] for sublist in outcomes_list]
    element_count = {}
    for element in player_elements:
        element_count[element] = element_count.get(element, 0) + 1
    
    return element_count

# Example usage (commented out)
# player_hand = ['6D']
# previous_bids = ['', '', '']
# player_id = 0
# trump = 'H'
# n_players = len(previous_bids)
# root_properties = {'name':'root', 
#                    'score':[0] * n_players,
#                    'trick_end':1, 
#                    'player_id':n_players-1, 
#                    'starting_suit':'', 
#                    'depth':0,
#                    'cards_played_in_trick':[],
#                    'previous_trick_winner':0,
#                    'cards_played':[],
#                    'minmax_score':[]
#                    }  # Define root properties here
# element_count = find_bid(player_hand, previous_bids, trump, player_id, root_properties)
# most_common = max(element_count, key=element_count.get)
# print("Most common bid: {}".format(most_common))
