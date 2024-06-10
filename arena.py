
# Import the rikiki game environemnt, to run the games
from rikiki import Rikiki

# Import some bots to play with
from bots import human, basic_bot, basic_bot_v2

room = [human,basic_bot,basic_bot_v2]

# Setup the game
my_game = Rikiki(room=room, round_movement='up',minmax_size=[2,7],hell_bridge=True,verbose=True)

my_game.run_game()

