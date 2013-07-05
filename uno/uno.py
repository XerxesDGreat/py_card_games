import cards
import player
from time import sleep
from sys import stdout

class Game:
	NUM_CARDS = 7
	def __init__(self):
		self.draw_pile = None
		self.discard_pile = None
		self.players = []
		self.cards_initialized = False
		self.winner = None

	def prepare_game(self):
		self.make_cards()
		self.draw_pile.shuffle(7)
	
	def make_cards(self):
		if self.cards_initialized:
			return
		self.draw_pile = cards.Deck()
		self.draw_pile.init()
		self.discard_pile = cards.Deck()

	def start_game(self):
		num_players = self.get_num_players()
		self.add_players(num_players)
		self.deal()
		self.play_game()
	
	def add_players(self, num_players):
		i = 0
		while i < num_players:
			i += 1
			name = raw_input("Enter name for player %s: " % str(i))
			self.players.append(player.Player(name))
	
	def deal(self):
		i = 0
		while i < Game.NUM_CARDS:
			for player in self.players:
				card = self.draw_pile.top_card()
				player.draw_card(card)
			i += 1
	
	def show_hands(self):
		i = 0
		for player in self.players:
			print "Cards for player " + str(i)
			for card in player.hand.cards:
				print card
			i += 1
			print ""
	
	def get_num_players(self):
		num_players = int(raw_input("How many players (2-4)? "))
		if num_players < 2 or num_players > 4:
			print "Invalid number of players, must choose a number between 2 and 4"
			return self.get_num_players()
		return num_players
	
	def play_game(self):
		self.flip_draw_card()
		move_count = 0
		player_index = 0
		reversed = False
		active_color = self.discard_pile.bottom_card(True).color

		while self.winner == None:
			msg = ""
			player = self.players[player_index]
			starting_cards = player.num_cards()
			old_active_color = active_color

			card_played, active_color = player.take_turn(self.discard_pile, self.draw_pile, active_color)
			move_count += 1

			msg += "Player %s played %s and has " % (player.name, str(card_played))

			ending_cards = player.num_cards()
			cards_drawn = ending_cards - starting_cards + 1

			msg += "%d cards remaining! " % ending_cards

			if cards_drawn > 0:
				msg += "cards drawn: %d! " % cards_drawn

			if card_played.is_skip():
				msg +="skip played! "
				player_index = self.next_player(player_index, reversed)

			if card_played.is_reverse():
				msg += "reverse played! "
				reversed = not reversed

			if card_played.is_draw():
				msg += "draw played! "
				next_player = self.next_player(player_index, reversed) 
				num_cards_drawn = 0
				while num_cards_drawn < card_played.num_draw_cards():
					self.players[next_player].draw_card(self.draw_pile.top_card())
					num_cards_drawn += 1

			if active_color != old_active_color:
				msg += "New color: %s" % active_color
			print (msg)
			if player.num_cards() == 1:
				print "========= Player %s has UNO! =========" % player.name
			if player.num_cards() == 0:
				self.winner = player

			player_index = self.next_player(player_index, reversed)	
		
			sleep(1)

		print "Winner is %s! Congratulations!" % self.winner.name
	
	def flip_draw_card(self):
		self.discard_pile.add_card(self.draw_pile.top_card())
		print "new card on discard pile: " + str(self.discard_pile.bottom_card(True))
	
	def next_player(self, current_index, reversed):
		new_index = (current_index - 1) if reversed else (current_index + 1)
		if new_index < 0:
			new_index = len(self.players) - 1
		elif new_index == len(self.players):
			new_index = 0
		return new_index
		
		

if __name__ == "__main__":
	c = Game()
	c.prepare_game()
	c.start_game()
