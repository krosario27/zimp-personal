from abc import ABC, abstractmethod

class DevCardEventStrategy(ABC):
    def __init__(self, game):
        self.game = game
        
    @abstractmethod
    def execute(self, player):
        raise NotImplementedError("This method should be overridden in a subclass")