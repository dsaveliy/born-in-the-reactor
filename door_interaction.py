"""
Обработчик взаимодействия с дверью
Принцип единственной ответственности: только логика двери
"""

import pygame
from typing import Dict, Optional
from quest_system import QuestSystem, QuestEventType


class DoorInteractionHandler:
    """
    Обрабатывает взаимодействие игрока с дверью
    Инкапсулирует логику проверки условий прохождения
    """
    
    def __init__(self, quest_system: QuestSystem):
        self.quest_system = quest_system
        self._door_touched = False
        self._last_door_state = False
    
    def check_door_interaction(self, player_rect: pygame.Rect, door_zone: Dict) -> bool:
        """
        Проверяет взаимодействие игрока с дверью
        Возвращает True, если можно перейти на следующий уровень
        """
        door_rect = pygame.Rect(
            door_zone["x"], 
            door_zone["y"], 
            door_zone["width"], 
            door_zone["height"]
        )
        
        is_touching_door = door_rect.contains(player_rect)
        
        # Обрабатываем первое касание двери
        if is_touching_door and not self._door_touched:
            self._door_touched = True
            self.quest_system.trigger_event(QuestEventType.DOOR_TOUCHED)
        
        # Проверяем, можно ли пройти уровень
        if is_touching_door and self.quest_system.can_complete_level():
            return True
        
        return False
    
    def reset(self):
        """Сбрасывает состояние для нового уровня"""
        self._door_touched = False
        self._last_door_state = False
