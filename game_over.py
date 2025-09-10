import pygame
import math
from state import State, GameState
from stats_state import StatsState  # Убедитесь, что это новый stats_state.py с SQLite

class GameOverState(State):
    def __init__(self, game, score=0):
        super().__init__(game)
        self.score = score  # Score passed from GameplayState (e.g., enemies killed)
        self.stats = StatsState(game)  # Initialize with SQLite-based StatsState
        try:
            self.font = pygame.font.Font("assets/fonts/Orbitron-Light.ttf", 36)
        except FileNotFoundError:
            print("Error loading Orbitron-Light font, using default")
            self.font = pygame.font.Font(None, 36)
        
        try:
            self.background = pygame.image.load("assets/bgs/game_over_bg.png").convert()
            self.background = pygame.transform.scale(self.background, (800, 600))
        except FileNotFoundError:
            print("Error loading game over background")
            self.background = pygame.Surface((800, 600))
            self.background.fill((20, 20, 20))  # Dark gray background

        self.player_name = ""
        self.action_triggered = False
        self.text_pulse = 0
        self.max_name_length = 12  # Limit name length
        self.input_active = True  # Allow name input until submitted

    def enter(self):
        print("Entered Game Over State")
        self.player_name = ""
        self.action_triggered = False
        self.text_pulse = 0
        self.input_active = True

    def exit(self):
        print("Exiting Game Over State")
        pygame.event.clear()  # Clear input to prevent carryover

    def update(self, dt):
        self.text_pulse += dt
        if self.text_pulse >= 1.0:
            self.text_pulse = 0

        if not self.input_active:
            keys = pygame.key.get_pressed()
            if (keys[pygame.K_RETURN] or keys[pygame.K_ESCAPE]) and not self.action_triggered:
                print("Returning to main menu from Game Over")
                self.game.change_state(GameState.MAIN_MENU)
                self.action_triggered = True
            if not keys[pygame.K_RETURN] and not keys[pygame.K_ESCAPE]:
                self.action_triggered = False
            return

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and not self.action_triggered:
                    if self.player_name.strip():
                        self.stats.add_score(self.player_name.strip(), self.score)
                        self.input_active = False
                        self.action_triggered = True
                        print(f"Saved score: {self.score} for player: {self.player_name}")
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                elif event.key == pygame.K_ESCAPE and not self.action_triggered:
                    print("Returning to main menu from Game Over without saving")
                    self.game.change_state(GameState.MAIN_MENU)
                    self.action_triggered = True
                elif len(self.player_name) < self.max_name_length and event.unicode.isalnum():
                    self.player_name += event.unicode

        keys = pygame.key.get_pressed()
        if not keys[pygame.K_RETURN] and not keys[pygame.K_ESCAPE]:
            self.action_triggered = False

    def render(self, screen):
        pulse_alpha = 180 + int(30 * (1 + math.sin(self.text_pulse * math.pi)) / 2)  # Pulse between 180-210

        screen.blit(self.background, (0, 0))
        
        # Render "Game Over" title
        title_text = self.font.render("Game Over", True, (255, 50, 50))
        title_rect = title_text.get_rect(center=(400, 100))
        screen.blit(title_text, title_rect)

        # Render score
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(400, 200))
        screen.blit(score_text, score_rect)

        # Render name input or saved message
        if self.input_active:
            name_text = self.font.render(f"Enter Name: {self.player_name}", True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(400, 300))
            background_rect = name_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), background_rect)
            screen.blit(name_text, name_rect)
            prompt_text = self.font.render("Press Enter to save", True, (255, 255, 255))
            prompt_rect = prompt_text.get_rect(center=(400, 350))
            screen.blit(prompt_text, prompt_rect)
        else:
            saved_text = self.font.render(f"Score Saved for {self.player_name}", True, (255, 255, 255))
            saved_rect = saved_text.get_rect(center=(400, 300))
            screen.blit(saved_text, saved_rect)

        # Render return prompt
        return_text = self.font.render("Press Enter or ESC to return", True, (255, 255, 255))
        return_rect = return_text.get_rect(center=(400, 540))
        background_rect = return_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), background_rect)
        screen.blit(return_text, return_rect)