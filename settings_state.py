import pygame
import json
import os
from state import State, GameState

class SettingsState(State):
    def __init__(self, game):
        super().__init__(game)
        try:
            self.font = pygame.font.Font("assets/fonts/Orbitron-Light.ttf", 36)
        except FileNotFoundError:
            print("Error loading Orbitron-Light font, using default")
            self.font = pygame.font.Font(None, 36)
        
        self.load_settings()
        self.message = None
        self.action_triggered = False
        
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
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading settings: {e}")
            self.data = {
                "initial_level": "gomel_streets",
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
        self.message = f"Initial level: {self.get_initial_level()}"
        self.action_triggered = False

    def exit(self):
        print("Exiting Settings State")

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE] and not self.action_triggered:
            self.game.change_state(GameState.MAIN_MENU)
            self.action_triggered = True

        if not keys[pygame.K_ESCAPE]:
            self.action_triggered = False

    def render(self, screen):
        screen.blit(self.background, (0, 0))
        if self.message:
            message_text = self.font.render(self.message, True, (255, 255, 255))
            screen.blit(message_text, (400 - message_text.get_width() // 2, 240))
        return_text = self.font.render("Press ESC to return", True, (255, 255, 255))
        screen.blit(return_text, (400 - return_text.get_width() // 2, 540))