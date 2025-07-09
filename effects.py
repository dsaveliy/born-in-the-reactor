import pygame
import math

class DamageEffect:
    def __init__(self):
        self.timer = 0
        self.duration = 0.2
        self.color = (255, 0, 0, 210)
        
    def trigger(self):
        self.timer = self.duration
        
    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt
            
    def render(self, screen, screen_rect):
        if self.timer > 0:
            alpha = int(255 * (self.timer / self.duration))
            effect_surface = pygame.Surface((screen_rect.width, screen_rect.height), pygame.SRCALPHA)
            effect_surface.fill((self.color[0], self.color[1], self.color[2], alpha))
            screen.blit(effect_surface, (0, 0))