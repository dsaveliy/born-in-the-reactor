import pygame
import sys
from pathlib import Path
from state import GameState
from menu_state import MainMenuState
from game_state import GameplayState
from settings_state import SettingsState
from stats_state import StatsState
from help_state import HelpState
from cutscene_state import CutsceneState
#from pause import PauseState
from game_over import GameOverState
#from level_transition import LevelTransitionState

class Game:
    def __init__(self):
        self._init_pygame()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.mouse_wheel = 0  
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
            GameState.STATS: StatsState(self),
            GameState.SETTINGS: SettingsState(self),
            GameState.GAME_OVER: GameOverState(self, score=0),
            GameState.HELP: HelpState(self),
            GameState.CUTSCENE: CutsceneState(self)
            #GameState.INVENTORY: InventoryState(self),
            #GameState.PAUSE: PauseState(self),
            #GameState.LEVEL_TRANSITION: LevelTransitionState(self)
        }
    
    def change_state(self, new_state, **kwargs):
        self.states[self.current_state].exit()
        if new_state == GameState.GAME_OVER:
            self.states[new_state] = GameOverState(self, **kwargs)  # Create new instance with score
        self.current_state = new_state
        self.states[self.current_state].enter()
    
    def play_cutscene(self, cutscene_path: str, next_state: GameState = None, **kwargs):
        """Запускает катсцену с переходом к указанному состоянию"""
        cutscene_state = self.states[GameState.CUTSCENE]
        cutscene_state.load_cutscene(cutscene_path, next_state, **kwargs)
        self.change_state(GameState.CUTSCENE)
    
    def run(self):
        while self.running:
            self.mouse_wheel = 0 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEWHEEL:
                    self.mouse_wheel += event.y 
            
            self.dt = self.clock.tick(60) / 1000
            self.states[self.current_state].update(self.dt)
            
            self.screen.fill((0, 0, 0))
            self.states[self.current_state].render(self.screen)
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
