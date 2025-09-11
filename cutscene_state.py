"""
Система катсцен с красивыми визуальными эффектами
Поддерживает fade эффекты, печатающийся текст, плавные переходы
"""

import pygame
import json
import math
from typing import Dict, List, Optional, Callable
from state import State, GameState
from enum import Enum


class CutscenePhase(Enum):
    BLACK_SCREEN = "black_screen"
    FADE_IN_FIRST = "fade_in_first"
    SHOW_FIRST_TEXT = "show_first_text"
    BLINK_WHITE = "blink_white"
    BLACK_PAUSE = "black_pause"
    SLOW_FADE_SECOND = "slow_fade_second"
    SHOW_SECOND_TEXT = "show_second_text"
    BLACK_TITLE_SCREEN = "black_title_screen"
    WAIT_FOR_INPUT = "wait_for_input"
    FADE_OUT = "fade_out"
    FINISHED = "finished"


class CutsceneConfig:
    """Конфигурация катсцены из JSON файла"""
    def __init__(self, config_dict: Dict):
        self.config = config_dict
        
        # Изображения
        self.background_image = config_dict.get("background_image")
        self.second_image = config_dict.get("second_image")
        
        # Тексты
        self.text = config_dict.get("text", "")
        self.second_text = config_dict.get("second_text", "")
        
        # Тайминги (в секундах)
        self.black_duration = config_dict.get("black_duration", 0.0)
        self.first_fade_duration = config_dict.get("first_fade_duration", 0.0)
        self.text_duration = config_dict.get("text_duration", 0.0)
        self.blink_duration = config_dict.get("blink_duration", 0.0)
        self.black_pause_duration = config_dict.get("black_pause_duration", 0.0)
        self.slow_fade_duration = config_dict.get("slow_fade_duration", 0.0)
        self.second_text_duration = config_dict.get("second_text_duration", 0.0)
        self.title_screen_duration = config_dict.get("title_screen_duration", 0.0)
        self.fade_duration = config_dict.get("fade_duration", 0.0)
        
        # Скорость печати текста
        self.chars_per_second = config_dict.get("chars_per_second", 8)
        self.second_chars_per_second = config_dict.get("second_chars_per_second", 8)
        
        # Определяем последовательность фаз на основе наличия полей
        self.phases = self._build_phase_sequence()
    
    def _build_phase_sequence(self) -> List[CutscenePhase]:
        """Строит последовательность фаз на основе конфигурации"""
        phases = []
        
        # Всегда начинаем с черного экрана
        phases.append(CutscenePhase.BLACK_SCREEN)
        
        # Если есть первое изображение
        if self.background_image:
            if self.first_fade_duration > 0:
                phases.append(CutscenePhase.FADE_IN_FIRST)
            
            if self.text and self.text_duration > 0:
                phases.append(CutscenePhase.SHOW_FIRST_TEXT)
            
            # Если есть второе изображение
            if self.second_image:
                if self.blink_duration > 0:
                    phases.append(CutscenePhase.BLINK_WHITE)
                
                if self.black_pause_duration > 0:
                    phases.append(CutscenePhase.BLACK_PAUSE)
                
                if self.slow_fade_duration > 0:
                    phases.append(CutscenePhase.SLOW_FADE_SECOND)
                
                if self.second_text and self.second_text_duration > 0:
                    phases.append(CutscenePhase.SHOW_SECOND_TEXT)
        
        # Если есть заголовок (только для intro катсцены)
        if self.title_screen_duration > 0:
            phases.append(CutscenePhase.BLACK_TITLE_SCREEN)
        
        # Если есть ожидание ввода
        if self.config.get("wait_for_input", False):
            phases.append(CutscenePhase.WAIT_FOR_INPUT)
        
        # Если есть fade out
        if self.fade_duration > 0:
            phases.append(CutscenePhase.FADE_OUT)
        
        phases.append(CutscenePhase.FINISHED)
        return phases
    
    def has_phase(self, phase: CutscenePhase) -> bool:
        """Проверяет, есть ли фаза в последовательности"""
        return phase in self.phases
    
    def get_phase_duration(self, phase: CutscenePhase) -> float:
        """Возвращает длительность фазы"""
        duration_map = {
            CutscenePhase.BLACK_SCREEN: self.black_duration,
            CutscenePhase.FADE_IN_FIRST: self.first_fade_duration,
            CutscenePhase.SHOW_FIRST_TEXT: self.text_duration,
            CutscenePhase.BLINK_WHITE: self.blink_duration,
            CutscenePhase.BLACK_PAUSE: self.black_pause_duration,
            CutscenePhase.SLOW_FADE_SECOND: self.slow_fade_duration,
            CutscenePhase.SHOW_SECOND_TEXT: self.second_text_duration,
            CutscenePhase.BLACK_TITLE_SCREEN: self.title_screen_duration,
            CutscenePhase.WAIT_FOR_INPUT: 0.0,  # Бесконечное ожидание
            CutscenePhase.FADE_OUT: self.fade_duration,
        }
        return duration_map.get(phase, 0.0)


class VisualEffect:
    """Базовый класс для визуальных эффектов"""
    def __init__(self, duration: float):
        self.duration = duration
        self.timer = 0.0
        self.finished = False
    
    def update(self, dt: float):
        self.timer += dt
        if self.timer >= self.duration:
            self.finished = True
    
    def get_progress(self) -> float:
        """Возвращает прогресс от 0.0 до 1.0"""
        return min(self.timer / self.duration, 1.0)


class FadeEffect(VisualEffect):
    """Эффект затухания/появления"""
    def __init__(self, duration: float, fade_in: bool = True):
        super().__init__(duration)
        self.fade_in = fade_in
    
    def get_alpha(self) -> int:
        progress = self.get_progress()
        if self.fade_in:
            return int(255 * progress)
        else:
            return int(255 * (1.0 - progress))


class TypewriterEffect(VisualEffect):
    """Эффект печатающейся машинки для текста"""
    def __init__(self, text: str, duration: float, chars_per_second: float = None):
        super().__init__(duration)
        self.full_text = text
        if chars_per_second is not None:
            self.chars_per_second = chars_per_second
        else:
            self.chars_per_second = len(text) / duration if duration > 0 else len(text)
    
    def get_visible_text(self) -> str:
        chars_to_show = int(self.timer * self.chars_per_second)
        return self.full_text[:chars_to_show]


class BlurEffect(VisualEffect):
    """Эффект размытия изображения"""
    def __init__(self, duration: float, blur_in: bool = True):
        super().__init__(duration)
        self.blur_in = blur_in
    
    def get_blur_strength(self) -> float:
        """Возвращает силу размытия от 0.0 до 1.0"""
        progress = self.get_progress()
        if self.blur_in:
            return progress  # 0.0 → 1.0 (размывается)
        else:
            return 1.0 - progress  # 1.0 → 0.0 (проясняется)

class BlinkEffect(VisualEffect):
    """Эффект белого моргания"""
    def __init__(self, duration: float):
        super().__init__(duration)
    
    def get_white_alpha(self) -> int:
        """Возвращает альфу белого экрана от 0 до 255"""
        progress = self.get_progress()
        # Быстрое появление и исчезновение белого
        if progress < 0.3:
            return int(255 * (progress / 0.3))  # 0 → 255
        else:
            return int(255 * (1.0 - (progress - 0.3) / 0.7))  # 255 → 0

class PulseEffect:
    """Пульсирующий эффект для кнопок"""
    def __init__(self, speed: float = 2.0, min_scale: float = 0.9, max_scale: float = 1.1):
        self.speed = speed
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.timer = 0.0
    
    def update(self, dt: float):
        self.timer += dt * self.speed
    
    def get_scale(self) -> float:
        pulse = math.sin(self.timer) * 0.5 + 0.5  # 0.0 to 1.0
        return self.min_scale + pulse * (self.max_scale - self.min_scale)


class CutsceneState(State):
    """
    Гибкая система катсцен на основе JSON конфигурации
    
    Поддерживает:
    - Динамическую последовательность фаз на основе JSON
    - Независимые методы отрисовки
    - Гибкую настройку таймингов
    - Автоматическое определение необходимых фаз
    """
    
    def __init__(self, game):
        super().__init__(game)
        
        # Визуальные настройки
        self.screen_width = 800
        self.screen_height = 600
        
        # Загрузка шрифтов
        try:
            self.title_font = pygame.font.Font("assets/fonts/Orbitron-Bold.ttf", 48)
            self.text_font = pygame.font.Font("assets/fonts/ShareTechMono-Regular.ttf", 24)
            self.button_font = pygame.font.Font("assets/fonts/Orbitron-Bold.ttf", 28)
        except FileNotFoundError:
            print("Warning: Custom fonts not found, using default")
            self.title_font = pygame.font.Font(None, 48)
            self.text_font = pygame.font.Font(None, 24)
            self.button_font = pygame.font.Font(None, 28)
        
        # Конфигурация катсцены
        self.config: Optional[CutsceneConfig] = None
        self.current_phase_index = 0
        self.current_phase = CutscenePhase.BLACK_SCREEN
        self.phase_timer = 0.0
        
        # Эффекты
        self.fade_effect: Optional[FadeEffect] = None
        self.typewriter_effect: Optional[TypewriterEffect] = None
        self.blink_effect: Optional[BlinkEffect] = None
        self.second_typewriter_effect: Optional[TypewriterEffect] = None
        self.pulse_effect = PulseEffect()
        
        # Ресурсы
        self.background_image: Optional[pygame.Surface] = None
        self.second_image: Optional[pygame.Surface] = None
        
        # Навигация
        self.next_state: Optional[GameState] = None
        self.next_state_kwargs: Dict = {}
        self.action_triggered = False
    
    def load_cutscene(self, cutscene_path: str, next_state: GameState = None, **kwargs):
        """Загружает катсцену из JSON файла"""
        try:
            with open(cutscene_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # Создаем конфигурацию
            self.config = CutsceneConfig(config_dict)
            self.next_state = next_state
            self.next_state_kwargs = kwargs
            
            # Загружаем изображения если они есть в конфигурации
            self._load_images()
            
            # Сброс состояния
            self._reset_state()
            
        except FileNotFoundError:
            print(f"Error: Cutscene file not found: {cutscene_path}")
            self._finish_cutscene()
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in cutscene file: {cutscene_path}")
            self._finish_cutscene()
    
    def _load_images(self):
        """Загружает изображения из конфигурации"""
        if self.config.background_image:
            try:
                self.background_image = pygame.image.load(
                    self.config.background_image
                ).convert()
                self.background_image = pygame.transform.scale(
                    self.background_image, (self.screen_width, self.screen_height)
                )
            except FileNotFoundError:
                print(f"Warning: Background image not found: {self.config.background_image}")
                self.background_image = None
        
        if self.config.second_image:
            try:
                self.second_image = pygame.image.load(
                    self.config.second_image
                ).convert()
                self.second_image = pygame.transform.scale(
                    self.second_image, (self.screen_width, self.screen_height)
                )
            except FileNotFoundError:
                print(f"Warning: Second image not found: {self.config.second_image}")
                self.second_image = None
    
    def _reset_state(self):
        """Сбрасывает состояние катсцены"""
        if not self.config:
            return
            
        self.current_phase_index = 0
        self.current_phase = self.config.phases[0] if self.config.phases else CutscenePhase.FINISHED
        self.phase_timer = 0.0
        self.fade_effect = None
        self.typewriter_effect = None
        self.blink_effect = None
        self.second_typewriter_effect = None
        self.action_triggered = False
    
    def enter(self):
        """Вход в состояние катсцены"""
        print("Entered Cutscene State")
        if not self.config:
            print("Warning: No cutscene loaded, finishing immediately")
            self._finish_cutscene()
    
    def exit(self):
        """Выход из состояния катсцены"""
        print("Exiting Cutscene State")
    
    def update(self, dt: float):
        """Обновление логики катсцены"""
        if not self.config:
            return
        
        self.phase_timer += dt
        self.pulse_effect.update(dt)
        
        # Обновление текущих эффектов
        self._update_effects(dt)
        
        # Проверяем, нужно ли перейти к следующей фазе
        if self._should_advance_phase():
            self._advance_to_next_phase()
        
        # Обработка ввода для интерактивных фаз
        if self.current_phase in [CutscenePhase.BLACK_TITLE_SCREEN, CutscenePhase.WAIT_FOR_INPUT]:
            self._handle_input()
    
    def _update_effects(self, dt: float):
        """Обновляет все активные эффекты"""
        if self.fade_effect:
            self.fade_effect.update(dt)
        
        if self.typewriter_effect:
            self.typewriter_effect.update(dt)
        
        if self.blink_effect:
            self.blink_effect.update(dt)
        
        if self.second_typewriter_effect:
            self.second_typewriter_effect.update(dt)
    
    def _should_advance_phase(self) -> bool:
        """Проверяет, нужно ли перейти к следующей фазе"""
        if not self.config:
            return False
        
        # Получаем длительность текущей фазы
        phase_duration = self.config.get_phase_duration(self.current_phase)
        
        # Если фаза имеет определенную длительность
        if phase_duration > 0:
            return self.phase_timer >= phase_duration
        
        # Специальная логика для фаз с эффектами
        if self.current_phase == CutscenePhase.FADE_IN_FIRST:
            return self.fade_effect and self.fade_effect.finished
        
        elif self.current_phase == CutscenePhase.SHOW_FIRST_TEXT:
            return self.typewriter_effect and self.typewriter_effect.finished
        
        elif self.current_phase == CutscenePhase.BLINK_WHITE:
            return self.blink_effect and self.blink_effect.finished
        
        elif self.current_phase == CutscenePhase.SLOW_FADE_SECOND:
            return self.fade_effect and self.fade_effect.finished
        
        elif self.current_phase == CutscenePhase.SHOW_SECOND_TEXT:
            if self.second_typewriter_effect and self.second_typewriter_effect.finished:
                # Дополнительная задержка после завершения печати
                return self.phase_timer >= 3.0
            return False
        
        # Для интерактивных фаз не переходим автоматически
        elif self.current_phase in [CutscenePhase.BLACK_TITLE_SCREEN, CutscenePhase.WAIT_FOR_INPUT]:
            return False
        
        elif self.current_phase == CutscenePhase.FADE_OUT:
            return self.fade_effect and self.fade_effect.finished
        
        return False
    
    def _advance_to_next_phase(self):
        """Переходит к следующей фазе"""
        if not self.config:
            return
        
        # Специальная логика для intro катсцены - после второго текста показываем заголовок
        if (self.current_phase == CutscenePhase.SHOW_SECOND_TEXT and 
            self.config.background_image and self.config.second_image and
            not self.config.has_phase(CutscenePhase.BLACK_TITLE_SCREEN)):
            # Переходим к заголовку напрямую
            self.current_phase = CutscenePhase.BLACK_TITLE_SCREEN
            self.phase_timer = 0.0
            return
        
        self.current_phase_index += 1
        
        # Проверяем, есть ли следующая фаза
        if self.current_phase_index < len(self.config.phases):
            self.current_phase = self.config.phases[self.current_phase_index]
            self.phase_timer = 0.0
            
            # Инициализируем эффекты для новой фазы
            self._initialize_phase_effects()
        else:
            # Катсцена завершена
            self._finish_cutscene()
    
    def _initialize_phase_effects(self):
        """Инициализирует эффекты для текущей фазы"""
        if not self.config:
            return
        
        # Сбрасываем все эффекты
        self.fade_effect = None
        self.typewriter_effect = None
        self.blink_effect = None
        self.second_typewriter_effect = None
        
        # Инициализируем эффекты в зависимости от фазы
        if self.current_phase == CutscenePhase.FADE_IN_FIRST:
            duration = self.config.get_phase_duration(self.current_phase)
            self.fade_effect = FadeEffect(duration, fade_in=True)
        
        elif self.current_phase == CutscenePhase.SHOW_FIRST_TEXT:
            duration = self.config.get_phase_duration(self.current_phase)
            self.typewriter_effect = TypewriterEffect(
                self.config.text, duration, 
                chars_per_second=self.config.chars_per_second
            )
        
        elif self.current_phase == CutscenePhase.BLINK_WHITE:
            duration = self.config.get_phase_duration(self.current_phase)
            self.blink_effect = BlinkEffect(duration)
        
        elif self.current_phase == CutscenePhase.SLOW_FADE_SECOND:
            duration = self.config.get_phase_duration(self.current_phase)
            self.fade_effect = FadeEffect(duration, fade_in=True)
        
        elif self.current_phase == CutscenePhase.SHOW_SECOND_TEXT:
            duration = self.config.get_phase_duration(self.current_phase)
            self.second_typewriter_effect = TypewriterEffect(
                self.config.second_text, duration,
                chars_per_second=self.config.second_chars_per_second
            )
        
        elif self.current_phase == CutscenePhase.FADE_OUT:
            duration = self.config.get_phase_duration(self.current_phase)
            self.fade_effect = FadeEffect(duration, fade_in=False)
    
    
    def _handle_input(self):
        """Обрабатывает ввод пользователя"""
        keys = pygame.key.get_pressed()

        if (keys[pygame.K_RETURN] or keys[pygame.K_SPACE]) and not self.action_triggered:
            self.action_triggered = True

            if self.current_phase == CutscenePhase.BLACK_TITLE_SCREEN:
                # После нажатия Enter на заголовке сразу завершаем катсцену
                self._finish_cutscene()
            elif self.current_phase == CutscenePhase.WAIT_FOR_INPUT:
                # После нажатия Enter переходим к следующей фазе
                self._advance_to_next_phase()

        if not (keys[pygame.K_RETURN] or keys[pygame.K_SPACE]):
            self.action_triggered = False
    
    
    def _finish_cutscene(self):
        """Завершает катсцену и переходит к следующему состоянию"""
        self.current_phase = CutscenePhase.FINISHED
        
        if self.next_state:
            # Если нужно сменить уровень после катсцены
            if self.next_state == GameState.GAMEPLAY and "target_level" in self.next_state_kwargs:
                target_level = self.next_state_kwargs.pop("target_level")
                self.game.change_state(self.next_state, **self.next_state_kwargs)
                # Меняем уровень после перехода к геймплею
                gameplay_state = self.game.states[GameState.GAMEPLAY]
                gameplay_state.change_level(target_level)
            else:
                self.game.change_state(self.next_state, **self.next_state_kwargs)
        else:
            # По умолчанию возвращаемся в главное меню
            self.game.change_state(GameState.MAIN_MENU)
    
    def render(self, screen: pygame.Surface):
        """Отрисовка катсцены"""
        if not self.config:
            return
        
        # Очищаем экран
        screen.fill((0, 0, 0))
        
        # Рисуем фоновые изображения в зависимости от фазы
        self._render_backgrounds(screen)
        
        # Применяем эффекты
        self._render_effects(screen)
        
        # Рисуем тексты и интерфейс
        self._render_ui(screen)
    
    def _render_backgrounds(self, screen: pygame.Surface):
        """Отрисовывает фоновые изображения"""
        # Рисуем первое изображение
        if (self.background_image and 
            self.current_phase in [CutscenePhase.FADE_IN_FIRST, CutscenePhase.SHOW_FIRST_TEXT, CutscenePhase.BLINK_WHITE]):
            screen.blit(self.background_image, (0, 0))
        
        # Рисуем второе изображение
        if (self.second_image and 
            self.current_phase in [CutscenePhase.SLOW_FADE_SECOND, CutscenePhase.SHOW_SECOND_TEXT, CutscenePhase.WAIT_FOR_INPUT]):
            screen.blit(self.second_image, (0, 0))
    
    def _render_effects(self, screen: pygame.Surface):
        """Отрисовывает визуальные эффекты"""
        # Fade эффект для первого изображения
        if (self.current_phase == CutscenePhase.FADE_IN_FIRST and 
            self.fade_effect and not self.fade_effect.finished):
            fade_alpha = 255 - self.fade_effect.get_alpha()
            if fade_alpha > 0:
                fade_surface = pygame.Surface((self.screen_width, self.screen_height))
                fade_surface.fill((0, 0, 0))
                fade_surface.set_alpha(fade_alpha)
                screen.blit(fade_surface, (0, 0))
        
        # Fade эффект для второго изображения
        if (self.current_phase == CutscenePhase.SLOW_FADE_SECOND and 
            self.fade_effect and not self.fade_effect.finished):
            fade_alpha = 255 - self.fade_effect.get_alpha()
            if fade_alpha > 0:
                fade_surface = pygame.Surface((self.screen_width, self.screen_height))
                fade_surface.fill((0, 0, 0))
                fade_surface.set_alpha(fade_alpha)
                screen.blit(fade_surface, (0, 0))
        
        # Белое моргание
        if (self.current_phase == CutscenePhase.BLINK_WHITE and 
            self.blink_effect and not self.blink_effect.finished):
            white_alpha = self.blink_effect.get_white_alpha()
            if white_alpha > 0:
                white_surface = pygame.Surface((self.screen_width, self.screen_height))
                white_surface.fill((255, 255, 255))
                white_surface.set_alpha(white_alpha)
                screen.blit(white_surface, (0, 0))
    
    def _render_ui(self, screen: pygame.Surface):
        """Отрисовывает пользовательский интерфейс"""
        # Первый текст
        if self.current_phase == CutscenePhase.SHOW_FIRST_TEXT:
            self._draw_text_bottom(screen)
        
        # Второй текст
        if self.current_phase == CutscenePhase.SHOW_SECOND_TEXT:
            self._draw_second_text_bottom(screen)
        
        # Заголовок игры
        if self.current_phase == CutscenePhase.BLACK_TITLE_SCREEN:
            self._draw_title_screen(screen)
        
        # Кнопка продолжения
        if self.current_phase == CutscenePhase.WAIT_FOR_INPUT:
            self._draw_continue_button(screen)
    
    def _draw_gradient_background(self, screen: pygame.Surface):
        """Рисует градиентный фон"""
        for y in range(self.screen_height):
            progress = y / self.screen_height
            color_r = int(10 + progress * 30)  # От темно-серого к серому
            color_g = int(5 + progress * 20)
            color_b = int(20 + progress * 40)
            pygame.draw.line(screen, (color_r, color_g, color_b), (0, y), (self.screen_width, y))
    
    def _draw_title(self, screen: pygame.Surface):
        """Рисует заголовок катсцены"""
        title = self.current_cutscene.get("title", "")
        if title:
            title_surface = self.title_font.render(title, True, (255, 255, 255))
            title_rect = title_surface.get_rect(center=(self.screen_width // 2, 100))
            
            # Добавляем тень для лучшей читаемости
            shadow_surface = self.title_font.render(title, True, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect(center=(self.screen_width // 2 + 2, 102))
            screen.blit(shadow_surface, shadow_rect)
            screen.blit(title_surface, title_rect)
    
    def _draw_text_bottom(self, screen: pygame.Surface):
        """Рисует первый текст внизу экрана"""
        if not self.typewriter_effect:
            return
        
        visible_text = self.typewriter_effect.get_visible_text()
        if not visible_text:
            return
        
        # Разбиваем текст на строки
        lines = self._wrap_text(visible_text, self.text_font, self.screen_width - 100)
        
        # Позиционируем текст внизу экрана
        y_offset = self.screen_height - 150
        line_height = self.text_font.get_height() + 5
        
        for i, line in enumerate(lines):
            text_surface = self.text_font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, y_offset + i * line_height))
            
            # Тень для текста
            shadow_surface = self.text_font.render(line, True, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect(center=(self.screen_width // 2 + 2, y_offset + i * line_height + 2))
            screen.blit(shadow_surface, shadow_rect)
            screen.blit(text_surface, text_rect)
    
    def _draw_second_text_bottom(self, screen: pygame.Surface):
        """Рисует второй текст внизу экрана"""
        if not self.second_typewriter_effect:
            return
        
        visible_text = self.second_typewriter_effect.get_visible_text()
        if not visible_text:
            return
        
        # Разбиваем текст на строки
        lines = self._wrap_text(visible_text, self.text_font, self.screen_width - 100)
        
        # Позиционируем текст внизу экрана
        y_offset = self.screen_height - 150
        line_height = self.text_font.get_height() + 5
        
        for i, line in enumerate(lines):
            text_surface = self.text_font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, y_offset + i * line_height))
            
            # Тень для текста
            shadow_surface = self.text_font.render(line, True, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect(center=(self.screen_width // 2 + 2, y_offset + i * line_height + 2))
            screen.blit(shadow_surface, shadow_rect)
            screen.blit(text_surface, text_rect)
    
    def _draw_second_image(self, screen: pygame.Surface):
        """Рисует второе изображение с blur эффектом"""
        if not self.second_image:
            return
        
        # Применяем blur эффект если нужно
        if self.current_phase == CutscenePhase.BLUR_TRANSITION and self.blur_effect:
            blur_strength = self.blur_effect.get_blur_strength()
            # Создаем размытую версию изображения
            blurred_image = self._apply_blur(self.second_image, blur_strength)
            screen.blit(blurred_image, (0, 0))
        else:
            # Обычное изображение
            screen.blit(self.second_image, (0, 0))
    
    def _draw_second_text(self, screen: pygame.Surface):
        """Рисует второй текст с эффектом печатания"""
        if not self.second_typewriter_effect:
            return
        
        visible_text = self.second_typewriter_effect.get_visible_text()
        if not visible_text:
            return
        
        # Разбиваем текст на строки
        lines = self._wrap_text(visible_text, self.text_font, self.screen_width - 100)
        
        y_offset = self.screen_height // 2
        line_height = self.text_font.get_height() + 5
        
        for i, line in enumerate(lines):
            text_surface = self.text_font.render(line, True, (220, 220, 220))  # Чуть светлее для контраста
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, y_offset + i * line_height))
            
            # Тень для текста
            shadow_surface = self.text_font.render(line, True, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect(center=(self.screen_width // 2 + 1, y_offset + i * line_height + 1))
            screen.blit(shadow_surface, shadow_rect)
            screen.blit(text_surface, text_rect)
    
    def _draw_title_screen(self, screen: pygame.Surface):
        """Рисует черный экран с заголовком 'born in the reactor' по центру"""
        # Черный фон уже установлен в render()
        
        # Заголовок игры
        title_text = "born in the reactor"
        
        # Используем большой шрифт для заголовка
        try:
            title_font = pygame.font.Font("assets/fonts/Orbitron-Bold.ttf", 64)
        except FileNotFoundError:
            title_font = pygame.font.Font(None, 64)
        
        # Рендерим заголовок
        title_surface = title_font.render(title_text, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        
        # Добавляем тень для лучшей читаемости
        shadow_surface = title_font.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(self.screen_width // 2 + 3, self.screen_height // 2 + 3))
        
        # Рисуем тень и заголовок
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(title_surface, title_rect)

        # Добавляем подсказку о нажатии Enter
        hint_text = "Press ENTER to continue"
        hint_font = pygame.font.Font(None, 24)
        hint_surface = hint_font.render(hint_text, True, (200, 200, 200))
        hint_rect = hint_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 80))

        # Тень для подсказки
        hint_shadow = hint_font.render(hint_text, True, (0, 0, 0))
        hint_shadow_rect = hint_shadow.get_rect(center=(self.screen_width // 2 + 1, self.screen_height // 2 + 81))

        screen.blit(hint_shadow, hint_shadow_rect)
        screen.blit(hint_surface, hint_rect)
    
    def _draw_continue_button(self, screen: pygame.Surface):
        """Рисует простую кнопку продолжения без анимаций"""
        button_text = "Press ENTER to continue"
        # Используем меньший шрифт
        small_font = pygame.font.Font(None, 20)
        button_surface = small_font.render(button_text, True, (255, 255, 255))
        button_rect = button_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
        
        # Простая тень
        shadow_surface = small_font.render(button_text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(self.screen_width // 2 + 1, self.screen_height - 19))
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(button_surface, button_rect)
    
    def _draw_particles(self, screen: pygame.Surface):
        """Рисует простые частицы для атмосферы"""
        # Простые "звездочки" для атмосферы
        import random
        for i in range(20):
            x = (self.phase_timer * 10 + i * 40) % self.screen_width
            y = (i * 30) % self.screen_height
            alpha = int(128 * (math.sin(self.phase_timer + i) * 0.5 + 0.5))
            
            particle_surface = pygame.Surface((2, 2))
            particle_surface.fill((100, 150, 255))
            particle_surface.set_alpha(alpha)
            screen.blit(particle_surface, (x, y))
    
    def _apply_blur(self, surface: pygame.Surface, blur_strength: float) -> pygame.Surface:
        """Применяет blur эффект к поверхности"""
        if blur_strength <= 0:
            return surface
        
        # Простая реализация blur через масштабирование
        # В реальной игре можно использовать более сложные алгоритмы
        blur_factor = int(1 + blur_strength * 3)  # От 1 до 4
        
        # Уменьшаем изображение
        small_width = max(1, surface.get_width() // blur_factor)
        small_height = max(1, surface.get_height() // blur_factor)
        small_surface = pygame.transform.scale(surface, (small_width, small_height))
        
        # Увеличиваем обратно
        blurred = pygame.transform.scale(small_surface, (surface.get_width(), surface.get_height()))
        
        # Добавляем затемнение для эффекта потери сознания
        if blur_strength > 0.5:
            darken_factor = (blur_strength - 0.5) * 2  # 0.0 → 1.0
            darken_surface = pygame.Surface(blurred.get_size())
            darken_surface.fill((0, 0, 0))
            darken_surface.set_alpha(int(darken_factor * 100))
            blurred.blit(darken_surface, (0, 0), special_flags=pygame.BLEND_MULT)
        
        return blurred
    
    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """Разбивает текст на строки по ширине"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
