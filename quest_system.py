import pygame
from typing import Dict, List, Optional, Callable
from enum import Enum

class QuestEventType(Enum):
    # типы квестовых событий
    DOOR_TOUCHED = "door_touched"
    ITEM_COLLECTED = "item_collected"
    ENEMY_KILLED = "enemy_killed"

class QuestItem:
    def __init__(self, item_type: str, x: int, y: int, spawn_condition: str = None):
        self.item_type = item_type  # "pistol", "armor", "medkit" и др.
        self.x = x
        self.y = y
        self.spawn_condition = spawn_condition  # флаг для появления предмета
        self.is_spawned = False
        self.is_collected = False
    
    def can_spawn(self, quest_flags: Dict[str, bool]):
        # проверяет, может ли предмет появиться
        if self.spawn_condition is None:
            return True
        return quest_flags.get(self.spawn_condition, False)


class TextMessage:
    # представляет текстовое сообщение
    def __init__(self, text: str, duration: float = None, persistent: bool = False):
        self.text = text
        self.duration = duration  # None = показать один раз и убрать
        self.persistent = persistent  # True = показывать до конца уровня
        self.shown = False
        self.timer = 0.0


class QuestSystem:
    # основная система квестов
    def __init__(self):
        self._quest_flags: Dict[str, bool] = {}
        self._required_items: List[str] = []
        self._quest_items: List[QuestItem] = []
        self._text_messages: List[TextMessage] = []
        self._event_handlers: Dict[QuestEventType, List[Callable]] = {
            QuestEventType.DOOR_TOUCHED: [],
            QuestEventType.ITEM_COLLECTED: [],
            QuestEventType.ENEMY_KILLED: []
        }

        self.is_quest_completed = False
        self.current_message: Optional[TextMessage] = None
    
    def load_from_level_data(self, level_data: Dict):
        # загружает квестовые данные из JSON уровня
        quest_data = level_data.get("quest", {})
        # загружает требуемые предметы для прохождения
        self._required_items = quest_data.get("required_items", [])
        # загружаем квестовые предметы
        for item_data in quest_data.get("quest_items", []):
            quest_item = QuestItem(
                item_type=item_data["type"],
                x=item_data["x"],
                y=item_data["y"],
                spawn_condition=item_data.get("spawn_condition")
            )
            self._quest_items.append(quest_item)
        
        # загружаем текстовые сообщения
        for msg_data in quest_data.get("text_messages", []):
            message = TextMessage(
                text=msg_data["text"],
                duration=msg_data.get("duration"),
                persistent=msg_data.get("persistent", False)
            )
            self._text_messages.append(message)
    
    def set_flag(self, flag_name: str, value: bool = True):
        # устанавливает квестовый флаг
        self._quest_flags[flag_name] = value
        self._check_spawn_conditions()
    
    def get_flag(self, flag_name: str):
        # получает значение квестового флага
        return self._quest_flags.get(flag_name, False)
    
    def trigger_event(self, event_type: QuestEventType, data: Dict = None):
        # запускает квестовое событие
        if event_type == QuestEventType.DOOR_TOUCHED:
            self._handle_door_touched()
        elif event_type == QuestEventType.ITEM_COLLECTED:
            self._handle_item_collected(data.get("item_type"))
        
        for handler in self._event_handlers[event_type]:
            handler(data)

    def _handle_door_touched(self):
        # обрабатывает касание двери
        if not self.get_flag("door_touched_first_time"):
            self.set_flag("door_touched_first_time", True)
            self._show_next_message()
    
    def _handle_item_collected(self, item_type: str):
        # обрабатывает сбор предмета
        for quest_item in self._quest_items:
            if quest_item.item_type == item_type and not quest_item.is_collected:
                quest_item.is_collected = True
                break
        
        # проверяем завершение квеста
        self._check_quest_completion()
    
    def _check_spawn_conditions(self):
        # проверяет условия появления предметов
        for quest_item in self._quest_items:
            if not quest_item.is_spawned and quest_item.can_spawn(self._quest_flags):
                quest_item.is_spawned = True
    
    def _check_quest_completion(self):
        # проверяет завершение квеста
        collected_items = [item.item_type for item in self._quest_items 
                          if item.is_collected]
        
        # проверяем, собраны ли все требуемые предметы
        self.is_quest_completed = all(
            required_item in collected_items 
            for required_item in self._required_items
        )
    
    def _show_next_message(self):
        # показывает следующее сообщение в очереди
        for message in self._text_messages:
            if not message.shown:
                self.current_message = message
                message.shown = True
                break
    
    def update(self, dt: float):
        # обновляет систему квестов
        if self.current_message:
            if self.current_message.duration is not None:
                self.current_message.timer += dt
                if self.current_message.timer >= self.current_message.duration:
                    if not self.current_message.persistent:
                        self.current_message = None
                    self._show_next_message()
    
    def get_spawned_items(self):
        # возвращает список появившихся предметов
        return [item for item in self._quest_items if item.is_spawned and not item.is_collected]
    
    def can_complete_level(self):
        # проверяет, можно ли завершить уровень
        return self.is_quest_completed
    
    def register_event_handler(self, event_type: QuestEventType, handler: Callable):
        # регистрирует обработчик события (принцип открытости/закрытости)
        self._event_handlers[event_type].append(handler)


class TextDisplayManager:
    def __init__(self, font_path: str = None):
        try:
            self.font = pygame.font.Font(font_path or "assets/fonts/ShareTechMono-Regular.ttf", 13)
        except FileNotFoundError:
            self.font = pygame.font.Font(None, 13)
        
        self.text_color = (255, 255, 255)
        self.bg_color = (0, 0, 0, 150)
    
    def render_text_above_health(self, screen: pygame.Surface, text: str, health_bar_y: int):
        # отображает текст над полосой здоровья
        if not text:
            return
        
        # создаём текстовую поверхность
        text_surface = self.font.render(text, True, self.text_color)
        text_rect = text_surface.get_rect()
        screen_center_x = screen.get_width() // 2
        text_x = screen_center_x - text_rect.width // 2
        text_y = health_bar_y - 40  # на 40 пикселей выше полосы здоровья
        
        # фон для текста
        bg_rect = pygame.Rect(text_x - 10, text_y - 5, text_rect.width + 20, text_rect.height + 10)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill(self.bg_color)
        screen.blit(bg_surface, bg_rect.topleft)
        screen.blit(text_surface, (text_x, text_y))
