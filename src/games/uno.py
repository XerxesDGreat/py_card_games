from common.common import AbstractCardFactory, AbstractGameLogic, AbstractPlayer
from common.common import Card, CardContainer
from random import choice
from time import sleep


def get_game_play_class():
	return UnoGameLogic

class UnoCardFactory(AbstractCardFactory):
	SUITS = ["r", "b", "g", "y"]
	SUITED_VALUES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, "S","D2", "R"]
	WILD_CARD_VALUES = ["W", "D4"]
	DRAW_CARD_VALUES = ["D4", "D2"]
	SKIP_CARD_VALUES = ["S"]
	REVERSE_CARD_VALUES = ["R"]

	def get_cards(self):
		cards = []
		'''
		Create a deck of cards ready for UNO
		'''
		# all the regular, colored cards
		for suit in UnoCardFactory.SUITS:
			for value in UnoCardFactory.SUITED_VALUES:
				cards.append(UnoCard(suit, str(value)))
				if value != 0:
					# there are two of each value > 0
					cards.append(UnoCard(suit, str(value)))
		# special cards; 4 of each
		for value in UnoCardFactory.WILD_CARD_VALUES:
			i = 0
			while i < 4:
				cards.append(UnoCard(None, str(value)))
				i += 1
		return cards
	
class UnoCard(Card):
	def __init__(self, suit, value):
		self.special_state_used = False
		Card.__init__(self, suit, value)
	
	def is_wild(self):
		'''
		Whether this card is wild
		'''
		return self.value in UnoCardFactory.WILD_CARD_VALUES
	
	def is_draw(self):
		'''
		Whether this card is a draw card
		'''
		return self.value in UnoCardFactory.DRAW_CARD_VALUES
	
	def is_skip(self):
		'''
		Whether this card is a skip card
		'''
		return self.value in UnoCardFactory.SKIP_CARD_VALUES
	
	def is_reverse(self):
		'''
		Whether this card is a reverse card
		'''
		return self.value in UnoCardFactory.REVERSE_CARD_VALUES
	
	def num_draw_cards(self):
		'''
		How many cards the next player should draw if this
		card is played
		'''
		if not self.is_draw():
			return 0
		return 2 if self.value is "D2" else 4
	
	def is_match(self, card):
		"""
		Whether the given card matches this card
		"""
		return self.suit == card.suit or self.value == card.value
	
class UnoCardContainer(CardContainer):
	def __init__(self):
		'''
		We also want to create a list of wild cards, so override
		the base constructor
		'''
		self.wild_cards = []
		CardContainer.__init__(self)
	
	def add_card(self, card):
		'''
		Override base functionality to keep wild cards up to date
		'''
		CardContainer.add_card(self, card)
		if card.is_wild():
			self.wild_cards.append(card)
	
	def remove_card(self, card):
		'''
		Override base functionality to keep wild cards up to date
		'''
		CardContainer.remove_card(self, card)
		if card.is_wild():
			self.wild_cards.remove(card)
	
	def get_matches(self, card, active_suit, include_wild = True):
		'''
		Retrieves a list of all the cards which match the
		provided card.  Also provide the active_suit in case the
		card provided is wild
		'''
		ret = []
		suit = active_suit if card.is_wild() else card.suit
		all_cards = self.cards_by_suit.get(suit, []) + self.cards_by_value.get(card.value, [])
		if include_wild:
			all_cards = all_cards + self.wild_cards
		for card in all_cards:
			# this is inefficient
			if card not in ret:
				ret.append(card)
		return ret
	
	def get_suit_most_owned(self):
		'''
		Gets the suit of which there are the most cards in this hand. If it
		happens that there are no suited cards, pick a suit at random
		'''
		count = 0
		most_owned_suit = None
		for suit, cards in self.cards_by_suit.iteritems():
			if suit == None:
				# we don't want the wild card suit to override a real suit
				continue
			if len(cards) > count:
				count = len(cards)
				most_owned_suit = suit

		if most_owned_suit == None:
			most_owned_suit = choice(UnoCardFactory.SUITS)

		return most_owned_suit

class UnoPlayer(AbstractPlayer):
	def init_hand(self):
		'''
		Override base functionality to create an UnoHand
		'''
		self.hand = UnoCardContainer()
	
	def determine_best_match(self, card, active_suit):
		'''
		Determines what the best match is for the given card and suit
		'''
		matches = self.hand.get_matches(card, active_suit)
		if len(matches) > 0:
			return choice(matches)
		return None
	
	def take_turn(self, **kwargs):
		game_logic = kwargs.get("game_logic", "hello")
		active_card = game_logic.discard_pile.bottom_card(True)
		chosen_card = None
		while chosen_card is None:
			if len(self.hand.get_matches(active_card, game_logic.active_suit)) > 0:
				chosen_card = self.determine_best_match(active_card, game_logic.active_suit)
			else:
				self._prompt_draw(game_logic)
			
		self.hand.remove_card(chosen_card)
		game_logic.discard_pile.add_card(chosen_card)
		if chosen_card.is_wild():
			print "You played a wild card; please choose a suit!"
			new_suit = self._get_choice_in_list(UnoCardFactory.SUITS)
		else:
			new_suit = chosen_card.suit
			
		return (chosen_card, new_suit)
	
	def _prompt_draw(self, game_logic):
		'''
		prompts the user to draw. Basically, any input will do it
		'''
		game_logic.update_draw_pile()
		card = game_logic.draw_pile.top_card()
		self.hand.add_card(card)
		print("You have no matches for the top card in your hand; drew %s" % card)
		
	def _get_choice_in_list(self, selection_list):
		'''
		Displays a list of cards for the user and prompts them for a selection
		'''
		selection = self.hand.get_suit_most_owned()
		print "%s selected" % selection
		return selection
	
	def _validate_card_match(self, chosen_card, active_card, active_suit):
		"""
		Ensures that chosen_card is an acceptable match, given the active_card
		and active_suit
		"""
		return chosen_card.is_match(active_card) or chosen_card.suit == active_suit

class UnoRealPlayer(UnoPlayer):
	
	def _prompt_draw(self, game_logic):
		'''
		prompts the user to draw. Basically, any input will do it
		'''
		raw_input("You have no matches for the top card in your hand; hit enter to draw")
		game_logic.update_draw_pile
		self.hand.add_card(game_logic.draw_pile.top_card())
		
	def determine_best_match(self, active_card, active_suit):
		'''
		prompts the user to select a card to play
		'''
		chosen_card = None
		while chosen_card is None:
			print "Card to match is %s" % active_card
			if active_card.is_wild():
				print "Suit to match is %s" % active_suit
			print "Your cards: "
			chosen_card = self._get_choice_in_list(self.hand.cards)
			
			if not self.validate_card_match(chosen_card, active_card, active_suit):
				chosen_card = None
		return chosen_card


class UnoGameLogic(AbstractGameLogic):
	NUM_CARDS = 7
	MAX_PLAYERS = 10
	MIN_PLAYERS = 2

	def __init__(self):
		AbstractGameLogic.__init__(self)
	
	def update_draw_pile(self):
		if self.draw_pile.empty():
			print "***************************\nFLIPPING DISCARD AND SHUFFLING\n***************************\n"
			sleep(1)
			tmp = self.discard_pile
			self.discard_pile = self.draw_pile
			self.draw_pile = tmp
			self.draw_pile.shuffle()
			self.discard_pile.add_card(self.draw_pile.top_card())
	
	@staticmethod
	def get_friendly_name():
		return "Uno!"
	
	@staticmethod
	def get_starting_message():
		return '''
  UUUUUUUU     UUUUUUUUNNNNNNNN        NNNNNNNN     OOOOOOOOO      !!! 
  U::::::U     U::::::UN:::::::N       N::::::N   OO:::::::::OO   !!:!!
  U::::::U     U::::::UN::::::::N      N::::::N OO:::::::::::::OO !:::!
  UU:::::U     U:::::UUN:::::::::N     N::::::NO:::::::OOO:::::::O!:::!
   U:::::U     U:::::U N::::::::::N    N::::::NO::::::O   O::::::O!:::!
   U:::::D     D:::::U N:::::::::::N   N::::::NO:::::O     O:::::O!:::!
   U:::::D     D:::::U N:::::::N::::N  N::::::NO:::::O     O:::::O!:::!
   U:::::D     D:::::U N::::::N N::::N N::::::NO:::::O     O:::::O!:::!
   U:::::D     D:::::U N::::::N  N::::N:::::::NO:::::O     O:::::O!:::!
   U:::::D     D:::::U N::::::N   N:::::::::::NO:::::O     O:::::O!:::!
   U:::::D     D:::::U N::::::N    N::::::::::NO:::::O     O:::::O!!:!!
   U::::::U   U::::::U N::::::N     N:::::::::NO::::::O   O::::::O !!! 
   U:::::::UUU:::::::U N::::::N      N::::::::NO:::::::OOO:::::::O     
    UU:::::::::::::UU  N::::::N       N:::::::N OO:::::::::::::OO  !!! 
      UU:::::::::UU    N::::::N        N::::::N   OO:::::::::OO   !!:!!
        UUUUUUUUU      NNNNNNNN         NNNNNNN     OOOOOOOOO      !!!'''
	
	def _get_min_num_players(self):
		return UnoGameLogic.MIN_PLAYERS

	def _get_max_num_players(self):
		return UnoGameLogic.MAX_PLAYERS
	
	def _get_player_class(self):
		return UnoPlayer

	def _make_cards(self):
		self.draw_pile = CardContainer(UnoCardFactory())
		self.discard_pile = CardContainer()

	
	def _deal(self):
		i = 0
		while i < UnoGameLogic.NUM_CARDS:
			for player in self.players:
				card = self.draw_pile.top_card()
				player.draw_card(card)
			i += 1
	
	def _play_game(self):
		self._flip_draw_card()
		move_count = 0
		player_index = 0
		rot_reversed = False
		self.active_suit = self.discard_pile.bottom_card(True).suit

		while self.winner == None:
			msg = ""
			player = self.players[player_index]
			starting_cards = player.num_cards_in_hand()
			old_active_suit = self.active_suit

			turn_args = {"game_logic": self}
			print player.hand
			card_played, self.active_suit = player.take_turn(**turn_args)
			move_count += 1

			msg += "Player %s played %s and has " % (player.name, str(card_played))

			ending_cards = player.num_cards_in_hand()
			cards_drawn = ending_cards - starting_cards + 1

			msg += "%d cards remaining! " % ending_cards

			if cards_drawn > 0:
				msg += "cards drawn: %d! " % cards_drawn

			if card_played.is_skip():
				print "Skip played!"
				player_index = self._next_player(player_index, rot_reversed)
			elif card_played.is_draw():
				draw_player = self.players[self._next_player(player_index, rot_reversed)]
				# if card is a draw, we draw and don't get to play
				print "Draw played! %s is taking %d cards" % (draw_player.name, card_played.num_draw_cards())
				num_cards_drawn = 0
				while num_cards_drawn < card_played.num_draw_cards():
					self.update_draw_pile()
					draw_player.draw_card(self.draw_pile.top_card())
					num_cards_drawn += 1
				player_index = self._next_player(player_index, rot_reversed)
			elif card_played.is_reverse():
				print "Reverse played!"
				rot_reversed = not rot_reversed

			if self.active_suit != old_active_suit:
				msg += "New suit: %s" % self.active_suit
			print (msg)
			if player.num_cards_in_hand() == 1:
				print "========= Player %s has UNO! =========" % player.name
			if player.num_cards_in_hand() == 0:
				self.winner = player
				break

			player_index = self._next_player(player_index, rot_reversed)
		return self.winner
	
	def _flip_draw_card(self):
		self.discard_pile.add_card(self.draw_pile.top_card())
		print "new card on discard pile: " + str(self.discard_pile.bottom_card(True))