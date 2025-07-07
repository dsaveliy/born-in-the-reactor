import pygame
import sys
from pathlib import Path
from state import GameState
from states.menu_state import MainMenuState
from game_state import GameplayState
#from inventory import InventoryState
#from pause import PauseState
#from game_over import GameOverState
#from level_transition import LevelTransitionState

class Game:
    def __init__(self):
        self._init_pygame()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        
        self._init_states()
        self.current_state = GameState.MAIN_MENU
        self.states[self.current_state].enter()
    
    def _init_pygame(self):
        pygame.init()
        pygame.display.set_caption("BORN IN THE REACTOR")
    
    def _init_states(self):
        self.states = {
            GameState.MAIN_MENU: MainMenuState(self),
            GameState.GAMEPLAY: GameplayState(self),
            #GameState.INVENTORY: InventoryState(self),
            #GameState.PAUSE: PauseState(self),
            #GameState.GAME_OVER: GameOverState(self),
            #GameState.LEVEL_TRANSITION: LevelTransitionState(self)
        }
    
    def change_state(self, new_state):
        self.states[self.current_state].exit()
        self.current_state = new_state
        self.states[self.current_state].enter()
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.dt = self.clock.tick(60) / 1000
            self.states[self.current_state].update(self.dt)
            
            self.screen.fill((0, 0, 0))
            self.states[self.current_state].render(self.screen)
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()