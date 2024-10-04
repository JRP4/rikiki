
# Import the rikiki game environemnt, to run the games
from rikiki import Rikiki

# Import some bots to play with
from bots import human, basic_bot, basic_bot_v2, NE_bot

room = [NE_bot,basic_bot]

# Setup the game
my_game = Rikiki(room=room, round_movement='both',minmax_size=[4,5],hell_bridge=False,verbose=True)

my_game.run_game()


