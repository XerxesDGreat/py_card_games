import games
from common.common import Deck
from time import sleep
from sys import stdout

if __name__ == "__main__":
	game_list = games.get_available_games()
	print "Please select the game you'd like to play from the following list"
	print "================================================================="
	for i in range(0, (len(game_list))):
		(friendly_name, module_name) = game_list[i]
		print "  %d) %s" % (i + 1, friendly_name)
	selection = int(raw_input("Selection: "))
	try:
		game = game_list[selection - 1]
	except:
		print "Sorry, %d is an invalid selection. You lose!" % selection
		exit()
	
	(friendly_name, module_name) = game
	to_import = "games.%s" % module_name
	module = __import__("games.%s" % module_name, fromlist=["games"])
	game_play_class = module.get_game_play_class()
	c = game_play_class()
	print("")
	print("")
	c.print_starting_message()
	print("")
	print("")
	c.start_game()
