import pygame
from typing import Dict, List, Optional
from enum import Enum


class ItemType(Enum):
    MEDKIT = "medkit"
    AMMO = "ammo"
    PISTOL = "pistol"


class InventoryItem:
    def __init__(self, item_type: ItemType, sprite_path: str, display_size: tuple = (35, 20)):
        self.item_type = item_type
        self.sprite_path = sprite_path
        self.display_size = display_size
        self.sprite = None
        
        # Убеждаемся, что pygame инициализирован
        if not pygame.get_init():
            pygame.init()
        
        # Загружаем спрайт
        try:
            self.original_sprite = pygame.image.load(sprite_path).convert_alpha()
            self.sprite = pygame.transform.scale(self.original_sprite, display_size)
            print(f"Successfully loaded sprite for {item_type.value} from {sprite_path}")
        except FileNotFoundError:
            print(f"Warning: Could not load sprite for {item_type.value} at {sprite_path}")
            # Создаём placeholder
            self.sprite = pygame.Surface(display_size)
            self.sprite.fill((150, 150, 150))
        except Exception as e:
            print(f"Error loading sprite for {item_type.value}: {e}")
            # Создаём placeholder
            self.sprite = pygame.Surface(display_size)
            self.sprite.fill((150, 150, 150))


class ItemManager:
    def __init__(self):
        self.inventory_slots: List[InventoryItem] = []  # Список слотов инвентаря
        self.item_templates: Dict[ItemType, Dict] = self._load_item_definitions()
        
        # Константы ограничений
        self.MAX_CONSUMABLE_SLOTS = 4
        self.consumable_types = {ItemType.MEDKIT, ItemType.AMMO}
        self.equipment_types = {ItemType.PISTOL}
    
    def _load_item_definitions(self) -> Dict[ItemType, Dict]:
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
                "sprite_path": "assets/weapons/pistol/right/side.png",
                "display_size": (40, 20)
            }
        }
    
    def can_add_item(self, item_type: ItemType, amount: int = 1) -> bool:
        if item_type in self.consumable_types:
            # Для расходных предметов - проверяем общий лимит
            current_consumables = sum(1 for item in self.inventory_slots 
                                    if item.item_type in self.consumable_types)
            return current_consumables + amount <= self.MAX_CONSUMABLE_SLOTS
        
        elif item_type in self.equipment_types:
            # Для экипировки - проверяем, есть ли уже такой предмет
            return not self.has_item(item_type)
        
        return False  # Неизвестный тип предмета
    
    def add_item(self, item_type: ItemType, amount: int = 1) -> bool:
        if not self.can_add_item(item_type, amount):
            if item_type in self.consumable_types:
                current_consumables = sum(1 for item in self.inventory_slots 
                                        if item.item_type in self.consumable_types)
                print(f"Cannot add {item_type.value}: consumable inventory full ({current_consumables}/{self.MAX_CONSUMABLE_SLOTS})")
            else:
                print(f"Cannot add {item_type.value}: already have this equipment")
            return False
        
        if item_type in self.item_templates:
            config = self.item_templates[item_type]
            added_count = 0
            for _ in range(amount):
                if self.can_add_item(item_type, 1):  # Проверяем перед каждым добавлением
                    new_item = InventoryItem(
                        item_type=item_type,
                        sprite_path=config["sprite_path"],
                        display_size=config["display_size"]
                    )
                    self.inventory_slots.append(new_item)
                    added_count += 1
                else:
                    break
            
            if added_count > 0:
                print(f"Added {added_count} {item_type.value}(s). Total slots: {len(self.inventory_slots)}")
            return added_count > 0
        
        return False
    
    def remove_item(self, item_type: ItemType, amount: int = 1) -> bool:
        removed = 0
        for i in range(len(self.inventory_slots) - 1, -1, -1):  # Идём с конца
            if self.inventory_slots[i].item_type == item_type and removed < amount:
                self.inventory_slots.pop(i)
                removed += 1
        
        success = removed == amount
        print(f"Tried to remove {amount} {item_type.value}(s). Removed: {removed}, Success: {success}")
        return success
    
    def get_item_count(self, item_type: ItemType) -> int:
        return sum(1 for item in self.inventory_slots if item.item_type == item_type)
    
    def has_item(self, item_type: ItemType) -> bool:
        return any(item.item_type == item_type for item in self.inventory_slots)
    
    def get_consumable_items(self) -> List[InventoryItem]:
        return [item for item in self.inventory_slots if item.item_type in self.consumable_types]
    
    def get_consumable_count(self) -> int:
        return sum(1 for item in self.inventory_slots if item.item_type in self.consumable_types)
    
    def get_inventory_status(self) -> str:
        consumable_count = self.get_consumable_count()
        equipment_items = [item.item_type.value for item in self.inventory_slots 
                          if item.item_type in self.equipment_types]
        
        status = f"Consumables: {consumable_count}/{self.MAX_CONSUMABLE_SLOTS}"
        if equipment_items:
            status += f", Equipment: {', '.join(equipment_items)}"
        return status
    
    def get_all_items_with_count(self) -> List[InventoryItem]:
        return self.inventory_slots.copy()
