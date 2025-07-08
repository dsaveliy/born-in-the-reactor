from enum import Enum, auto
from abc import ABC, abstractmethod

class GameState(Enum):
    MAIN_MENU = auto()
    GAMEPLAY = auto()
    STATS = auto()
    INVENTORY = auto()
    PAUSE = auto()
    GAME_OVER = auto()
    SETTINGS = auto()
    LEVEL_TRANSITION = auto()

class State(ABC):
    def __init__(self, game):
        self.game = game
    
    @abstractmethod
    def enter(self):
        pass
    
    @abstractmethod
    def exit(self):
        pass
    
    @abstractmethod
    def update(self, dt):
        pass
    
    @abstractmethod
    def render(self, screen):
        pass