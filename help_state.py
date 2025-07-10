import pygame
import json
import math
from state import State, GameState

class HelpState(State):
    def __init__(self, game):
        super().__init__(game)
        try:
            self.font = pygame.font.Font("assets/fonts/ShareTechMono-Regular.ttf", 32)
        except FileNotFoundError:
            print("Error loading fonts, using default")
            self.font = pygame.font.Font(None, 36)

        try:
            with open("assets/main/help.json", "r") as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading help.json: {e}")
            self.config = {
                "background": "assets/bgs/help_bg.png",
                "options": [
                    {"name": "Description", "message": "A post-apocalyptic shooter set in a reactor."},
                    {"name": "Hotkeys", "message": "WASD/Arrows: Move, Space: Shoot, I: Inventory"},
                    {"name": "About", "message": "BORN IN THE REACTOR, 2025"},
                    {"name": "Back", "message": ""}
                ]
            }

        try:
            self.background = pygame.image.load(self.config["background"]).convert()
            self.background = pygame.transform.scale(self.background, (800, 600))
        except FileNotFoundError:
            print(f"Error loading help background {self.config['background']}")
            self.background = pygame.Surface((800, 600))
            self.background.fill((40, 60, 40))

        self.options = [option["name"] for option in self.config["options"]]
        self.messages = {option["name"]: option["message"] for option in self.config["options"]}
        self.selected_option = 0
        self.message = None
        self.action_triggered = False
        self.text_pulse = 0

    def enter(self):
        print("Entered Help State")
        self.selected_option = 0
        self.message = None
        self.action_triggered = False
        self.text_pulse = 0

    def exit(self):
        print("Exiting Help State")

    def update(self, dt):
        keys = pygame.key.get_pressed()

        # Update text pulse effect
        self.text_pulse += dt
        if self.text_pulse >= 1.0:
            self.text_pulse = 0

        if keys[pygame.K_ESCAPE] and not self.action_triggered:
            print("Returning to main menu from Help")
            self.game.change_state(GameState.MAIN_MENU)
            self.action_triggered = True
        elif keys[pygame.K_DOWN] and not self.action_triggered:
            self.selected_option = (self.selected_option + 1) % len(self.options)
            print(f"Selected option: {self.options[self.selected_option]}")
            self.action_triggered = True
        elif keys[pygame.K_UP] and not self.action_triggered:
            self.selected_option = (self.selected_option - 1) % len(self.options)
            print(f"Selected option: {self.options[self.selected_option]}")
            self.action_triggered = True
        elif keys[pygame.K_RETURN] and not self.action_triggered:
            self.action_triggered = True
            print(f"Enter pressed, selected_option={self.selected_option}")
            if self.options[self.selected_option] == "Back":
                print("Returning to main menu from Help")
                self.game.change_state(GameState.MAIN_MENU)
            else:
                self.message = self.messages[self.options[self.selected_option]]

        if not keys[pygame.K_RETURN] and not keys[pygame.K_UP] and not keys[pygame.K_DOWN] and not keys[pygame.K_ESCAPE]:
            self.action_triggered = False

    def render(self, screen):
        # Calculate pulse_alpha for all rendering blocks
        pulse_alpha = 180 + int(30 * (1 + math.sin(self.text_pulse * math.pi)) / 2)  # Pulse between 180-210

        screen.blit(self.background, (0, 0))
        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i != self.selected_option else (255, 200, 0)
            text = self.font.render(option, True, color)
            screen.blit(text, (400 - text.get_width() // 2, 150 + i * 50))

        if self.message:
            message_text = self.font.render(self.message, True, (255, 255, 255))
            screen.blit(message_text, (400 - message_text.get_width() // 2, 240))

        return_text = self.font.render("Press ESC to return", True, (255, 255, 255))
        return_rect = return_text.get_rect(center=(400, 540))
        background_rect = return_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), background_rect)
        screen.blit(return_text, return_rect)