import pygame
from state import State, GameState

class MainMenuState(State):
    def enter(self):
        self.font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 64)
        self.options = ["Start Game", "Settings", "Quit"]
        self.selected_option = 0
        self.background = pygame.Surface((800, 600))
        self.background.fill((20, 20, 40))
    
    def exit(self):
        pass
    
    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            self.selected_option = (self.selected_option + 1) % len(self.options)
        if keys[pygame.K_UP]:
            self.selected_option = (self.selected_option - 1) % len(self.options)
        if keys[pygame.K_RETURN]:
            if self.selected_option == 0:
                self.game.change_state(GameState.GAMEPLAY)
            elif self.selected_option == 2:
                self.game.running = False
    
    def render(self, screen):
        screen.blit(self.background, (0, 0))
        
        title = self.title_font.render("BORN IN THE REACTOR", True, (255, 0, 0))
        screen.blit(title, (400 - title.get_width() // 2, 100))
        
        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i != self.selected_option else (255, 200, 0)
            text = self.font.render(option, True, color)
            screen.blit(text, (400 - text.get_width() // 2, 250 + i * 60))