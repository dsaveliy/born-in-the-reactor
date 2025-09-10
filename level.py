import pygame
import json
import logging
import os
from typing import Dict, List, Optional
from enemy import Enemy
import random
from typing import List, Dict
from quest_system import QuestSystem

class Level:
    def __init__(self, json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.name = self.data['name']
        self.background_texture = self.data.get('background_texture')
        self.obstacles = self.data.get('obstacles', [])
        self.objects_decor = self.data.get('objects_decor', [])
        self.objects = self.data.get('objects', [])
        self.player_spawn = self.data.get('player_spawn', {'x': 400, 'y': 300})
        self.enemies = [Enemy(e["x"], e["y"]) for e in self.data.get("enemies", [])]
        self.transition_zone = self.data.get("transition_zone", None)
        if self.transition_zone and "image" in self.transition_zone:
            self.door_image = pygame.image.load(self.transition_zone["image"]).convert_alpha()
            self.door_image = pygame.transform.scale( self.door_image, (self.transition_zone["width"],
                    self.transition_zone["height"]))
        else:
            self.door_image = None
        
        # Инициализация системы квестов
        self.quest_system = QuestSystem()
        self.quest_system.load_from_level_data(self.data)

        # загрузка фонового изображения
        if self.background_texture:
            self.background = pygame.image.load(self.background_texture).convert()
            self.bg_width = self.background.get_width()
            self.bg_height = self.background.get_height()
        else:
            self.background = None


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
        if self.background_texture != None:
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

        # отрисовка двери перехода
        if self.transition_zone:
            door_x = self.transition_zone["x"] + camera_offset_x
            door_y = self.transition_zone["y"] + camera_offset_y

            if self.door_image:
                screen.blit(self.door_image, (door_x, door_y))
            else:
                pygame.draw.rect(screen, (0, 255, 255), 
                    (door_x, door_y, self.transition_zone["width"], self.transition_zone["height"]), 0)
        
        # отрисовка квестовых предметов
        self._render_quest_items(screen, camera_offset_x, camera_offset_y)
    
    def _render_quest_items(self, screen, camera_offset_x, camera_offset_y):
        """Отрисовка квестовых предметов"""
        for quest_item in self.quest_system.get_spawned_items():
            item_x = quest_item.x + camera_offset_x
            item_y = quest_item.y + camera_offset_y
            
            # Загружаем спрайт в зависимости от типа предмета
            sprite = None
            try:
                if quest_item.item_type == "pistol":
                    sprite = pygame.image.load("assets/weapons/pistol/side.png").convert_alpha()
                    sprite = pygame.transform.scale(sprite, (40, 25))
                elif quest_item.item_type == "armor":
                    # Временно используем спрайт пистолета для брони (пока нет спрайта брони)
                    sprite = pygame.image.load("assets/weapons/pistol/side.png").convert_alpha()
                    sprite = pygame.transform.scale(sprite, (35, 25))
                elif quest_item.item_type == "medkit":
                    sprite = pygame.image.load("assets/medkit/medkit.png").convert_alpha()
                    sprite = pygame.transform.scale(sprite, (30, 20))
                elif quest_item.item_type == "ammo":
                    sprite = pygame.image.load("assets/ammo/ammo.png").convert_alpha()
                    sprite = pygame.transform.scale(sprite, (25, 15))
                    
                if sprite:
                    screen.blit(sprite, (item_x, item_y))
                else:
                    # Fallback к цветным прямоугольникам
                    color = (255, 255, 0) if quest_item.item_type == "pistol" else (0, 255, 255)
                    pygame.draw.rect(screen, color, (item_x, item_y, 30, 20))
                    pygame.draw.rect(screen, (0, 0, 0), (item_x, item_y, 30, 20), 2)
                    
            except FileNotFoundError:
                # Fallback к цветным прямоугольникам если спрайт не найден
                if quest_item.item_type == "pistol":
                    color = (255, 255, 0)  # Жёлтый для пистолета
                elif quest_item.item_type == "armor":
                    color = (0, 255, 255)  # Циан для брони
                elif quest_item.item_type == "medkit":
                    color = (0, 255, 0)    # Зелёный для медкита
                elif quest_item.item_type == "ammo":
                    color = (255, 165, 0)  # Оранжевый для патронов
                else:
                    color = (255, 255, 255)  # Белый для остальных
                
                pygame.draw.rect(screen, color, (item_x, item_y, 30, 20))
                pygame.draw.rect(screen, (0, 0, 0), (item_x, item_y, 30, 20), 2)
