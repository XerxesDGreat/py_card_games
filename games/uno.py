from common.common import *
from time import sleep
from sys import stdout

def get_game_play_class():
	return UnoGamePlay

class UnoCardContainer(AbstractCardContainer):
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
		for suit in UnoCardContainer.SUITS:
			for value in UnoCardContainer.SUITED_VALUES:
				cards.append(UnoCard(suit, str(value)))
				if value != 0:
					# there are two of each value > 0
					cards.append(UnoCard(suit, str(value)))
		# special cards; 4 of each
		for value in UnoCardContainer.WILD_CARD_VALUES:
			i = 0
			while i < 4:
				cards.append(UnoCard(None, str(value)))
				i += 1
		return cards
	
class UnoCard(Card):
	def is_wild(self):
		'''
		Whether this card is wild
		'''
		return self.value in UnoCardContainer.WILD_CARD_VALUES
	
	def is_draw(self):
		'''
		Whether this card is a draw card
		'''
		return self.value in UnoCardContainer.DRAW_CARD_VALUES
	
	def is_skip(self):
		'''
		Whether this card is a skip card
		'''
		return self.value in UnoCardContainer.SKIP_CARD_VALUES
	
	def is_reverse(self):
		'''
		Whether this card is a reverse card
		'''
		return self.value in UnoCardContainer.REVERSE_CARD_VALUES
	
	def num_draw_cards(self):
		'''
		How many cards the next player should draw if this
		card is played
		'''
		if not self.is_draw():
			return 0
		return 2 if self.value is "D2" else 4
	
class UnoHand(Hand):
	def __init__(self):
		'''
		We also want to create a list of wild cards, so override
		the base constructor
		'''
		Hand.__init__(self)
		self.wild_cards = []
	
	def add_card(self, card):
		'''
		Override base functionality to keep wild cards up to date
		'''
		Hand.add_card(self, card)
		if card.is_wild():
			self.wild_cards.append(card)
	
	def remove_card(self, card):
		'''
		Override base functionality to keep wild cards up to date
		'''
		Hand.remove_card(self, card)
		if card.is_wild():
			self.wild_cards.remove(card)
	
	def get_matches(self, card, active_suit):
		'''
		Retrieves a list of all the non-wild cards which match the
		provided card.  Also provide the active_suit in case the
		card provided is wild
		'''
		ret = []
		suit = active_suit if card.is_wild() else card.suit
		all_cards = self.cards_by_suit.get(suit, []) + self.cards_by_value.get(card.value, [])
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
			most_owned_suit = choice(Deck.COLORS)

		return most_owned_suit
	
	def __str__(self):
		return unicode(self).encode("utf-8")

	def __unicode__(self):
		return [(card.suit, card.value) for card in self.card]

class UnoPlayer(AbstractPlayer):
	def init_hand(self):
		'''
		Override base functionality to create an UnoHand
		'''
		self.hand = UnoHand()
	
	def determine_best_match(self, card, active_suit):
		'''
		Determines what the best match is for the given card and suit
		'''
		matches = self.hand.get_matches(card, active_suit)
		if len(matches) > 0:
			return choice(matches)
		if len(self.hand.wild_cards) > 0:
			return choice(self.hand.wild_cards)
		return None

	def take_turn(self, **kwargs):
		'''
		Implement how a turn is taken in Uno, ensuring all the values
		are in the args
		'''
		discard_pile = kwargs.get("discard_pile", "hello")
		active_suit = kwargs.get("active_suit", "goodbye")
		draw_pile = kwargs.get("draw_pile", "asdf")

		active_card = discard_pile.bottom_card(True)

		match = self.determine_best_match(active_card, active_suit)
		while match == None:
			if draw_pile.empty():
				break;
			self.hand.add_card(draw_pile.top_card())
			match = self.determine_best_match(active_card, active_suit)
		
		self.hand.remove_card(match)
		discard_pile.add_card(match)
		new_suit = match.suit
		if match.is_wild():
			new_suit = self.hand.get_suit_most_owned()
		return (match, new_suit)


class UnoGamePlay(AbstractGamePlay):
	NUM_CARDS = 7
	MAX_PLAYERS = 10
	MIN_PLAYERS = 2

	def __init__(self):
		self.draw_pile = None
		self.discard_pile = None
		self.players = []
		self.cards_initialized = False
		self.winner = None
		self._make_cards()
		self.draw_pile.shuffle(self._get_num_times_to_shuffle())
	
	def print_starting_message(self):
		print "===================================================="
		print "=                                                  ="
		print "=      UU    UU    NN   NN      OOOO     !!!!      ="
		print "=      UU    UU    NNN  NN     OO  OO    !!!!      ="
		print "=      UU    UU    NNNN NN    OO    OO   !!!!      ="
		print "=      UU    UU    NN NNNN    OO    OO    !!       ="
		print "=       UU  UU     NN  NNN     OO  OO              ="
		print "=        UUUU      NN   NN      OOOO      !!       ="
		print "=                                                  ="
		print "===================================================="
	
	def _get_min_num_players(self):
		return UnoGamePlay.MIN_PLAYERS

	def _get_max_num_players(self):
		return UnoGamePlay.MAX_PLAYERS
	
	def _get_player_class(self):
		return UnoPlayer

	def _make_cards(self):
		if self.cards_initialized:
			return
		self.draw_pile = Deck(UnoCardContainer())
		self.discard_pile = Deck(EmptyCardContainer())

	
	def _deal(self):
		i = 0
		while i < UnoGamePlay.NUM_CARDS:
			for player in self.players:
				card = self.draw_pile.top_card()
				player.draw_card(card)
			i += 1
	
	def _play_game(self):
		self._flip_draw_card()
		move_count = 0
		player_index = 0
		reversed = False
		active_suit = self.discard_pile.bottom_card(True).suit

		while self.winner == None:
			msg = ""
			player = self.players[player_index]
			starting_cards = player.num_cards()
			old_active_suit = active_suit

			turn_args = {
				"discard_pile": self.discard_pile,
				"draw_pile": self.draw_pile,
				"active_suit": active_suit
			}
			card_played, active_suit = player.take_turn(**turn_args)
			move_count += 1

			msg += "Player %s played %s and has " % (player.name, str(card_played))

			ending_cards = player.num_cards()
			cards_drawn = ending_cards - starting_cards + 1

			msg += "%d cards remaining! " % ending_cards

			if cards_drawn > 0:
				msg += "cards drawn: %d! " % cards_drawn

			if card_played.is_skip():
				msg +="skip played! "
				player_index = self._next_player(player_index, reversed)

			if card_played.is_reverse():
				msg += "reverse played! "
				reversed = not reversed

			if card_played.is_draw():
				msg += "draw played! "
				player_index = self._next_player(player_index, reversed) 
				num_cards_drawn = 0
				while num_cards_drawn < card_played.num_draw_cards():
					self.players[player_index].draw_card(self.draw_pile.top_card())
					num_cards_drawn += 1

			if active_suit != old_active_suit:
				msg += "New suit: %s" % active_suit
			print (msg)
			if player.num_cards() == 1:
				print "========= Player %s has UNO! =========" % player.name
			if player.num_cards() == 0:
				self.winner = player

			player_index = self._next_player(player_index, reversed)	
		
			sleep(.25)

		print "Winner is %s! Congratulations!" % self.winner.name
	
	def _flip_draw_card(self):
		self.discard_pile.add_card(self.draw_pile.top_card())
		print "new card on discard pile: " + str(self.discard_pile.bottom_card(True))
	
	def _next_player(self, current_index, reversed):
		new_index = (current_index - 1) if reversed else (current_index + 1)
		if new_index < 0:
			new_index = len(self.players) - 1
		elif new_index == len(self.players):
			new_index = 0
		return new_index
