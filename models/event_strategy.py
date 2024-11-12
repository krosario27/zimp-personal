from abc import ABC, abstractmethod

class DevCardEventStrategy(ABC):
    def __init__(self, game, card):
        self.game = game
        self.card = card
        
    @abstractmethod
    def execute(self, player):
        pass