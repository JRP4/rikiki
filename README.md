# rikiki

An application to play the card game Rikiki (also known as oh hell! or contract whist).
During the summer of 2020 (under a COVID lockdown) I was taught this game by a housemate, we played it in a group of 3 or 4 every evening.
This project was designed as an aid to winning against my housemates by getting algorithmic assitance and eventually (due to their annoyance) as a training aid.
There is a dual purpose to this project: the first purpose is an implementation of the card game and the second purpose is to develop an algorithm (in the form of a bot) to play as well as possible.

A modification to the rules of Rikiki that I cannot find anywhere on the internet but I played with my housemates is the 'hells bridge' round. 
It is a change to the round of one card in which you have to bid without having seen your card.
Whether or not the 'hells bridge' change should be part of the game structure is an option in the game setup.

## Structure
An implementation of the game is in the 'rikiki.py' file.
The 'arena.py' file shows how to play a game with a human player and a couple of basic bots.
The human player prompts the user for what bid or card to play next.
'cards.py' is a deck of cards class.