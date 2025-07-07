import pygame
import random

class Enemy:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.health = 30
        self.speed = 50
        self.direction = pygame.Vector2(1, 0)
        self.direction_change_timer = 0
    
    def update(self, dt):
        self.direction_change_timer -= dt
        if self.direction_change_timer <= 0:
            self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            if self.direction.length() > 0:
                self.direction = self.direction.normalize()
            self.direction_change_timer = random.uniform(1, 3)
        
        self.position += self.direction * self.speed * dt
    
    def render(self, screen, camera_offset):
        screen_pos = self.position - camera_offset
        pygame.draw.rect(screen, (0, 0, 255), (screen_pos.x - 10, screen_pos.y - 10, 20, 20))