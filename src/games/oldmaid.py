from common.common import AbstractGameLogic, AbstractPlayer
from common.common import Card, CardContainer, StandardCardFactory
from time import sleep

def get_game_play_class():
	return OldMaidGameLogic

class OldMaidCard(Card):
	pass

class OldMaidCardFactory(StandardCardFactory):
	def get_cards(self):
		cards = StandardCardFactory.get_cards(self)
		cards_to_remove = []
		for card in cards:
			if card.value == "Q":
				cards_to_remove.append(card)
				if len(cards_to_remove) == 3:
					break;
		for card_to_remove in cards_to_remove:
			print card_to_remove
			cards.remove(card_to_remove)
		return cards	
	
class OldMaidPlayer(AbstractPlayer):
	def __init__(self, name):
		AbstractPlayer.__init__(self, name)
		self.had_matches = False

	def init_hand(self):
		self.hand = CardContainer()
		self.discard = CardContainer()
	
	def discard_pairs(self):
		'''
		discards any instance of pairs
		'''
		for value, cards in self.hand.cards_by_value.items():
			while len(cards) > 1:
				self.had_matches = True
				cards_to_remove = cards[-2:]
				for card in cards_to_remove:
					print "removing %s" % str(card)
					self.hand.remove_card(card)
					self.discard.add_card(card)


	def take_turn(self, **kwargs):
		'''
		Implement how a turn is taken in OldMaid, ensuring all the values
		are in the args
		'''
		draw_from_player = kwargs.get("draw_from_player", None)
		if not draw_from_player:
			raise ValueError("Need to pass a player object in 'draw_from_player'")

		draw_from_player.hand.shuffle()
		card = draw_from_player.hand.top_card()
		print "drew a %s" % str(card)
		self.hand.add_card(card)
		self.discard_pairs()


class OldMaidGameLogic(AbstractGameLogic):
	@staticmethod
	def get_friendly_name():
		return "Old Maid"

	@staticmethod	
	def get_starting_message():
		msg = '''
  _______  _        ______     _______  _______ _________ ______  
  (  ___  )( \      (  __  \   (       )(  ___  )\__   __/(  __  \ 
  | (   ) || (      | (  \  )  | () () || (   ) |   ) (   | (  \  )
  | |   | || |      | |   ) |  | || || || (___) |   | |   | |   ) |
  | |   | || |      | |   | |  | |(_)| ||  ___  |   | |   | |   | |
  | |   | || |      | |   ) |  | |   | || (   ) |   | |   | |   ) |
  | (___) || (____/\| (__/  )  | )   ( || )   ( |___) (___| (__/  )
  (_______)(_______/(______/   |/     \||/     \|\_______/(______/ '''
		return msg
	
	def _get_min_num_players(self):
		return 2

	def _get_max_num_players(self):
		return 8 
	
	def _get_player_class(self):
		return OldMaidPlayer

	def _make_cards(self):
		self.draw_pile = CardContainer(OldMaidCardFactory())

	
	def _deal(self):
		while len(self.draw_pile) > 0:
			for player in self.players:
				# we are likely to reach the end of the deck sometime in
				# this loop, not when dealing with the "while" loop;
				# we have to check again :-(
				if len(self.draw_pile) == 0:
					break;
				player.draw_card(self.draw_pile.top_card())

		for player in self.players:
			player.discard_pairs()
			cl = []
			for card in player.hand.card_list:
				cl.append(str(card))
			print ", ".join(cl)
			

	def _play_game(self):
		player_index = 0
		self.turns_without_matches = 0

		while self.winner is None:
			player = self.players[player_index]
			print "=========\n%s's turn" % player.name
			if player.num_cards_in_hand() == 0:
				print "no cards left, skipping\n===========\n"
				player_index = self._next_player(player_index, False)
				continue

			draw_from_index = player_index
			draw_from_player = None
			while draw_from_player is None:
				draw_from_index = self._next_player(draw_from_index, False)
				if draw_from_index == player_index:
					# we've gone around the table
					break
	
				if self.players[draw_from_index].num_cards_in_hand() > 0:
					draw_from_player = self.players[draw_from_index]

			if draw_from_player != None:
				print "drawing from %s" % draw_from_player.name
				player.take_turn(draw_from_player=draw_from_player)
				if player.had_matches:
					self.turns_without_matches = 0
					player.had_matches = False
				else:
					self.turns_without_matches += 1

			self.winner = self._check_for_game_completion()

			player_index = self._next_player(player_index, False)
			print "left with %d cards\n========\n" % player.num_cards_in_hand()
			sleep(.25)

		return self.winner
	
	def _check_for_game_completion(self):
		'''
		Checks for game completion. If the game is complete (meaning only one
		card is left in play and it is the Old Maid), return the winner
		'''
		winner = None
		if self.turns_without_matches > 3 * len(self.players):
			return winner

		if self._num_cards_in_play() == 1:
			for player in self.players:
				if player.num_cards_in_hand() == 1:
					winner = player
					break
		return winner

	def _num_cards_in_play(self):
		'''
		Determines how many total cards are in the players' hands
		'''
		num_cards_in_play = 0
		for player in self.players:
			num_cards_in_play += player.num_cards_in_hand()
		return num_cards_in_play
