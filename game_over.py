import pygame
import math
from state import State, GameState
from stats_state import StatsState

class GameOverState(State):
    def __init__(self, game, score=0):
        super().__init__(game)
        self.score = score
        self.stats = StatsState(game)
        try:
            self.font = pygame.font.Font("assets/fonts/Orbitron-Light.ttf", 36)
            self.button_font = pygame.font.Font("assets/fonts/Orbitron-Bold.ttf", 24)
        except FileNotFoundError:
            print("Error loading Orbitron-Light font, using default")
            self.font = pygame.font.Font(None, 36)
            self.button_font = pygame.font.Font(None, 24)
        
        try:
            self.background = pygame.image.load("assets/bgs/over_bg.jpg").convert()
            self.background = pygame.transform.scale(self.background, (800, 600))
        except FileNotFoundError:
            print("Error loading game over background")
            self.background = pygame.Surface((800, 600))
            self.background.fill((20, 20, 20))

        try:
            self.game_over_img = pygame.image.load("assets/bgs/game_over.png").convert_alpha()
            self.game_over_img = pygame.transform.scale(self.game_over_img, (500, int(500 * self.game_over_img.get_height() / self.game_over_img.get_width())))
        except FileNotFoundError:
            print("Error loading game over image, using placeholder")
            self.game_over_img = pygame.Surface((500, 125))
            self.game_over_img.fill((255, 50, 50))

        self.player_name = ""
        self.action_triggered = False
        self.text_pulse = 0
        self.max_name_length = 12
        self.input_active = True
        self.message = None
        self.message_timer = 0
        self.save_button_rect = pygame.Rect(250, 350, 150, 70)
        self.menu_button_rect = pygame.Rect(450, 350, 150, 70)

    def enter(self):
        print("Entered Game Over State")
        self.player_name = self.game.states[GameState.SETTINGS].data["player"].get("nickname", "Survivor")
        self.action_triggered = False
        self.text_pulse = 0
        self.input_active = True
        self.message = None
        self.message_timer = 0

    def exit(self):
        print("Exiting Game Over State")
        pygame.event.clear()

    def update(self, dt):
        self.text_pulse += dt
        if self.text_pulse >= 1.0:
            self.text_pulse = 0

        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            if self.input_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                elif event.key == pygame.K_RETURN:
                    self.input_active = False
                elif len(self.player_name) < self.max_name_length:
                    if event.unicode.isprintable():
                        self.player_name += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if self.save_button_rect.collidepoint(mouse_pos) and not self.action_triggered:
                    self.stats.add_score(self.player_name or "Survivor", self.score)
                    self.message = f"Score {self.score} saved for {self.player_name or 'Survivor'}"
                    self.message_timer = 2.0
                    self.action_triggered = True
                elif self.menu_button_rect.collidepoint(mouse_pos) and not self.action_triggered:
                    print("Returning to main menu from Game Over")
                    self.game.change_state(GameState.MAIN_MENU)
                    self.action_triggered = True

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_ESCAPE] or keys[pygame.K_RETURN]) and not self.action_triggered and not self.input_active:
            print("Returning to main menu from Game Over")
            self.game.change_state(GameState.MAIN_MENU)
            self.action_triggered = True
        if not keys[pygame.K_ESCAPE] and not keys[pygame.K_RETURN]:
            self.action_triggered = False

    def render(self, screen):
        pulse_alpha = 180 + int(30 * (1 + math.sin(self.text_pulse * math.pi)) / 2)
        screen.blit(self.background, (0, 0))

        game_over_rect = self.game_over_img.get_rect(center=(400, 50))
        screen.blit(self.game_over_img, game_over_rect)

        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(400, 200))
        screen.blit(score_text, score_rect)

        name_label = self.font.render("Enter Name:", True, (255, 255, 255))
        name_label_rect = name_label.get_rect(center=(400, 250))
        screen.blit(name_label, name_label_rect)

        name_text = self.font.render(self.player_name or "Enter name", True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(400, 300))
        name_bg_rect = name_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), name_bg_rect)
        if self.input_active:
            pygame.draw.rect(screen, (255, 255, 255, pulse_alpha), name_bg_rect, 2)
        screen.blit(name_text, name_rect)

        save_text = self.button_font.render("Save Score", True, (255, 255, 255))
        save_rect = save_text.get_rect(center=self.save_button_rect.center)
        save_bg_rect = self.save_button_rect.inflate(10, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), save_bg_rect)
        screen.blit(save_text, save_rect)

        menu_text = self.button_font.render("Main Menu", True, (255, 255, 255))
        menu_rect = menu_text.get_rect(center=self.menu_button_rect.center)
        menu_bg_rect = self.menu_button_rect.inflate(10, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), menu_bg_rect)
        screen.blit(menu_text, menu_rect)

        if self.message:
            message_text = self.font.render(self.message, True, (255, 255, 255))
            message_rect = message_text.get_rect(center=(400, 450))
            message_bg_rect = message_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), message_bg_rect)
            screen.blit(message_text, message_rect)