import pygame
import os
from typing import Dict, Optional

class AudioManager:
    # центральный менеджер звуков игры
    
    def __init__(self):
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.sound_enabled = True
        self.music_enabled = True
        self.master_volume = 1.0
        self.sfx_volume = 0.7
        self.music_volume = 0.5
        
        # инициализация pygame mixer
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        
        # загружаем звуки
        self._load_sounds()
    
    def _load_sounds(self):
        # загружает все звуковые файлы
        sound_files = {
            'menu_click': 'assets/sounds/menu_click.wav',
            'menu_hover': 'assets/sounds/menu_hover.wav',
            'shoot_pistol': 'assets/sounds/shoot_pistol.wav',
            'shoot_rifle': 'assets/sounds/shoot_rifle.wav',
            'shoot_shotgun': 'assets/sounds/shoot_shotgun.wav',
            'reload': 'assets/sounds/reload.wav',
            'medkit_use': 'assets/sounds/medkit_use.wav',
            'enemy_hit': 'assets/sounds/enemy_hit.wav',
            'enemy_death': 'assets/sounds/enemy_death.wav',
            'item_pickup': 'assets/sounds/item_pickup.wav',
            'door_open': 'assets/sounds/door_open.wav'
        }
        
        for sound_name, file_path in sound_files.items():
            try:
                if os.path.exists(file_path):
                    self.sounds[sound_name] = pygame.mixer.Sound(file_path)
                    print(f"Loaded sound: {sound_name}")
                else:
                    print(f"Sound file not found: {file_path}")
            except pygame.error as e:
                print(f"Error loading sound {sound_name}: {e}")
    
    def load_music(self, music_file: str):
        # загружает фоновую музыку
        try:
            if os.path.exists(music_file):
                pygame.mixer.music.load(music_file)
                print(f"Loaded music: {music_file}")
            else:
                print(f"Music file not found: {music_file}")
        except pygame.error as e:
            print(f"Error loading music: {e}")
    
    def play_sound(self, sound_name: str, volume: float = None):
        # воспроизводит звуковой эффект
        if not self.sound_enabled or sound_name not in self.sounds:
            return
        
        sound = self.sounds[sound_name]
        if volume is None:
            volume = self.sfx_volume
        
        sound.set_volume(volume * self.master_volume)
        sound.play()
    
    def play_music(self, loop: int = -1):
        # воспроизводит фоновую музыку
        if not self.music_enabled:
            return
        
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
        pygame.mixer.music.play(loop)
    
    def stop_music(self):
        # останавливает фоновую музыку
        pygame.mixer.music.stop()
    
    def set_sound_enabled(self, enabled: bool):
        # включает/выключает звуковые эффекты
        self.sound_enabled = enabled
    
    def set_music_enabled(self, enabled: bool):
        # включает/выключает фоновую музыку
        self.music_enabled = enabled
        if not enabled:
            self.stop_music()
    
    def set_master_volume(self, volume: float):
        # устанавливает общую громкость (0.0 - 1.0)
        self.master_volume = max(0.0, min(1.0, volume))
    
    def set_sfx_volume(self, volume: float):
        # устанавливает громкость звуковых эффектов (0.0 - 1.0)
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def set_music_volume(self, volume: float):
        # устанавливает громкость музыки (0.0 - 1.0)
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
    
    def cleanup(self):
        # очищает ресурсы
        pygame.mixer.quit()