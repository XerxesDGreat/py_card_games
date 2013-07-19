__all__ = ["uno", "oldmaid", "registry"]

from registry import GameRegistry
from uno import UnoGameLogic
from oldmaid import OldMaidGameLogic

GameRegistry.register_game(UnoGameLogic)
GameRegistry.register_game(OldMaidGameLogic)
