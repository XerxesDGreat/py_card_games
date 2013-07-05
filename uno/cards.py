from random import shuffle, choice

class Deck:
	COLORS = ["r", "b", "g", "y"]
	COLORED_VALUES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, "S","D2", "R"]
	WILD_CARD_VALUES = ["W", "D4"]
	DRAW_CARD_VALUES = ["D4", "D2"]
	SKIP_CARD_VALUES = ["S"]
	REVERSE_CARD_VALUES = ["R"]

	def __init__(self):
		self.card_list = []
	
	def init(self):
		# all the regular, colored cards
		for color in Deck.COLORS:
			for value in Deck.COLORED_VALUES:
				self.add_card(Card({"color": color, "value": value}))
				if value != 0:
					# there are two of each value > 0
					self.add_card(Card({"color": color, "value": value}))
		# special cards; 4 of each
		for value in Deck.WILD_CARD_VALUES:
			i = 0
			while i < 4:
				self.add_card(Card({"value": value}))
				i += 1
	
	def shuffle(self, num_times = 1):
		i = 0
		while i < num_times:
			shuffle(self.card_list)
			i += 1
	
	def empty(self):
		return len(self.card_list) < 1
	
	def top_card(self, peek=False):
		return self.fetch_card(0, peek)
	
	def bottom_card(self, peek=False):
		return self.fetch_card(-1, peek)

	
	def add_card(self, card):
		self.card_list.append(card)
	
	def fetch_card(self, index, peek=False):
		if len(self.card_list) == None:
			return None
		if peek:
			return self.card_list[index]
		else:
			return self.card_list.pop(index)
	
	def __unicode__(self):
		pass
		

class Card:

	def __init__(self, data):
		self.value = data["value"]
		self.setColor(data)
	
	def setColor(self, data):
		if self.is_wild():
			self.color = "None"
			return
		self.color = data["color"]
	
	def is_wild(self):
		return self.value in Deck.WILD_CARD_VALUES
	
	def is_draw(self):
		return self.value in Deck.DRAW_CARD_VALUES
	
	def is_skip(self):
		return self.value in Deck.SKIP_CARD_VALUES
	
	def is_reverse(self):
		return self.value in Deck.REVERSE_CARD_VALUES
	
	def num_draw_cards(self):
		if not self.is_draw():
			return 0
		return 2 if self.value is "D2" else 4
	
	def __str__(self):
		return unicode(self).encode("utf-8")
	
	def __unicode__(self):
		color = "None" if self.color == None else self.color
			
		return color + " " + str(self.value)

class Hand:
	def __init__(self):
		self.cards = []
		self.cards_by_color = {}
		for color in Deck.COLORS:
			self.cards_by_color[color] = []
		self.cards_by_color["None"] = []
		self.wild_cards = []
		self.cards_by_value = {}
		for value in Deck.COLORED_VALUES + Deck.WILD_CARD_VALUES:
			self.cards_by_value[value] = []
	
	def num_cards(self):
		return len(self.cards)
	
	def add_card(self, card):
		self.cards.append(card)
		self.cards_by_color[card.color].append(card)
		if card.is_wild():
			self.wild_cards.append(card)
		self.cards_by_value[card.value].append(card)
	
	def remove_card(self, card):
		self.cards.remove(card)
		self.cards_by_color[card.color].remove(card)
		if card.is_wild():
			self.wild_cards.remove(card)
		self.cards_by_value[card.value].remove(card)
	
	def get_matches(self, card, active_color):
		ret = []
		color = active_color if card.is_wild() else card.color
		all_cards = self.cards_by_color[color] + self.cards_by_value[card.value]
		for card in all_cards:
			# this is inefficient
			if card not in ret:
				ret.append(card)
		return ret
	
	def get_wild_cards(self):
		return self.wild_cards
	
	def get_color_most_owned(self):
		count = 0
		most_owned_color = None
		for color, cards in self.cards_by_color.iteritems():
			if color == None:
				# we don't want the wild card color to override a real color
				continue
			if len(cards) > count:
				count = len(cards)
				most_owned_color = color

		if most_owned_color == None:
			most_owned_color = choice(Deck.COLORS)

		return most_owned_color
	
	def __str__(self):
		return unicode(self).encode("utf-8")

	def __unicode__(self):
		return [(card.color, card.value) for card in self.card]
