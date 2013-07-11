class RegisteredGame:
	def __init__(self, logic_class):
		self.logic_class = logic_class
	
	@property
	def friendly_name(self):
		return self.logic_class.get_friendly_name()

class GameRegistry:
	registered_games = []

	def __init__(self):
		raise Exception("Must use this class statically")
	
	@staticmethod
	def register_game(logic_class):
		GameRegistry.registered_games.append(RegisteredGame(logic_class))
	
	@staticmethod
	def get_registered_games():
		return GameRegistry.registered_games
