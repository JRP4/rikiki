# rikiki

An application to play the card game Rikiki (also known as oh hell! or contract whist).
The rules can be easily be found online, such as here: https://rikiki.endrekadas.com/#/rules

During the summer of 2020 (under a COVID lockdown) I was taught this game by a housemate, we played it in a group of 3 or 4 every evening.
This project was designed as an aid to winning against my housemates in Rikiki using algorithmic assitance.
There is a dual purpose to this project: the first purpose is an implementation of the card game so that you don't need a deck of cards (or friends) to play, and the second purpose is to develop an algorithm (in the form of a bot) to play as well as possible.

Currently only the first purpose is complete.
There are a couple of bots, following a very basic set of rules, that a human player can play against.

A modification to the rules of Rikiki that I played with my housemates is the 'hells bridge' round. 
It is a change to the round of one card in which you cannot see your own card but can see everyone elses' (in-person this is achieved by everyone putting their card in-front of their forehead).
Whether or not the 'hells bridge' change should be part of the game structure is an option in the game setup, but it can only affect the round of one card.

## Structure
An implementation of the game is in the `rikiki.py` file.
The `arena.py` file shows how to play a game with a human player and a couple of basic bots.
The human player prompts the user for what bid or card to play next.
`cards.py` is a deck of cards class.

There are a couple of bots that play according to very simple rules `basic_bot.py` and `basic_bot_v2.py`.
You can also play using manual imputs by selecting one of the bots to be `human.py`. For this bot you are given a larger amount of information, which you can use to play along yourself and try to win against various bots.

The majority of the code in this reposity is dedicated to the so-called NE_bot. NE stands for Nash Equilibrum which is a concept this bot uses to make optimal decisions. Bots have two tasks: the first is to come up with an appropriate bid using the knowledge of their cards. The second is to play cards optimally, in this situation bots have knowledge of their cards, the bids of all bots and previously played cards. The challenge is using information on the bids of oppenents to plan your strategy. The algorithms are found in `NE_bid_bot.py` and `NE_card_bot.py` respectively. Below is a summary of the methods in each file:

### NE_card_bot
The NE_card_bot uses a Nash Equilibrium approach to determine the best card to play in a given situation. Here's a summary of its method:

Monte Carlo Simulation: The bot runs multiple simulations (default 1000) to account for different possible game states.
Hand Generation: For each simulation, it generates possible hands for opponents based on known information and remaining cards.
Game Tree Creation: It creates a full game tree for each simulation using the create_full_tree function, representing all possible future game states.
Nash Equilibrium Calculation: The find_nash_scores function calculates Nash Equilibrium scores for each node in the game tree, starting from the leaves and moving up to the root.
Action Scoring: The bot accumulates scores for each possible action (card to play) across all simulations.
Best Action Selection: It chooses the action with the highest accumulated score as the best card to play.

#### Key functions:

`find_nash_scores`: Calculates Nash Equilibrium scores for the game tree.
`get_root_action_scores`: Extracts scores for each possible action from the root of the tree.
`find_best_action`: Accumulates scores across simulations and finds the best overall action.
`find_best_action_overall`: Orchestrates the entire process, including simulation and score calculation.

### NE_bid_bot
The NE_bid_bot uses a similar Nash Equilibrium approach to determine the optimal bid. Here's a summary of its method:

Monte Carlo Simulation: Like the card bot, it runs multiple simulations to account for different possible game states.
Hand Generation: For each simulation, it generates possible hands for opponents.
Game Tree Creation: It creates a full game tree for each simulation, representing all possible future game states.
Nash Equilibrium Calculation: The find_nash_bids function calculates Nash Equilibrium bids for each node in the game tree.
Bid Frequency Calculation: The bot counts the frequency of each possible bid across all simulations.
Best Bid Selection: It chooses the most frequent bid as the optimal bid.

#### Key functions:

`create_full_tree`: Builds the game tree for a given game state.
`find_nash_bids`: Calculates Nash Equilibrium bids for the game tree.
`modify_list`: Introduces some randomness to the bids to account for imperfect play.
`find_bid`: Orchestrates the entire process, including simulation and bid calculation.

Both bots use helper functions like `valid_card_finder` and `refine_choices` to ensure that only legal moves are considered and to optimize the decision-making process.
The main difference between the two bots is their objective: `NE_card_bot` aims to choose the best card to play, while `NE_bid_bot` focuses on making the optimal bid at the start of a round.

## To-do list
This project is not complete, below is a list of programs still to be written:
- Improve the efficency of the NE_bot. One of the downsides of a Nash Equilibrium (NE) method is that the entire state space has to be searched, for large hand sizes this is computationally intensive. There are many ways to improve the efficency of the search such as: minimising replication, using heuristic-based search algorithms to only look in more promising areas of the state space and tranforming the problem.
- Improve methods. I can still easily beat the NE_bot so there are clearly ways that it can be improved. Investigating methods uses in other card games might provide insights. But of couse part of the fun is coming up with these ideas on your own and trying them out!
