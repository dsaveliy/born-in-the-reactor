import pygame
import json
import math
import os
from state import State, GameState

class SettingsState(State):
    def __init__(self, game):
        super().__init__(game)
        try:
            self.font = pygame.font.Font("assets/fonts/Orbitron-Bold.ttf", 24)
        except FileNotFoundError:
            print("Error loading Orbitron-Light font, using default")
            self.font = pygame.font.Font(None, 24)
        
        self.load_settings()
        self.message = None
        self.action_triggered = False
        self.text_pulse = 0  # For pulsing text background
        
        try:
            self.background = pygame.image.load("assets/bgs/settings_bg.png").convert()
            self.background = pygame.transform.scale(self.background, (800, 600))
        except FileNotFoundError:
            print("Error loading settings background")
            self.background = pygame.Surface((800, 600))
            self.background.fill((30, 30, 60))

    def load_settings(self, file_path="assets/settings/settings.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            # Validate initial_level to prevent KeyError in GameplayState
            if self.data.get("initial_level") not in ["gomel_streets", "home", "office"]:
                print(f"Invalid initial_level '{self.data.get('initial_level')}', resetting to 'gomel_streets'")
                self.data["initial_level"] = "gomel_streets"
                self.save_settings(file_path)
            # Ensure required settings exist
            if "sound_enabled" not in self.data:
                self.data["sound_enabled"] = True
            if "music_enabled" not in self.data:
                self.data["music_enabled"] = True
            if "master_volume" not in self.data:
                self.data["master_volume"] = 1.0
            if "sfx_volume" not in self.data:
                self.data["sfx_volume"] = 0.7
            if "music_volume" not in self.data:
                self.data["music_volume"] = 0.2
            if "player" not in self.data:
                self.data["player"] = {}
            if "id" not in self.data["player"]:
                self.data["player"]["id"] = "default_player"
            if "photo" not in self.data["player"]:
                self.data["player"]["photo"] = "assets/player/default_avatar.png"
            if "nickname" not in self.data["player"]:
                self.data["player"]["nickname"] = "Survivor"
            if "health_damage_effect" not in self.data["player"]:
                self.data["player"]["health_damage_effect"] = True
            if "aim_line" not in self.data["player"]:
                self.data["player"]["aim_line"] = False
            if "shot_animation" not in self.data["player"]:
                self.data["player"]["shot_animation"] = True
                self.save_settings(file_path)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading settings: {e}")
            self.data = {
                "initial_level": "gomel_streets",
                "sound_enabled": True,
                "player": {
                    "id": "default_player",
                    "photo": "assets/player/default_avatar.png",
                    "nickname": "Survivor",
                    "initial_health": 100,
                    "initial_ammo": {
                        "pistol": 30,
                        "rifle": 50,
                        "shotgun": 20
                    },
                    "health_damage_effect": True,
                    "aim_line": False,
                    "shot_animation": True
                }
            }
            self.save_settings(file_path)

    def save_settings(self, file_path="assets/settings/settings.json"):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get_initial_level(self):
        return self.data.get("initial_level", "gomel_streets")

    def get_player_settings(self):
        return self.data.get("player", {})

    def enter(self):
        print("Entered Settings State")
        self.message = None
        self.action_triggered = False
        self.text_pulse = 0

    def exit(self):
        print("Exiting Settings State")

    def update(self, dt):
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        # Update text pulse effect
        self.text_pulse += dt
        if self.text_pulse >= 1.0:
            self.text_pulse = 0

        if keys[pygame.K_ESCAPE] and not self.action_triggered:
            self.game.change_state(GameState.MAIN_MENU)
            self.action_triggered = True

        # Dynamic toggle logic for settings
        if mouse_clicked and not self.action_triggered:
            # Toggle sound
            if 200 < mouse_pos[0] < 400 and 200 < mouse_pos[1] < 250:
                self.data["sound_enabled"] = not self.data["sound_enabled"]
                if hasattr(self.game, 'audio_manager'):
                    self.game.audio_manager.set_sound_enabled(self.data["sound_enabled"])
                self.save_settings()
                self.action_triggered = True
            # Toggle health damage effect
            elif 450 < mouse_pos[0] < 650 and 200 < mouse_pos[1] < 250:
                self.data["player"]["health_damage_effect"] = not self.data["player"]["health_damage_effect"]
                self.save_settings()
                self.action_triggered = True
            # Toggle aiming line
            elif 200 < mouse_pos[0] < 400 and 350 < mouse_pos[1] < 400:
                self.data["player"]["aim_line"] = not self.data["player"]["aim_line"]
                self.save_settings()
                self.action_triggered = True
            # Toggle shot animation
            elif 450 < mouse_pos[0] < 650 and 350 < mouse_pos[1] < 400:
                self.data["player"]["shot_animation"] = not self.data["player"]["shot_animation"]
                self.save_settings()
                self.action_triggered = True

        if not keys[pygame.K_ESCAPE] and not mouse_clicked:
            self.action_triggered = False

    def render(self, screen):
        # Calculate pulse_alpha for all rendering blocks
        pulse_alpha = 180 + int(30 * (1 + math.sin(self.text_pulse * math.pi)) / 2)  # Pulse between 180-210

        screen.blit(self.background, (0, 0))
        
        # Render title
        title_text = self.font.render("Settings", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(400, 50))
        title_bg_rect = title_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), title_bg_rect)
        screen.blit(title_text, title_rect)

        # Render initial level
        level_text = self.font.render(f"Current Level: {self.get_initial_level()}", True, (255, 255, 255))
        level_rect = level_text.get_rect(center=(400, 100))
        level_bg_rect = level_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), level_bg_rect)
        screen.blit(level_text, level_rect)

        # Render sound (left column)
        sound_label = self.font.render("Sound", True, (255, 255, 255))
        sound_label_rect = sound_label.get_rect(center=(300, 175))
        sound_label_bg_rect = sound_label_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), sound_label_bg_rect)
        screen.blit(sound_label, sound_label_rect)

        sound_status = self.font.render("ON" if self.data["sound_enabled"] else "OFF", True, (255, 255, 255))
        sound_status_rect = sound_status.get_rect(center=(300, 225))
        sound_status_bg_rect = sound_status_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), sound_status_bg_rect)
        screen.blit(sound_status, sound_status_rect)

        # Render health damage effect (right column)
        health_effect_label = self.font.render("Health Damage Effect", True, (255, 255, 255))
        health_effect_label_rect = health_effect_label.get_rect(center=(550, 175))
        health_effect_bg_rect = health_effect_label_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), health_effect_bg_rect)
        screen.blit(health_effect_label, health_effect_label_rect)

        health_effect_status = self.font.render("ON" if self.data["player"]["health_damage_effect"] else "OFF", True, (255, 255, 255))
        health_effect_status_rect = health_effect_status.get_rect(center=(550, 225))
        health_effect_status_bg_rect = health_effect_status_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), health_effect_status_bg_rect)
        screen.blit(health_effect_status, health_effect_status_rect)

        # Render aiming line (left column)
        aim_line_label = self.font.render("Aiming Line", True, (255, 255, 255))
        aim_line_label_rect = aim_line_label.get_rect(center=(300, 325))
        aim_line_bg_rect = aim_line_label_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), aim_line_bg_rect)
        screen.blit(aim_line_label, aim_line_label_rect)

        aim_line_status = self.font.render("ON" if self.data["player"]["aim_line"] else "OFF", True, (255, 255, 255))
        aim_line_status_rect = aim_line_status.get_rect(center=(300, 375))
        aim_line_status_bg_rect = aim_line_status_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), aim_line_status_bg_rect)
        screen.blit(aim_line_status, aim_line_status_rect)

        # Render shot animation (right column)
        shot_anim_label = self.font.render("Shot Animation", True, (255, 255, 255))
        shot_anim_label_rect = shot_anim_label.get_rect(center=(550, 325))
        shot_anim_bg_rect = shot_anim_label_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), shot_anim_bg_rect)
        screen.blit(shot_anim_label, shot_anim_label_rect)

        shot_anim_status = self.font.render("ON" if self.data["player"]["shot_animation"] else "OFF", True, (255, 255, 255))
        shot_anim_status_rect = shot_anim_status.get_rect(center=(550, 375))
        shot_anim_status_bg_rect = shot_anim_status_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), shot_anim_status_bg_rect)
        screen.blit(shot_anim_status, shot_anim_status_rect)

        # Render return prompt
        return_text = self.font.render("Press ESC to return", True, (255, 255, 255))
        return_rect = return_text.get_rect(center=(400, 540))
        return_bg_rect = return_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), return_bg_rect)
        screen.blit(return_text, return_rect)
