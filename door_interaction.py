import pygame
from typing import Dict
from quest_system import QuestSystem, QuestEventType


class DoorInteractionHandler:
    def __init__(self, quest_system: QuestSystem):
        self.quest_system = quest_system
        self._door_touched = False
    
    def check_door_interaction(self, player_rect: pygame.Rect, door_zone: Dict) -> bool:
        door_rect = pygame.Rect(
            door_zone["x"], 
            door_zone["y"], 
            door_zone["width"], 
            door_zone["height"]
        )
        
        # check if player touches door
        is_touching_door = door_rect.colliderect(player_rect)
        
        # handle first door touch
        if is_touching_door and not self._door_touched:
            self._door_touched = True
            self.quest_system.trigger_event(QuestEventType.DOOR_TOUCHED)
        
        # check if can complete level
        return is_touching_door and self.quest_system.can_complete_level()
    
    def reset(self):
        self._door_touched = False