from games.registry import GameRegistry
from common.common import Deck, Game
from time import sleep
from sys import stdout

def play_game():
	game_list = GameRegistry.get_registered_games()
	if len(game_list) < 1:
		print "No games have been registered. Please register some."
		return

	print "Please select the game you'd like to play from the following list"
	print "================================================================="
	for i in range(0, (len(game_list))):
		print "  %d) %s" % (i + 1, game_list[i].friendly_name)
	selection = int(raw_input("Selection: "))
	try:
		game = game_list[selection - 1]
	except:
		print "Sorry, %d is an invalid selection. You lose!" % selection
		return
	
	c = Game(game.logic_class)
	c.start()

if __name__ == "__main__":
	play_game()
