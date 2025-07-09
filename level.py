import pygame
import json
import logging
import os
from typing import Dict, List, Optional
from enemy import Enemy
import random
from typing import List, Dict

class Level:
    def __init__(self, json_file):
        with open(json_file, 'r') as f:
            self.data = json.load(f)
        
        self.name = self.data['name']
        self.background_texture = self.data.get('background_texture')
        self.obstacles = self.data.get('obstacles', [])
        self.objects_decor = self.data.get('objects_decor', [])
        self.objects = self.data.get('objects', [])
        self.player_spawn = self.data.get('player_spawn', {'x': 400, 'y': 300})
        self.enemies = [Enemy(e["x"], e["y"]) for e in self.data.get("enemies", [])]
        self.transition_zone = self.data.get("transition_zone", None)
        # загрузка фонового изображения
        self.background = pygame.image.load(self.background_texture).convert()
        self.bg_width = self.background.get_width()
        self.bg_height = self.background.get_height()

    def is_position_blocked(self, x, y, width, height):
        # проверка, является ли область стеной
        player_rect = pygame.Rect(
            x - width//2,
            y - height//2,
            width, height
            )
        for obstacle in self.obstacles:
            obstacle_rect = pygame.Rect(
                obstacle['x'],
                obstacle['y'],
                obstacle['width'],
                obstacle['height']
            )
            if player_rect.colliderect(obstacle_rect):
                return True
            
        for object in self.objects_decor:
            object_rect = pygame.Rect(
                object['x'],
                object['y'],
                object['width'],
                object['height']
            )
            if player_rect.colliderect(object_rect):
                return True
        return False

    def render(self, screen, player_world_x, player_world_y):
        screen_width, screen_height = screen.get_size()
        camera_offset_x = screen_width // 2 - player_world_x
        camera_offset_y = screen_height // 2 - player_world_y
        
        # находим границы уровня из obstacles
        level_left = min(obs['x'] for obs in self.obstacles)
        level_right = max(obs['x'] + obs['width'] for obs in self.obstacles)
        level_top = min(obs['y'] for obs in self.obstacles)
        level_bottom = max(obs['y'] + obs['height'] for obs in self.obstacles)
        
        level_width = level_right - level_left
        level_height = level_bottom - level_top
        
        # отрисовка фона (только внутри границ)
        if self.background:
            # масштабируем фон под размер уровня
            scaled_bg = pygame.transform.scale(self.background, (level_width, level_height))
            screen.blit( scaled_bg, (level_left + camera_offset_x, level_top + camera_offset_y))
        
        # отрисовка границ (препятствий)
        for obstacle in self.obstacles:
            pygame.draw.rect(
                screen,
                (100, 100, 100, 180),  # цвет пока что, потом - текстуры
                (
                    obstacle['x'] + camera_offset_x,
                    obstacle['y'] + camera_offset_y,
                    obstacle['width'],
                    obstacle['height']
                )
            )
        
        for object in self.objects_decor:
                obj = pygame.image.load(object["image"]).convert_alpha()
                scaled_obj = pygame.transform.scale(obj, (object['width'], object['height']))
                screen.blit(scaled_obj, (object['x'] + camera_offset_x, object['y'] + camera_offset_y))