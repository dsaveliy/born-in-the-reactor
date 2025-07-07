import pygame
import json
import logging
import os
from typing import Dict, List, Optional
from enemy import Enemy

class Level:
    def __init__(self, json_file):
        with open(json_file, 'r') as f:
            self.data = json.load(f)
        
        self.name = self.data['name']
        self.background_texture = self.data.get('background_texture')
        self.obstacles = self.data.get('obstacles', [])
        self.objects = self.data.get('objects', [])
        self.player_spawn = self.data.get('player_spawn', {'x': 400, 'y': 300})
        
        # Загрузка фонового изображения
        self.background = None
        if self.background_texture and os.path.exists(self.background_texture):
            try:
                self.background = pygame.image.load(self.background_texture).convert()
                # Получаем размеры фона
                self.bg_width = self.background.get_width()
                self.bg_height = self.background.get_height()
            except pygame.error as e:
                print(f"Error loading background: {e}")
                self.background = None

    def is_position_blocked(self, x, y, width, height):
        """Check if position is blocked by obstacles (world coordinates)"""
        player_rect = pygame.Rect(x, y, width, height)
        for obstacle in self.obstacles:
            obstacle_rect = pygame.Rect(
                obstacle['x'],
                obstacle['y'],
                obstacle['width'],
                obstacle['height']
            )
            if player_rect.colliderect(obstacle_rect):
                return True
        return False

    def draw(self, screen, player_world_x, player_world_y):
        screen_width, screen_height = screen.get_size()
        camera_offset_x = screen_width // 2 - player_world_x
        camera_offset_y = screen_height // 2 - player_world_y
        
        # Отрисовка фона
        if self.background:
            # Рассчитываем сколько раз нужно нарисовать фон (для бесшовного повторения)
            bg_start_x = -((-camera_offset_x) % self.bg_width) - self.bg_width
            bg_start_y = -((-camera_offset_y) % self.bg_height) - self.bg_height
            
            for y in range(bg_start_y, screen_height, self.bg_height):
                for x in range(bg_start_x, screen_width, self.bg_width):
                    screen.blit(self.background, (x, y))
        
        # Отрисовка препятствий
        for obstacle in self.obstacles:
            pygame.draw.rect(
                screen, 
                (100, 100, 100, 128),  # Полупрозрачные препятствия
                (obstacle['x'] + camera_offset_x,
                 obstacle['y'] + camera_offset_y,
                 obstacle['width'],
                 obstacle['height'])
            )
        
        # Отрисовка объектов
        for obj in self.objects:
            color = {
                'medkit': (0, 255, 0),
                'ammo': (255, 255, 0),
                'rifle': (139, 69, 19),
                'portal': (255, 0, 255)
            }.get(obj['type'], (0, 0, 255))
            
            if obj['type'] == 'portal':
                pygame.draw.circle(
                    screen, color,
                    (int(obj['x'] + camera_offset_x), int(obj['y'] + camera_offset_y)),
                    15
                )
            else:
                pygame.draw.rect(
                    screen, color,
                    (obj['x'] + camera_offset_x, obj['y'] + camera_offset_y, 20, 20)
                )