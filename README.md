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

## To-do list
This project is not complete, below is a list of programs still to be written:
- Incoorporate the Monte-Carlo Tree Search (MCTS) algorithm.
An adjustment needs to be made due to the lack of information a player has about the card their oppenent holds.
This algorithm will be the basis of both the bidding and card choosing functions.
A mechanism for adaptive play needs to be created.
For example if an oppenent expected to win with a certain card and did not then their strategy may change - this is obvious to human players and thus the MCTS needs to be modified to compensate for this.
- Another algorithmic approach to try is Counterfactual Regret Minimisation (CRM) as it is designed from the ground up to cope with imperfect information. CRM has found success in poker bots, which if anything is more complicated than Rikiki.
