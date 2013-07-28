from random import shuffle


class CardContainer:
	MAX_SHUFFLES = 10

	###################################
	# INTERFACE #######################
	###################################
	def __init__(self, card_contents = None):
		'''
		Constructor; will create the card list for the deck,
		so child classes should take that into consideration
		'''
		self.card_list = []
		self.cards_by_suit = {}
		self.cards_by_value = {}
		if card_contents is None:
			card_contents = EmptyCardFactory()
		self._populate_deck(card_contents)
	
	def shuffle(self, num_times = 1):
		'''
		Shuffles the deck num_times times. Default is 1, max
		is 10 (if the deck is not fully shuffled after 10 
		shuffles, then something is wrong)
		'''
		i = 0
		while i < num_times and i < CardContainer.MAX_SHUFFLES:
			shuffle(self.card_list)
			i += 1
	
	def num_cards(self):
		'''
		How many cards are in this hand
		'''
		return len(self.card_list)
	
	def empty(self):
		'''
		Returns boolean of whether or not the deck is empty
		'''
		return len(self.card_list) < 1
	
	def top_card(self, peek=False):
		'''
		Returns the top Card. If peek=False, acts as if the card
		has been drawn, removing it from the deck
		'''
		card = self.fetch_card(0, peek)
		if not peek:
			self._remove_card_from_meta_lists(card)
		return card
	
	def bottom_card(self, peek=False):
		'''
		Returns the bottom Card. As with top_card() if peek=False,
		card is removed from the deck
		'''
		card = self.fetch_card(-1, peek)
		if not peek:
			self._remove_card_from_meta_lists(card)
		return card

	def add_card(self, card):
		'''
		Adds a Card to the end of the list of cards in the deck
		'''
		self.card_list.append(card)
		self._add_card_to_meta_lists(card)
	
	def remove_card(self, card):
		'''
		Removes a card from the hand
		'''
		self.card_list.remove(card)
		self._remove_card_from_meta_lists(card)
	
	def fetch_card(self, index, peek=False):
		'''
		Fetches the Card at index. If peek=False, the card is
		removed from the deck. Swallows IndexError if index is
		out of bounds
		'''
		if len(self.card_list) == None:
			return None
		try:
			if peek:
				return self.card_list[index]
			else:
				return self.card_list.pop(index)
		except IndexError:
			return None
	
	def clear(self):
		'''
		Removes all cards from this CardContainer
		'''
		self.card_list = []
		self.cards_by_suit = {}
		self.cards_by_value = {}
	
	def copy_from(self, src_card_container):
		'''
		Copies the entire state from the source CardContainer
		'''
		self.card_list = src_card_container.card_list
		self.cards_by_suit = src_card_container.cards_by_suit
		self.cards_by_value = src_card_container.cards_by_value
	
	###################################
	# PROTECTED METHODS ###############
	###################################
	def _remove_card_from_meta_lists(self, card):
		'''
		Removes a card from the various meta lists of cards
		'''
		if card.suit is not None:
			self.cards_by_suit[card.suit].remove(card)
		self.cards_by_value[card.value].remove(card)
		
	def _add_card_to_meta_lists(self, card):
		'''
		Adds a card to the various meta lists of cards
		'''
		if card.suit is not None:
			if card.suit not in self.cards_by_suit:
				self.cards_by_suit[card.suit] = []
			self.cards_by_suit[card.suit].append(card)

		if card.value not in self.cards_by_value:
			self.cards_by_value[card.value] = []
		self.cards_by_value[card.value].append(card)
	
	def _populate_deck(self, card_contents):
		'''
		Adds all the involved cards to the deck
		'''
		for card in card_contents.get_cards():
			self.add_card(card)

	###################################
	# MAGIC METHODS ###################
	###################################
	def __str__(self):
		return unicode(self)
	
	def __unicode__(self):
		return ", ".join([str(card) for card in self.card_list])
	
	def __len__(self):
		return len(self.card_list)

class AbstractCardFactory:
	def get_cards(self):
		'''
		Function to be overridden by child classes to get the correct
		cards
		'''
		raise NotImplementedError("Must override get_cards() in child classes")

class EmptyCardFactory(AbstractCardFactory):
	def get_cards(self):
		return []

class StandardCardFactory:
	'''
	Defines a standard 52-card deck as used for most card games
	'''
	SUITS = ["spade", "diamond", "heart", "club"]
	VALUES = ["A", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
	def get_cards(self):
		cards = []
		for suit in StandardCardFactory.SUITS:
			for value in StandardCardFactory.VALUES:
				cards.append(Card(suit, value))
		return cards

class Card:
	def __init__(self, suit, value):
		'''
		Basic constructor. Accepts Suit and Value, each of
		which is intended to be a string. None is an
		acceptable value by default; this can be overridden
		'''
		self.suit = suit
		self.value = value

	def __str__(self):
		return unicode(self).encode("utf-8")
	
	def __unicode__(self):
		suit = "None" if self.suit == None else str(self.suit)
		value = "None" if self.value == None else str(self.value)
		return suit + "-" + value

class AbstractPlayer:
	def __init__(self, name):
		'''
		Initializes the player by adding the name; each game's
		'''
		self.hand = CardContainer()
		self.name = name
		self.init_hand()
	
	def init_hand(self):
		'''
		responsible for setting up the player's hand
		'''
		raise NotImplementedError("Must override init_hand() in subclasses")
	
	def draw_card(self, card):
		'''
		adds a card to the user's hand
		'''
		self.hand.add_card(card)
	
	def take_turn(self, *args, **kwargs):
		'''
		Logic on how this player's turn is taken. We don't know what each game
		needs to take a turn, so just allow for a dictionary to be passed
		'''
		raise NotImplementedError("Must override take_turn() in subclasses")
	
	def num_cards_in_hand(self):
		'''
		How many cards in this player's hand
		'''
		return self.hand.num_cards()

class AbstractGameLogic:
	NUM_TIMES_TO_SHUFFLE = 7

	@staticmethod
	def get_starting_message():
		raise NotImplementedError()
	
	@staticmethod
	def get_friendly_name():
		raise NotImplementedError()
	
	def __init__(self):
		self.draw_pile = None
		self.players = []
		self.winner = None
		self._make_cards()
		self.draw_pile.shuffle(self._get_num_times_to_shuffle())
	
	def _make_cards(self):
		raise NotImplementedError()	

	def start_game(self):
		'''
		Begins the game by initializing the players, dealing, and 
		triggering the game loop
		'''
		self._init_players()
		self._deal()
		return self._play_game()

	def _get_num_players(self):
		'''
		Gets the number of players who will be playing this game. By
		default, requests input of the user, but can (and should) be
		overridden if a game has a specific number of players
		'''
		min_num_players = self._get_min_num_players()
		max_num_players = self._get_max_num_players()
		num_players = raw_input("How many players (%d-%d)? " % (min_num_players, max_num_players))
		if not num_players.isdigit() or int(num_players) < min_num_players or int(num_players) > max_num_players:
			print "Invalid number of players, must choose a number between %d and %d" % (min_num_players, max_num_players)
			return self._get_num_players()
		return int(num_players)

	def _init_players(self):
		'''
		Creates as many players as are going to play this game
		'''
		num_players = self._get_num_players()
		i = 0
		while i < num_players:
			i += 1
			name = raw_input("Enter name for player %s: " % str(i))
			player_class = self._get_player_class()
			self.players.append(player_class(name))

	def _next_player(self, current_index, rot_reversed):
		'''
		Finds the next player
		'''
		new_index = (current_index - 1) if rot_reversed else (current_index + 1)
		if new_index < 0:
			new_index = len(self.players) - 1
		elif new_index == len(self.players):
			new_index = 0
		return new_index
	
	def _deal(self):
		'''
		Handle dealing the cards to each user
		'''
		raise NotImplementedError()
		
	def _play_game(self):
		'''
		The core loop of the game. Includes all the turn-based game logic
		'''
		raise NotImplementedError()
	
	def _get_max_num_players(self):
		'''
		Max number of players for the game
		'''
		raise NotImplementedError()
	
	def _get_min_num_players(self):
		'''
		Minimum number of players for the game
		'''
		raise NotImplementedError()
	
	def _get_player_class(self):
		'''
		The class to instantiate for the players
		'''
		raise NotImplementedError()
	
	def _get_num_times_to_shuffle(self):
		'''
		Mundane, but fetches how many times we should shuffle the deck; can be
		overridden
		'''
		return AbstractGameLogic.NUM_TIMES_TO_SHUFFLE

class Game:
	def __init__(self, logic):
		self.logic = logic()
		self.continue_playing = True
	
	def start(self):
		print("\n\n%s\n\n" % self.logic.get_starting_message())
		winner = self.logic.start_game()
		if winner:
			print "Congratulations %s; you're the winner!" % winner.name
		else:
			print "Stalemate!"
				
				
				
				
				
				
				 