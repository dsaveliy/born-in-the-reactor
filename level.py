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
        
        # Кэшируем изображения декоративных объектов
        self.cached_decor_objects = []
        for obj in self.objects_decor:
            try:
                image = pygame.image.load(obj["image"]).convert_alpha()
                scaled_image = pygame.transform.scale(image, (obj['width'], obj['height']))
                self.cached_decor_objects.append({
                    'image': scaled_image,
                    'x': obj['x'],
                    'y': obj['y']
                })
            except FileNotFoundError:
                print(f"Warning: Decor object image not found: {obj['image']}")
                self.cached_decor_objects.append({
                    'image': None,
                    'x': obj['x'],
                    'y': obj['y']
                })
        
        if self.transition_zone and "image" in self.transition_zone:
            self.door_image = pygame.image.load(self.transition_zone["image"]).convert_alpha()
            self.door_image = pygame.transform.scale( self.door_image, (self.transition_zone["width"],
                    self.transition_zone["height"]))
        else:
            self.door_image = None
        
        # Инициализация системы квестов
        self.quest_system = QuestSystem()
        self.quest_system.load_from_level_data(self.data)
        
        # Кэшируем спрайты квестовых предметов
        self.quest_item_sprites = {}
        quest_item_types = ["pistol", "medkit", "ammo"]
        for item_type in quest_item_types:
            try:
                if item_type == "pistol":
                    sprite = pygame.image.load("assets/weapons/pistol/right/side.png").convert_alpha()
                    sprite = pygame.transform.scale(sprite, (40, 25))
                elif item_type == "medkit":
                    sprite = pygame.image.load("assets/medkit/medkit.png").convert_alpha()
                    sprite = pygame.transform.scale(sprite, (30, 20))
                elif item_type == "ammo":
                    sprite = pygame.image.load("assets/ammo/ammo.png").convert_alpha()
                    sprite = pygame.transform.scale(sprite, (25, 15))
                
                self.quest_item_sprites[item_type] = sprite
            except FileNotFoundError:
                print(f"Warning: Quest item sprite not found: {item_type}")
                self.quest_item_sprites[item_type] = None

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
        
        for cached_obj in self.cached_decor_objects:
            if cached_obj['image']:
                screen.blit(cached_obj['image'], (cached_obj['x'] + camera_offset_x, cached_obj['y'] + camera_offset_y))

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
        for quest_item in self.quest_system.get_spawned_items():
            item_x = quest_item.x + camera_offset_x
            item_y = quest_item.y + camera_offset_y
            
            # Используем кэшированный спрайт
            sprite = self.quest_item_sprites.get(quest_item.item_type)
            if sprite:
                screen.blit(sprite, (item_x, item_y))
            else:
                # Fallback к цветным прямоугольникам
                if quest_item.item_type == "pistol":
                    color = (255, 255, 0)  # Жёлтый для пистолета
                elif quest_item.item_type == "medkit":
                    color = (0, 255, 0)    # Зелёный для медкита
                elif quest_item.item_type == "ammo":
                    color = (255, 165, 0)  # Оранжевый для патронов
                else:
                    color = (255, 255, 255)  # Белый для остальных
                
                pygame.draw.rect(screen, color, (item_x, item_y, 30, 20))
                pygame.draw.rect(screen, (0, 0, 0), (item_x, item_y, 30, 20), 2)
