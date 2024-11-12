from abc import ABC, abstractmethod

class DevCardEventStrategy(ABC):
    def __init__(self, game):
        self.game = game
        
    @abstractmethod
    def execute(self, player):
        pass