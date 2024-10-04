import time
import random
import copy
import datetime
import csv

from cards import Cards


class Rikiki(object):
    """
    Runs one full rikiki game
    """	
    # A lot of the game variables can be changed by passing in parameters when starting the auction
    # If nothing is passed in, the default values are used as below 

    def __init__(self, 
            room=[], # List of bots to play in the game
            round_movement='up', # up, down or both
            minmax_size=[1,10], # smallest and largest hand sizes
            hell_bridge=True,
            #output_csv_file="data/game_log.csv",
            verbose=False # Result of every round is logged to csv
            ):

        self.round_movement=round_movement
        # if round_movement is 'up' then number of hands in each round goes from min to max in minmax_size
        # with increases of one card per hand
        # if round_movement is 'down' then number of hands goes from max to min
        # if round_movement is 'both' then number of hands goes from min to max and then back down to min
        self.round_order=[l for l in range(minmax_size[0],minmax_size[1]+1)]
        if self.round_movement=='down':
            self.round_order.reverse()
        elif self.round_movement=="both":
            self.round_order+=self.round_order[::-1][1:]
            
        #initialise variables
        self.current_round=0
        self.bots = []
        self.finished = False
        self.hell_bridge = hell_bridge
        self.cards={}
        self.valid_cards={}
        self.round_start_pos={}
        self.round_history=[]
        self.verbose=verbose

		# Game variables
		
		# Make sure there are at least two bots in the game
        if len(room)>1:
            self.room = room
        else:
            raise TypeError("You need at least two bots in a room, this room only has one bot in it")
		
		# Reset the random seed
        random.seed()
		# Game specific variables         

		# Data export variables
        #self.output_csv_file = output_csv_file
        #self.error_log_csv_file = "data/error_log.csv"
        #self.game_start_time = str(datetime.datetime.now())

		# Start the bots
        self.__initialise_bots()

    def __initialise_bots(self):
        count = 0
        for bot_module in self.room:
            count += 1

			# Initialise the bot
			# Catch any errors here, add them to an error log and raise the error again so it stops the game
            try:
                bot_instance = bot_module.Bot()
            except Exception as e:
                print("Error caught ", str(e))
                self.__log_error(bot_name=bot_module, game_stage="initialisation", error_message=str(e))
                raise

			# The unique id is the bot's name and the bot's number in this auction. 
			# For test bots, you can use a name to remind you which bot is which
			# Adding a number to the bot's name means that you can use the same bot class more than once in an auction 
			# Any errors are caught here, added to an error log and the error is raised again so that it stops the game
			# Errors will be raised here if the bot doesn't have a name variable
            try:
                bot_unique_id = "{}-{}".format(bot_instance.name, count)
            except Exception as e:
                print("Error caught ", str(e))
                self.__log_error(bot_name=bot_module, game_stage="initialisation - bot name", error_message=str(e))
                raise

			# Add bot details to a dictionary. Stores bot instance in memory
			# Also used to keep track of hands won
            new_bot = {
                "bot_instance":bot_instance,
                "bot_name":copy.deepcopy(bot_instance.name),
				"bot_unique_id":bot_unique_id,
				"hands_won":0,
				"aim_hands_won":'',
				"score":0,
                "start_pos":count-1,
                "card_played":"",
				}

			# Add the bot and its details to the bots array
            self.bots.append(new_bot)
            self.cards[bot_unique_id]=[]
            self.valid_cards[bot_unique_id]=[]
            self.round_start_pos[bot_unique_id]=new_bot["start_pos"]
        

	##########################################
	## Running a single round of the game
	##########################################

    def run_game(self):
        while not self.finished:
            
            for round in self.round_order:
                #functions for initialising the round (dealing cards etc.)
                self.__start_round()
                self.__collect_bids()
                self.round_history=[]
                
                #functions for playing cards
                for hand in range(round):
                    self.__play_trick()
                    self.__pick_winner_of_the_hand()
                
                self.__update_scores()
                self.current_round+=1
            
            self.finished=True

            if self.verbose==True:
                lst=[bot["score"] for bot in self.bots]
                winner_position=lst.index(max(lst))
                print("\n")
                print("### WINNER: {} ###".format(self.bots[winner_position]["bot_unique_id"]))


    def __start_round(self):
        # shift starting positions of bots
        for bot in self.bots:
            bot['start_pos']=self.round_start_pos[bot["bot_unique_id"]]  
            
        self.bots =sorted(self.bots, key = lambda k: k['start_pos'])
        
        size=self.round_order[self.current_round]
        #create deck of cards, shuffle them and then deal
        c=Cards()
        c.shuffle()
        
        c.deal(len(self.bots),size)
        
        #keep a record of hands of bots
        for i,bot in enumerate(self.bots):
            self.cards[bot['bot_unique_id']] = c.hands[i]

        #the trump suit is decided by the deal function in the cards class. 
        self.trump = c.trump

        

    def __collect_bids(self):
        #collect bids from bots.
        # each bots gets sent (public) information on the current state of the game and then uses (private) information
        # on their hand to create a bid value.
        self.totbid=0
        for bot in self.bots:
        
        # Build a dictionary of the data we will pass to bots
            info_for_bots = {
    			"current_round_size":self.round_order[self.current_round],
    			"bots":self.bots,
                "trump": self.trump,
                "cards": self.cards[bot['bot_unique_id']],
                "hells_bridge": False,
    		}
            
            if self.round_order[self.current_round]==1 and self.hell_bridge==True:
                all_cards=[self.cards[bot['bot_unique_id']][0] for bot in self.bots]
                all_cards.remove(self.cards[bot['bot_unique_id']][0])
                info_for_bots["cards"]=all_cards
                info_for_bots["hells_bridge"]=True
		# Make a deep copy of the data to pass to bots, so we are not just passing the bot shared references to data
		# Every bot gets data in completely seperate memory so there is no risk of changing data in other bots or the rikiki object
            info_for_bots_deep_copy = copy.deepcopy(info_for_bots)

			# Add this bot's details to the data to pass to the bot, but as a deep copy rather than the actual data  
            info_for_bots_deep_copy["my_bot_details"] = copy.deepcopy(bot)
			
			# If the bot raises an error - catch it, log it and either stop the game or carry on with the bot bidding zero
            try:
                bid = int(bot["bot_instance"].get_bid(**info_for_bots_deep_copy))
            except Exception as e:
                print("Bidding error caught on {} - {}".format(bot["bot_unique_id"], e))
            
            #the last bot to bid has an extra condition to follow.
            if self.bots[-1]['bot_instance']==bot['bot_instance'] and self.totbid+bid==self.round_order[self.current_round]:
                bid=self.round_order[self.current_round]+1-self.totbid
            
            bot["aim_hands_won"]=bid
            #this variable is updated and used in the condition for the final bot
            self.totbid+=bid

        if self.verbose==True:
            print("\n")
            print("### round {} bids ###".format(self.current_round+1))
            print("bots: {}".format([bot["bot_unique_id"] for bot in self.bots]))
            print("bids: {}".format([bot["aim_hands_won"] for bot in self.bots]))
            
    def __play_trick(self):
        #order bots according to postion and get them to play
        self.bots = sorted(self.bots, key=lambda k: k['start_pos'])
        self.round_history.append({})
        
        for bot in self.bots:
            if self.round_order[self.current_round]==1 and self.hell_bridge==True:
                bot["card_played"]=self.cards[bot['bot_unique_id']][0]
            else:
                if bot["start_pos"]==0:
                    self.valid_cards[bot['bot_unique_id']]=self.cards[bot['bot_unique_id']]
                elif bot["start_pos"]==1:
                    self.__valid_card()
                    
                # (public) information to let the bot decide what card to play next.    
                info_for_bots = {
        			"current_round_size":self.round_order[self.current_round],
        			"bots":self.bots,
                    "trump": self.trump,
                    "cards": self.cards[bot['bot_unique_id']],
                    "history": self.round_history,
                    "total_bid": self.totbid,
                    "valid_cards":self.valid_cards[bot['bot_unique_id']]
        		}
                
                
                info_for_bots_deep_copy = copy.deepcopy(info_for_bots)
                info_for_bots_deep_copy["my_bot_details"] = copy.deepcopy(bot)
            

                bot["card_played"] = bot["bot_instance"].play_card(**info_for_bots_deep_copy)
                #need to add in that have to follow starting suit, can only play trump when can't follow suit
            self.round_history[-1][bot["bot_unique_id"]]=bot["card_played"]
            
            self.cards[bot['bot_unique_id']].remove(bot["card_played"])

        
    def __pick_winner_of_the_hand(self):
        #computes which player won the hand.
        values = {"2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "1":10, "J":11, "Q":12, "K":13, "A":14}
        for bot in self.bots:
            if bot["start_pos"]==0:
                current_winner=bot["start_pos"]
                winning_card=bot["card_played"]

            else:
                if bot["card_played"][-1]==winning_card[-1] and values[bot["card_played"][0]]>values[winning_card[0]]:
                    current_winner=bot["start_pos"]
                    winning_card=bot["card_played"]
                elif winning_card[-1]!=self.trump and bot["card_played"][-1]==self.trump:
                    current_winner=bot["start_pos"]
                    winning_card=bot["card_played"]  
        self.bots[current_winner]["hands_won"]+=1

        if self.verbose==True:
            print("\n")
            print("### round {} hand {} summary ###".format(self.current_round+1,sum([bot["hands_won"] for bot in self.bots])))
            print("bots: {}".format([bot["bot_unique_id"] for bot in self.bots]))
            print("trump: {}".format(self.trump))
            print("cards played: {}".format([bot["card_played"] for bot in self.bots]))
            print("WINNER: {}".format(self.bots[current_winner]["bot_unique_id"]))
            print("tricks won: {}".format([bot["hands_won"] for bot in self.bots]))
            print("tricks bid: {}".format([bot["aim_hands_won"] for bot in self.bots]))
        
        for bot in self.bots:
            new_pos=bot["start_pos"]-current_winner
            bot["start_pos"]=new_pos%len(self.room)
            bot["card_played"]=""
        
    def __update_scores(self):
        #updates the scorces and other variables.

        old_scores=[bot["score"] for bot in self.bots]

        for bot in self.bots:
            new_pos = self.round_start_pos[bot["bot_unique_id"]]-1
            self.round_start_pos[bot["bot_unique_id"]]=new_pos%len(self.room)
            
            if bot["hands_won"]==bot["aim_hands_won"]:
                bot["score"]+=10+2*bot["aim_hands_won"]
            else:
                bot["score"]-=2*abs(bot["hands_won"]-bot["aim_hands_won"])

        #print info from round    
        if self.verbose==True:
            print("\n")
            print("### round {} summary ###".format(self.current_round+1))
            print("bots: {}".format([bot["bot_unique_id"] for bot in self.bots] ))
            print("tricks bid: {}".format([bot["aim_hands_won"] for bot in self.bots] ))
            print("tricks won: {}".format([bot["hands_won"] for bot in self.bots] ))
            print("beginning of round scores: {}".format(old_scores))
            print("end of round scores: {}".format([bot["score"] for bot in self.bots]))

        #reset hands
        for bot in self.bots:
            bot['hands_won']=0
            bot['aim_hands_won']=''
                
    def __valid_card(self):
        #checks that the bot plays a card that is in their hand.
        for bot in self.bots[1:]:
            start_bot=self.bots[0]["bot_unique_id"]
            start_suit=self.round_history[-1][start_bot][-1]
            self.valid_cards[bot['bot_unique_id']]=[]
            
            for card in self.cards[bot['bot_unique_id']]:
                if card[-1]==start_suit:
                    self.valid_cards[bot['bot_unique_id']].append(card)
            
            if len(self.valid_cards[bot['bot_unique_id']])==0:
                self.valid_cards[bot['bot_unique_id']]=self.cards[bot['bot_unique_id']]


