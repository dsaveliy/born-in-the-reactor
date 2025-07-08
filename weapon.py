import pygame
from enum import Enum
from typing import Dict, Tuple

class WeaponType(Enum):
    PISTOL = "pistol"
    RIFLE = "rifle"
    SHOTGUN = "shotgun"

class Weapon:
    def __init__(self, weapon_type):
        self.type = weapon_type
        self.stats = self._get_weapon_stats()
        self.ammo = self.stats["max_ammo"]
        self.cooldown = 0
        self.is_reloading = False
        
    def _get_weapon_stats(self):
        """Возвращает параметры оружия"""
        stats = {
            WeaponType.PISTOL: {
                "damage": 10,
                "fire_rate": 0.5,  # сек между выстрелами
                "max_ammo": 30,
                "reload_time": 1.5,
                "range": 300,
                "color": (150, 150, 150)  # серый
            },
            WeaponType.RIFLE: {
                "damage": 20,
                "fire_rate": 0.1,
                "max_ammo": 50,
                "reload_time": 2.0,
                "range": 400,
                "color": (100, 100, 100)  # темно-серый
            },
            WeaponType.SHOTGUN: {
                "damage": 30,
                "fire_rate": 1.0,
                "max_ammo": 20,
                "reload_time": 2.5,
                "range": 200,
                "color": (80, 80, 80)  # почти черный
            }
        }
        return stats[self.type]
    
    def update(self, dt):
        """Обновляет таймеры"""
        if self.cooldown > 0:
            self.cooldown -= dt
            
    def can_fire(self):
        """Можно ли совершить выстрел"""
        return (self.ammo > 0 
                and self.cooldown <= 0 
                and not self.is_reloading)
    
    def fire(self):
        """Совершает выстрел"""
        if not self.can_fire():
            return False
            
        self.ammo -= 1
        self.cooldown = self.stats["fire_rate"]
        return True
    
    def start_reload(self):
        """Начинает перезарядку"""
        if self.ammo < self.stats["max_ammo"] and not self.is_reloading:
            self.is_reloading = True
            self.cooldown = self.stats["reload_time"]
    
    def finish_reload(self):
        """Завершает перезарядку"""
        if self.is_reloading and self.cooldown <= 0:
            self.ammo = self.stats["max_ammo"]
            self.is_reloading = False
    
    def draw(self, screen: pygame.Surface, pos: Tuple[int, int]):
        """Отрисовывает оружие"""
        size = (20, 10)  # Ширина, Высота
        pygame.draw.rect(screen, self.stats["color"], 
                        (pos[0] - size[0]//2, pos[1] - size[1], 
                        size[0], size[1]))