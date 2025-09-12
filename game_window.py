import pygame
import sys
import json
from pathlib import Path
from state import GameState
from menu_state import MainMenuState
from game_state import GameplayState
from settings_state import SettingsState
from stats_state import StatsState
from help_state import HelpState
from cutscene_state import CutsceneState
from audio_manager import AudioManager
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
        
        # Инициализация аудио менеджера
        self.audio_manager = AudioManager()
        
        # Загружаем настройки звука
        self._load_audio_settings()
        
        self._init_states()
        self.current_state = GameState.MAIN_MENU
        self.states[self.current_state].enter()
    
    def _init_pygame(self):
        pygame.init()
        pygame.display.set_caption("BORN IN THE REACTOR")
    
    def _load_audio_settings(self):
        """Загружает настройки звука из файла настроек"""
        try:
            with open("assets/settings/settings.json", 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # Применяем настройки к аудио менеджеру
            self.audio_manager.set_sound_enabled(settings.get("sound_enabled", True))
            self.audio_manager.set_music_enabled(settings.get("music_enabled", True))
            self.audio_manager.set_master_volume(settings.get("master_volume", 1.0))
            self.audio_manager.set_sfx_volume(settings.get("sfx_volume", 0.7))
            self.audio_manager.set_music_volume(settings.get("music_volume", 0.2))
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading audio settings: {e}")
            # Используем настройки по умолчанию
    
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
            
            # Ограничиваем FPS для стабильности
            self.dt = self.clock.tick(60) / 1000
            self.states[self.current_state].update(self.dt)
            
            # Очищаем экран только если нужно
            self.screen.fill((0, 0, 0))
            self.states[self.current_state].render(self.screen)
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
