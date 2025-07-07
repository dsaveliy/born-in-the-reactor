import pygame
from state import State
from player import Player
from level import Level

class GameplayState(State):
    def enter(self):
        self.player = Player()
        self.level = Level("level1")
        self.font = pygame.font.Font(None, 24)
        self.camera_offset = pygame.Vector2(0, 0)
    
    def exit(self):
        pass
    
    def update(self, dt):
        self.player.update(dt)
        self.level.update(dt)
        
        # Обновление камеры (следование за игроком)
        target_x = self.player.position.x - 400
        target_y = self.player.position.y - 300
        self.camera_offset.x += (target_x - self.camera_offset.x) * 0.1
        self.camera_offset.y += (target_y - self.camera_offset.y) * 0.1
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.game.change_state(GameState.PAUSE)
        if keys[pygame.K_TAB]:
            self.game.change_state(GameState.INVENTORY)
    
    def render(self, screen):
        # Отрисовка уровня с учётом камеры
        self.level.render(screen, self.camera_offset)
        self.player.render(screen, self.camera_offset)
        
        # Отрисовка HUD
        health_text = self.font.render(f"HP: {self.player.health}", True, (255, 255, 255))
        screen.blit(health_text, (10, 10))