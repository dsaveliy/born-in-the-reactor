import pygame
import time

class HitscanShot:
    def __init__(self, start_pos, end_pos, damage):
        self.start = pygame.Vector2(start_pos)
        self.end = pygame.Vector2(end_pos)
        self.damage = damage
        self.timer = 0.15  # трейсер будет жить 0.05 сек

    def update(self, dt):
        self.timer -= dt

    def is_alive(self):
        return self.timer > 0

    def render(self, screen):
        pygame.draw.line(screen, (255, 255, 204), self.start, self.end, 10)