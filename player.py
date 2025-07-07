import pygame
from constants import PLAYER_SPEED

class Player:
    def __init__(self):
        self.health = 100
        self.position = pygame.Vector2(400, 300)
        self.velocity = pygame.Vector2(0, 0)
        self.speed = PLAYER_SPEED
        self.weapons = ["knife", "pistol", "shotgun"]
        self.current_weapon = 0
    
    def update(self, dt):
        keys = pygame.key.get_pressed()
        
        self.velocity.x = 0
        self.velocity.y = 0
        
        if keys[pygame.K_w]:
            self.velocity.y = -self.speed
        if keys[pygame.K_s]:
            self.velocity.y = self.speed
        if keys[pygame.K_a]:
            self.velocity.x = -self.speed
        if keys[pygame.K_d]:
            self.velocity.x = self.speed
        
        if self.velocity.length() > 0:
            self.velocity = self.velocity.normalize() * self.speed
        
        self.position += self.velocity * dt
    
    def render(self, screen, camera_offset):
        screen_pos = self.position - camera_offset
        pygame.draw.rect(screen, (255, 0, 0), (screen_pos.x - 10, screen_pos.y - 10, 20, 20))