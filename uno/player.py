from cards import Deck, Hand
from random import choice

class Player:
	def __init__(self, name):
		self.hand = Hand()
		self.name = name
	
	def draw_card(self, card):
		self.hand.add_card(card)
	
	def determine_best_match(self, card, active_color):
		matches = self.hand.get_matches(card, active_color)
		if len(matches) > 0:
			return choice(matches)
		wild_cards = self.hand.get_wild_cards()
		if len(wild_cards) > 0:
			return choice(wild_cards)
		return None

	def take_turn(self, discard_pile, draw_pile, active_color):
		active_card = discard_pile.bottom_card(True)

		match = self.determine_best_match(active_card, active_color)
		while match == None:
			if draw_pile.empty():
				break;
			self.hand.add_card(draw_pile.top_card())
			match = self.determine_best_match(active_card, active_color)
		
		self.hand.remove_card(match)
		discard_pile.add_card(match)
		new_color = match.color
		if match.is_wild():
			new_color = self.hand.get_color_most_owned()
		return (match, new_color)
	
	def num_cards(self):
		return self.hand.num_cards()

