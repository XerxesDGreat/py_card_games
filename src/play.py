from games.registry import GameRegistry
from common.common import Game

def play_game():
	game_list = GameRegistry.get_registered_games()
	if len(game_list) < 1:
		print "No games have been registered. Please register some."
		return
	
	while True:
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
			
		while True:
			play_again = raw_input("Would you like to play another game? (y/n) ")
			play_again = play_again.lower()
			if play_again == "n" or play_again == "y":
				break
			print "I'm sorry, %s is not an acceptable response" % play_again
		
		if play_again == "n":
			print "That was fun! Goodbye Dr. Falken!"
			break
		print "\n\n\n\n\n"


if __name__ == "__main__":
	play_game()
