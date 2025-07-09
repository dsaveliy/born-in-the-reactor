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
        self.just_fired = False
        self.range = self.stats["range"]
        self.sprites = {
            "up": {
                "side": pygame.image.load(f"assets/weapons/{weapon_type.value}/up/side.png").convert_alpha(),
                "shoot": pygame.image.load(f"assets/weapons/{weapon_type.value}/up/shoot.png").convert_alpha(),
                "reload": pygame.image.load(f"assets/weapons/{weapon_type.value}/up/reload.png").convert_alpha()
            },
            "down": {
                "side": pygame.image.load(f"assets/weapons/{weapon_type.value}/down/side.png").convert_alpha(),
                "shoot": pygame.image.load(f"assets/weapons/{weapon_type.value}/down/shoot.png").convert_alpha(),
                "reload": pygame.image.load(f"assets/weapons/{weapon_type.value}/down/reload.png").convert_alpha()
            },
            "left": {
                "side": pygame.image.load(f"assets/weapons/{weapon_type.value}/left/side.png").convert_alpha(),
                "shoot": pygame.image.load(f"assets/weapons/{weapon_type.value}/left/shoot.png").convert_alpha(),
                "reload": pygame.image.load(f"assets/weapons/{weapon_type.value}/left/reload.png").convert_alpha()
            },
            "right": {
                "side": pygame.image.load(f"assets/weapons/{weapon_type.value}/right/side.png").convert_alpha(),
                "shoot": pygame.image.load(f"assets/weapons/{weapon_type.value}/right/shoot.png").convert_alpha(),
                "reload": pygame.image.load(f"assets/weapons/{weapon_type.value}/right/reload.png").convert_alpha()
            }
        }
        
        self.scale_sizes = {
            "up": {
                "side": (15, 45),
                "shoot": (15, 45),
                "reload": (45, 45)
            },
            "down": {
                "side": (15, 45),
                "shoot": (15, 45),
                "reload": (45, 45)
            },
            "left": {
                "side": (41, 25),
                "shoot": (41, 25),
                "reload": (41, 25)
            },
            "right": {
                "side": (41, 25),
                "shoot": (41, 25),
                "reload": (41, 25)
            }
        }

    def _get_weapon_stats(self):
        stats = {
            WeaponType.PISTOL: {
                "damage": 10,
                "fire_rate": 0.2,  # сек между выстрелами
                "max_ammo": 30,
                "reload_time": 1.5,
                "range": 300,
            },
            WeaponType.RIFLE: {
                "damage": 20,
                "fire_rate": 0.05,
                "max_ammo": 50,
                "reload_time": 2.0,
                "range": 400,
            },
            WeaponType.SHOTGUN: {
                "damage": 30,
                "fire_rate": 0.7,
                "max_ammo": 20,
                "reload_time": 2.5,
                "range": 200,
            }
        }
        return stats[self.type]
    
    def get_current_sprite_and_size(self, facing):
        if self.is_reloading:
            state = "reload"
        elif self.just_fired:
            state = "shoot"
        else:
            state = "side"
        sprite = self.sprites[facing][state]
        size = self.scale_sizes[facing][state]
        return sprite, size



    def update(self, dt):
        if self.cooldown > 0:
            self.cooldown -= dt
            
    def can_fire(self):
        return (self.ammo > 0 
                and self.cooldown <= 0 
                and not self.is_reloading)
    
    def fire(self):
        if not self.can_fire():
            return False
        self.just_fired = True    
        self.ammo -= 1
        self.cooldown = self.stats["fire_rate"]
        return True
    
    def start_reload(self):
        if self.ammo < self.stats["max_ammo"] and not self.is_reloading:
            self.is_reloading = True
            self.cooldown = self.stats["reload_time"]
    
    def finish_reload(self):
        if self.is_reloading and self.cooldown <= 0:
            self.ammo = self.stats["max_ammo"]
            self.is_reloading = False
    
    def render(self, screen, pos):
        # итоговая отрисовка оружия
        pass