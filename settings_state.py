import pygame
import json
import math
import os
from state import State, GameState

class SettingsState(State):
    def __init__(self, game):
        super().__init__(game)
        try:
            self.font = pygame.font.Font("assets/fonts/Orbitron-Bold.ttf", 36)
        except FileNotFoundError:
            print("Error loading Orbitron-Light font, using default")
            self.font = pygame.font.Font(None, 36)
        
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
            with open(file_path, 'r') as f:
                self.data = json.load(f)
            # Validate initial_level to prevent KeyError in GameplayState
            if self.data.get("initial_level") not in ["gomel_streets"]:
                print(f"Invalid initial_level '{self.data.get('initial_level')}', resetting to 'gomel_streets'")
                self.data["initial_level"] = "gomel_streets"
                self.save_settings(file_path)
            # Ensure sound_enabled exists
            if "sound_enabled" not in self.data:
                self.data["sound_enabled"] = True
                self.save_settings(file_path)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading settings: {e}")
            self.data = {
                "initial_level": "gomel_streets",
                "sound_enabled": True,
                "player": {
                    "initial_health": 100,
                    "initial_ammo": {
                        "pistol": 30,
                        "rifle": 50,
                        "shotgun": 20
                    },
                    "inventory": ["rifle", "medkit"]
                }
            }
            self.save_settings(file_path)

    def save_settings(self, file_path="assets/settings/settings.json"):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(self.data, f, indent=4)
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
        elif (keys[pygame.K_SPACE] or (mouse_clicked and 350 <= mouse_pos[1] <= 400 and 300 <= mouse_pos[0] <= 500)) and not self.action_triggered:
            self.data["sound_enabled"] = not self.data["sound_enabled"]
            self.save_settings()
            print(f"Sound toggled to: {self.data['sound_enabled']}")
            self.action_triggered = True

        if not keys[pygame.K_ESCAPE] and not keys[pygame.K_SPACE] and not mouse_clicked:
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
        level_text = self.font.render(f"Initial level: {self.get_initial_level()}", True, (255, 255, 255))
        level_rect = level_text.get_rect(center=(400, 150))
        level_bg_rect = level_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), level_bg_rect)
        screen.blit(level_text, level_rect)

        # Render inventory
        inventory = self.data.get("player", {}).get("inventory", [])
        inventory_text = f"Inventory: {', '.join(inventory) if inventory else 'Empty'}"
        inv_text = self.font.render(inventory_text, True, (255, 255, 255))
        inv_rect = inv_text.get_rect(center=(400, 230))
        inv_bg_rect = inv_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), inv_bg_rect)
        screen.blit(inv_text, inv_rect)

        # Render sound (two lines)
        sound_label = self.font.render("Sound", True, (255, 255, 255))
        sound_label_rect = sound_label.get_rect(center=(400, 310))
        sound_label_bg_rect = sound_label_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), sound_label_bg_rect)
        screen.blit(sound_label, sound_label_rect)

        sound_status = self.font.render("ON" if self.data["sound_enabled"] else "OFF", True, (255, 255, 255))
        sound_status_rect = sound_status.get_rect(center=(400, 360))
        sound_status_bg_rect = sound_status_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), sound_status_bg_rect)
        screen.blit(sound_status, sound_status_rect)

        # Render return prompt
        return_text = self.font.render("Press ESC to return to menu", True, (255, 255, 255))
        return_rect = return_text.get_rect(center=(400, 530))
        return_bg_rect = return_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), return_bg_rect)
        screen.blit(return_text, return_rect)

        # Render back to game prompt
        back_text = self.font.render("Press B to return to game", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=(400, 560))
        back_bg_rect = back_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), back_bg_rect)
        screen.blit(back_text, back_rect)