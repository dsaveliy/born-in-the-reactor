"""
Система предметов инвентаря
Управляет загрузкой, отображением и логикой предметов
"""

import pygame
from typing import Dict, List, Optional
from enum import Enum


class ItemType(Enum):
    """Типы предметов"""
    MEDKIT = "medkit"
    AMMO = "ammo"
    PISTOL = "pistol" 
    ARMOR = "armor"


class InventoryItem:
    """Представляет предмет в инвентаре"""
    
    def __init__(self, item_type: ItemType, sprite_path: str, display_size: tuple = (35, 20)):
        self.item_type = item_type
        self.sprite_path = sprite_path
        self.display_size = display_size
        self.sprite = None
        
        # Загружаем спрайт
        try:
            self.original_sprite = pygame.image.load(sprite_path).convert_alpha()
            self.sprite = pygame.transform.scale(self.original_sprite, display_size)
        except FileNotFoundError:
            print(f"Warning: Could not load sprite for {item_type.value} at {sprite_path}")
            # Создаём placeholder
            self.sprite = pygame.Surface(display_size)
            self.sprite.fill((150, 150, 150))


class ItemManager:
    """
    Менеджер предметов инвентаря
    Принцип единственной ответственности: только управление предметами
    Каждый слот = 1 предмет
    """
    
    def __init__(self):
        self.inventory_slots: List[InventoryItem] = []  # Список слотов инвентаря
        self.item_templates: Dict[ItemType, Dict] = self._load_item_definitions()
    
    def _load_item_definitions(self) -> Dict[ItemType, Dict]:
        """Загружает шаблоны предметов"""
        return {
            ItemType.MEDKIT: {
                "sprite_path": "assets/medkit/medkit.png",
                "display_size": (35, 20)
            },
            ItemType.AMMO: {
                "sprite_path": "assets/ammo/ammo.png", 
                "display_size": (35, 20)
            },
            ItemType.PISTOL: {
                "sprite_path": "assets/weapons/pistol/side.png",
                "display_size": (40, 20)
            },
            ItemType.ARMOR: {
                "sprite_path": "assets/weapons/pistol/side.png",  # Временно, пока нет спрайта брони
                "display_size": (35, 20)
            }
        }
    
    def add_item(self, item_type: ItemType, amount: int = 1):
        """Добавляет предмет в инвентарь (каждый в отдельный слот)"""
        if item_type in self.item_templates:
            config = self.item_templates[item_type]
            for _ in range(amount):
                new_item = InventoryItem(
                    item_type=item_type,
                    sprite_path=config["sprite_path"],
                    display_size=config["display_size"]
                )
                self.inventory_slots.append(new_item)
            print(f"Added {amount} {item_type.value}(s). Total slots: {len(self.inventory_slots)}")
    
    def remove_item(self, item_type: ItemType, amount: int = 1) -> bool:
        """Удаляет предмет из инвентаря"""
        removed = 0
        for i in range(len(self.inventory_slots) - 1, -1, -1):  # Идём с конца
            if self.inventory_slots[i].item_type == item_type and removed < amount:
                self.inventory_slots.pop(i)
                removed += 1
        
        success = removed == amount
        print(f"Tried to remove {amount} {item_type.value}(s). Removed: {removed}, Success: {success}")
        return success
    
    def get_item_count(self, item_type: ItemType) -> int:
        """Получает количество предметов"""
        return sum(1 for item in self.inventory_slots if item.item_type == item_type)
    
    def has_item(self, item_type: ItemType) -> bool:
        """Проверяет наличие предмета"""
        return any(item.item_type == item_type for item in self.inventory_slots)
    
    def get_consumable_items(self) -> List[InventoryItem]:
        """Возвращает список расходных предметов для отображения в HUD"""
        consumables = [ItemType.MEDKIT, ItemType.AMMO]
        return [item for item in self.inventory_slots if item.item_type in consumables]
    
    def get_all_items_with_count(self) -> List[InventoryItem]:
        """Возвращает все предметы в слотах"""
        return self.inventory_slots.copy()
