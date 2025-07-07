import pygame
import json
import os
from enemy import Enemy

class Level:
    def __init__(self, level_name):
        self.name = level_name
        self.tile_size = 32
        self.tiles = []
        self.enemies = []
        self._load_level()
    
    def _load_level(self):
        # Простая загрузка уровня (можно заменить на загрузку из файла)
        self.width = 50
        self.height = 50
        
        # Простая генерация уровня
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if x == 0 or y == 0 or x == self.width-1 or y == self.height-1:
                    row.append(1)  # Стена
                else:
                    row.append(0)  # Пол
            self.tiles.append(row)
        
        # Добавляем несколько врагов
        for i in range(5):
            self.enemies.append(Enemy(100 + i * 150, 100 + i * 100))
    
    def update(self, dt):
        for enemy in self.enemies:
            enemy.update(dt)
    
    def render(self, screen, camera_offset):
        for y in range(self.height):
            for x in range(self.width):
                tile_type = self.tiles[y][x]
                if tile_type == 1:  # Стена
                    rect = pygame.Rect(
                        x * self.tile_size - camera_offset.x,
                        y * self.tile_size - camera_offset.y,
                        self.tile_size,
                        self.tile_size
                    )
                    pygame.draw.rect(screen, (100, 100, 100), rect)
                else:  # Пол
                    rect = pygame.Rect(
                        x * self.tile_size - camera_offset.x,
                        y * self.tile_size - camera_offset.y,
                        self.tile_size,
                        self.tile_size
                    )
                    pygame.draw.rect(screen, (50, 50, 50), rect)
        
        for enemy in self.enemies:
            enemy.render(screen, camera_offset)