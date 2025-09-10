import pygame
from state import State, GameState
from player import Player
from level import Level
from settings_state import SettingsState
from weapon import Weapon, WeaponType
from hitscan import HitscanShot
from effects import DamageEffect
from quest_system import QuestEventType, TextDisplayManager
from door_interaction import DoorInteractionHandler
from inventory_items import ItemType

class GameplayState:
    def __init__(self, game):
        self.game = game
        self.settings = SettingsState(game)  # Create a temporary SettingsState instance
        self.current_level = self.settings.get_initial_level()
        self.enemies_killed = 0  # Track score
        player_settings = self.settings.get_player_settings()
        
        # Загрузка шрифта для HUD
        try:
            self.hud_font = pygame.font.Font("assets/fonts/ShareTechMono-Regular.ttf", 16)
            self.hud_title_font = pygame.font.Font("assets/fonts/Orbitron-Bold.ttf", 18)
        except FileNotFoundError:
            print("Error loading HUD fonts, using default")
            self.hud_font = pygame.font.Font(None, 16)
            self.hud_title_font = pygame.font.Font(None, 18)
        
        # Загрузка аватара игрока
        try:
            self.player_avatar = pygame.image.load(player_settings.get("photo", "assets/player/default_avatar.png")).convert_alpha()
            self.player_avatar = pygame.transform.scale(self.player_avatar, (30, 30))
        except FileNotFoundError:
            print("Error loading player avatar, using placeholder")
            self.player_avatar = pygame.Surface((30, 30))
            self.player_avatar.fill((100, 100, 100))
        
        # Загрузка картинок оружий для HUD
        self.weapon_icons = {}
        self.weapon_reload_icons = {}
        weapon_types = ["pistol", "rifle", "shotgun"]
        for weapon_type in weapon_types:
            try:
                if weapon_type == "rifle":
                    # У винтовки картинки в подпапках, берем right/side.png
                    icon_path = f"assets/weapons/{weapon_type}/right/side.png"
                    reload_path = f"assets/weapons/{weapon_type}/right/reload.png"
                else:
                    # У пистолета и дробовика картинки в корне папки
                    icon_path = f"assets/weapons/{weapon_type}/side.png"
                    reload_path = f"assets/weapons/{weapon_type}/reload.png"
                
                # Обычная картинка оружия
                icon = pygame.image.load(icon_path).convert_alpha()
                self.weapon_icons[weapon_type] = pygame.transform.scale(icon, (80, 40))
                
                # Картинка перезарядки
                reload_icon = pygame.image.load(reload_path).convert_alpha()
                self.weapon_reload_icons[weapon_type] = pygame.transform.scale(reload_icon, (80, 40))
            except FileNotFoundError:
                print(f"Error loading weapon icon for {weapon_type}")
                # Создаем placeholder
                self.weapon_icons[weapon_type] = pygame.Surface((80, 40))
                self.weapon_icons[weapon_type].fill((150, 150, 150))
                self.weapon_reload_icons[weapon_type] = pygame.Surface((80, 40))
                self.weapon_reload_icons[weapon_type].fill((150, 150, 150))
        
        self.player_nickname = player_settings.get("nickname", "Survivor")
        
        self.levels = { # загрузка уровней
            "gomel_streets": Level("assets/lvls/gomel.json"),
            "hospital": Level("assets/lvls/hospital.json")
        }
        level = self.levels[self.current_level]
        self.player = Player( # создание игрока
            x=level.player_spawn['x'],
            y=level.player_spawn['y'],
            health=player_settings.get("initial_health", 100),
            ammo=player_settings.get("initial_ammo", 0),
            inventory={ WeaponType[item.upper()] for item in player_settings.get("inventory", []) 
                    if item in ["pistol", "rifle", "shotgun"] },
            aim_line=player_settings.get("aim_line", 1),
        )
        self.tracers = []
        self.damage_effect = DamageEffect()
        
        # Инициализация квестовой системы
        self.text_display_manager = TextDisplayManager()
        self.door_handler = DoorInteractionHandler(self.levels[self.current_level].quest_system)

    def update(self, dt):
        # Обновление квестовой системы
        current_level = self.levels[self.current_level]
        current_level.quest_system.update(dt)
        
        # проверка прохода двери с квестовой логикой
        if current_level.transition_zone:
            player_rect = pygame.Rect(
                self.player.world_x - self.player.width//2,
                self.player.world_y - self.player.height//2,
                self.player.width, 
                self.player.height
            )

            # Используем новый обработчик двери
            if self.door_handler.check_door_interaction(player_rect, current_level.transition_zone):
                self.change_level(current_level.transition_zone["target_level"])
                return
        # действия на клавиатуре
        # движение
        keys = pygame.key.get_pressed()
        move_direction = None
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and (keys[pygame.K_a] or keys[pygame.K_LEFT]):
            move_direction = "up_left"
        elif (keys[pygame.K_w] or keys[pygame.K_UP]) and (keys[pygame.K_d] or keys[pygame.K_RIGHT]):
            move_direction = "up_right"
        elif (keys[pygame.K_s] or keys[pygame.K_DOWN]) and (keys[pygame.K_a] or keys[pygame.K_LEFT]):
            move_direction = "down_left"
        elif (keys[pygame.K_s] or keys[pygame.K_DOWN]) and (keys[pygame.K_d] or keys[pygame.K_RIGHT]):
            move_direction = "down_right"
        elif keys[pygame.K_w] or keys[pygame.K_UP]:
            move_direction = "up"
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_direction = "down"
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_direction = "left"
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_direction = "right"
        
        if move_direction:
            self.player.move(move_direction, self.levels[self.current_level])
        # смена оружия
        if keys[pygame.K_1]:
            self.player.switch_weapon(WeaponType.PISTOL)
        if keys[pygame.K_2]:
            self.player.switch_weapon(WeaponType.RIFLE)
        if keys[pygame.K_3]:
            self.player.switch_weapon(WeaponType.SHOTGUN)
        # перезарядка (только один раз за нажатие)
        if keys[pygame.K_r] and not getattr(self, '_r_key_pressed', False):
            self.player.reload()
            self._r_key_pressed = True
        elif not keys[pygame.K_r]:
            self._r_key_pressed = False
        # использование медкита (только один раз за нажатие)
        if keys[pygame.K_h] and not getattr(self, '_h_key_pressed', False):
            self.player.use_medkit()
            self._h_key_pressed = True
        elif not keys[pygame.K_h]:
            self._h_key_pressed = False
        # действия на мыши
        # выстрелы
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # лкм
            result = self.player.hitscan_fire(self.levels[self.current_level],
                    camera_offset=pygame.Vector2(self.player.world_x - 400, self.player.world_y - 300))
            if result:
                start, end, dmg = result
                self.tracers.append(HitscanShot(start, end, dmg)) # выстрел
                # Check for enemy kills
                for enemy in self.levels[self.current_level].enemies[:]:
                    enemy_rect = pygame.Rect(enemy.position.x, enemy.position.y, enemy.width, enemy.height)
                    if enemy_rect.clipline(start, end) and enemy.health <= 0 and not enemy.is_dead:
                        self.enemies_killed += 1  # Increment score

        # обновление трейсеров
        for tracer in self.tracers[:]:
            tracer.update(dt)
            if not tracer.is_alive():
                self.tracers.remove(tracer)
        # обновление объектов
        self.player.update(dt)
        
        # Проверка сбора квестовых предметов
        self._check_quest_item_collection(current_level)

        # if self.player.health <= 0:
        #     self.game.change_state(GameState.MAIN_MENU)
        #     self.player.health = 100
        if self.player.health <= 0:
            print(f"Player died, transitioning to GameOverState with score: {self.enemies_killed}")
            self.game.change_state(GameState.GAME_OVER, score=self.enemies_killed)
            self.reset_game()  # Reset game state

        for enemy in self.levels[self.current_level].enemies:
            if enemy.update(dt, self.levels[self.current_level], self.player):
                self.levels[self.current_level].enemies.remove(enemy)
                self.enemies_killed += 1  # Increment score for enemies killed by other means
        # эффект крови
        current_health = self.player.health
        if hasattr(self, 'last_health') and current_health < self.last_health:
            self.damage_effect.trigger()
        self.last_health = current_health
        
        self.damage_effect.update(dt)
    
    def _check_quest_item_collection(self, level):
        """Проверяет сбор квестовых предметов игроком"""
        player_rect = pygame.Rect(
            self.player.world_x - self.player.width//2,
            self.player.world_y - self.player.height//2,
            self.player.width, 
            self.player.height
        )
        
        for quest_item in level.quest_system.get_spawned_items():
            item_rect = pygame.Rect(quest_item.x, quest_item.y, 30, 20)
            
            if player_rect.colliderect(item_rect):
                # Помечаем предмет как собранный СРАЗУ
                quest_item.is_collected = True
                
                # Предмет собран
                level.quest_system.trigger_event(
                    QuestEventType.ITEM_COLLECTED, 
                    {"item_type": quest_item.item_type}
                )
                
                # Добавляем предмет в инвентарь игрока
                if quest_item.item_type == "pistol":
                    self.player.inventory.add(WeaponType.PISTOL)
                    if WeaponType.PISTOL not in self.player.weapons:
                        self.player.weapons[WeaponType.PISTOL] = Weapon(WeaponType.PISTOL)
                    self.player.add_item(ItemType.PISTOL)
                elif quest_item.item_type == "armor":
                    self.player.add_item(ItemType.ARMOR)
                elif quest_item.item_type == "medkit":
                    self.player.add_item(ItemType.MEDKIT)
                elif quest_item.item_type == "ammo":
                    self.player.add_item(ItemType.AMMO)
                
                print(f"Collected {quest_item.item_type}!")
                break  # Собираем только ОДИН предмет за кадр


    def render(self, screen):
        self.levels[self.current_level].render(screen, self.player.world_x, self.player.world_y) # сначала рисуем уровень(с учетом позиции игрока)
        for enemy in self.levels[self.current_level].enemies: # враги
            enemy.render(screen, camera_offset=pygame.Vector2(self.player.world_x - 400, self.player.world_y - 300))
        for tracer in self.tracers: # прицел
            tracer.render(screen)

        # отрисовка наводки
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            aim_start, aim_end = self.player.get_aim_line()
            offset = pygame.Vector2(self.player.world_x - 400, self.player.world_y - 300)
            pygame.draw.line(screen, (200, 200, 50), aim_start - offset, aim_end - offset, 1)

        self.player.render(screen) # игрок

        # эффект крови
        screen_rect = screen.get_rect()
        self.damage_effect.render(screen, screen_rect)

        # отрисовка HUD
        self._render_hud(screen)
        
        # отрисовка квестового текста над полосой здоровья
        current_level = self.levels[self.current_level]
        if current_level.quest_system.current_message:
            # Находим Y-позицию полосы здоровья (из _render_health_bar)
            health_bar_y = screen.get_height() - 50
            self.text_display_manager.render_text_above_health(
                screen, 
                current_level.quest_system.current_message.text, 
                health_bar_y
            )

    def _render_hud(self, screen):
        """Отрисовка креативного HUD в разных частях экрана"""
        # Получаем информацию об оружии
        weapon = None
        if self.player.current_weapon and self.player.current_weapon in self.player.weapons:
            weapon = self.player.weapons[self.player.current_weapon]
        
        # Получаем название уровня
        level_name = self.levels[self.current_level].name
        
        # 1. Левый верхний угол - Аватар, имя и уровень
        self._render_player_info(screen, level_name)
        
        # 2. Правый нижний угол - Большой логотип активного оружия
        self._render_weapon_info(screen, weapon)
        
        # 3. Левый нижний угол - Компактный инвентарь
        self._render_inventory(screen)
        
        # 4. Нижний центр - Здоровье (креативно)
        self._render_health_bar(screen)
    
    def _render_player_info(self, screen, level_name):
        """Отрисовка информации о игроке в левом верхнем углу"""
        # Создаем фон для блока игрока
        info_width = 200
        info_height = 80
        info_surface = pygame.Surface((info_width, info_height), pygame.SRCALPHA)
        
        # Рисуем полупрозрачный фон с градиентом
        pygame.draw.rect(info_surface, (0, 0, 0, 120), (0, 0, info_width, info_height))
        pygame.draw.rect(info_surface, (100, 100, 255, 80), (0, 0, info_width, info_height), 2)
        
        # Аватар и никнейм
        info_surface.blit(self.player_avatar, (10, 10))
        nickname_text = self.hud_title_font.render(self.player_nickname, True, (255, 255, 255))
        info_surface.blit(nickname_text, (50, 15))
        
        # Название уровня
        level_text = self.hud_font.render(f"Level: {level_name}", True, (200, 200, 255))
        info_surface.blit(level_text, (10, 45))
        
        screen.blit(info_surface, (10, 10))
    
    def _render_weapon_info(self, screen, weapon):
        """Отрисовка большого логотипа активного оружия справа"""
        # Если нет оружия - не отображаем блок
        if weapon is None:
            return
            
        # Создаем фон для блока оружия
        weapon_width = 120  # Уменьшили в 1.5 раза (180/1.5 = 120)
        weapon_height = 67   # Уменьшили в 1.5 раза (100/1.5 ≈ 67)
        weapon_surface = pygame.Surface((weapon_width, weapon_height), pygame.SRCALPHA)
        
        # Добавляем легкую красную подсветку во время перезарядки
        if weapon.is_reloading:
            # Полупрозрачный красный фон
            pygame.draw.rect(weapon_surface, (255, 100, 100, 50), (0, 0, weapon_width, weapon_height))
            # Красная рамка
            #pygame.draw.rect(weapon_surface, (255, 150, 150, 150), (0, 0, weapon_width, weapon_height), 2)
        
        # Большая картинка текущего оружия
        if weapon.is_reloading:
            # Используем картинку перезарядки
            current_weapon_icon = self.weapon_reload_icons.get(weapon.type.value, self.weapon_reload_icons["rifle"])
        else:
            # Используем обычную картинку оружия
            current_weapon_icon = self.weapon_icons.get(weapon.type.value, self.weapon_icons["rifle"])
        
        weapon_surface.blit(current_weapon_icon, (20, 7))  # Скорректировали позицию
        
        # Боеприпасы обычным шрифтом (уменьшили размер)
        if weapon.is_reloading:
            # Во время перезарядки делаем патроны ярко-красными
            ammo_color = (255, 50, 50)
        else:
            # Обычная цветовая схема патронов
            ammo_color = (255, 100, 100) if weapon.ammo < 5 else (255, 255, 100) if weapon.ammo < 15 else (100, 255, 100)
        
        ammo_text = self.hud_font.render(f"{weapon.ammo}/{weapon.stats['max_ammo']}", True, ammo_color)
        ammo_rect = ammo_text.get_rect(center=(weapon_width//2, 53))  # Скорректировали позицию
        weapon_surface.blit(ammo_text, ammo_rect)
        
        # Убираем текст перезарядки - теперь используется картинка
        
        # Позиционируем в правом нижнем углу
        screen.blit(weapon_surface, (screen.get_width() - weapon_width - 10, screen.get_height() - weapon_height - 15))
    
    def _render_inventory(self, screen):
        """Отрисовка компактного инвентаря слева"""
        # Создаем фон для инвентаря
        inv_width = 200
        inv_height = 120
        inv_surface = pygame.Surface((inv_width, inv_height), pygame.SRCALPHA)
        
        # Заголовок инвентаря
        inventory_text = self.hud_font.render("Inventory:", True, (200, 200, 200))
        inv_surface.blit(inventory_text, (10, 10))
        
        # Первая строка - оружие (пистолет, автомат, дробовик)
        weapon_y = 35
        weapon_icon_x = 10
        
        # Список всех типов оружия для отображения
        weapon_types_to_show = ["pistol", "rifle", "shotgun"]
        
        for weapon_key in weapon_types_to_show:
            if weapon_key in self.weapon_icons:
                # Увеличенные иконки для оружия
                weapon_icon = pygame.transform.scale(self.weapon_icons[weapon_key], (40, 20))
                
                # Проверяем, есть ли это оружие в инвентаре и активно ли оно
                weapon_in_inventory = False
                is_current_weapon = False
                
                for weapon_type in self.player.inventory:
                    weapon_type_key = weapon_type.value if hasattr(weapon_type, 'value') else str(weapon_type)
                    if weapon_type_key == weapon_key:
                        weapon_in_inventory = True
                        if weapon_type == self.player.current_weapon:
                            is_current_weapon = True
                        break
                
                # Если оружие есть в инвентаре, показываем его
                if weapon_in_inventory:
                    inv_surface.blit(weapon_icon, (weapon_icon_x, weapon_y))
                #else:
                    # # Показываем серую версию для отсутствующего оружия
                    # gray_icon = pygame.transform.scale(self.weapon_icons[weapon_key], (40, 20))
                    # gray_surface = pygame.Surface(gray_icon.get_size(), pygame.SRCALPHA)
                    # gray_surface.fill((100, 100, 100, 100))
                    # gray_icon.blit(gray_surface, (0, 0), special_flags=pygame.BLEND_MULT)
                    # inv_surface.blit(gray_icon, (weapon_icon_x, weapon_y))
                
                weapon_icon_x += 50
        
        # Вторая строка - слоты для расходных предметов (медкиты, патроны)
        consumables_y = 65
        slot_x = 10
        
        # Получаем все предметы в инвентаре
        all_items = self.player.item_manager.get_all_items_with_count()
        consumable_items = [item for item in all_items if item.item_type in [ItemType.MEDKIT, ItemType.AMMO]]
        
        # Показываем слоты для расходных предметов
        max_slots = 4  # 4 слота для предметов
        for i in range(max_slots):
            slot_rect = pygame.Rect(slot_x, consumables_y, 35, 20)
            
            if i < len(consumable_items):
                # Есть предмет для отображения
                item = consumable_items[i]
                
                # Рисуем фон слота (зелёный если есть предметы)
                pygame.draw.rect(inv_surface, (50, 100, 50, 150), slot_rect)
                pygame.draw.rect(inv_surface, (100, 200, 100, 200), slot_rect, 1)
                
                # Рисуем спрайт предмета
                if item.sprite:
                    sprite_rect = item.sprite.get_rect(center=slot_rect.center)
                    inv_surface.blit(item.sprite, sprite_rect)
                
                # Убираем счётчики - каждый слот = 1 предмет
            else:
                # Пустой слот
                pygame.draw.rect(inv_surface, (50, 50, 50, 150), slot_rect)
                pygame.draw.rect(inv_surface, (100, 100, 100, 200), slot_rect, 1)
                
                # Добавляем знак "+" для обозначения пустого слота
                plus_text = self.hud_font.render("+", True, (150, 150, 150))
                plus_rect = plus_text.get_rect(center=slot_rect.center)
                inv_surface.blit(plus_text, plus_rect)
            
            slot_x += 40  # Уменьшаем расстояние между слотами
        
        # Позиционируем в левом нижнем углу, но чуть выше
        screen.blit(inv_surface, (10, screen.get_height() - inv_height + 5))
    
    def _render_health_bar(self, screen):
        """Креативная отрисовка здоровья в нижнем центре"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Размеры полосы здоровья
        bar_width = 300
        bar_height = 25
        bar_x = (screen_width - bar_width) // 2
        bar_y = screen_height - 50
        
        # Создаем поверхность для полосы здоровья
        health_surface = pygame.Surface((bar_width + 20, bar_height + 20), pygame.SRCALPHA)
        
        # Фон полосы здоровья
        pygame.draw.rect(health_surface, (0, 0, 0, 150), (10, 10, bar_width, bar_height))
        pygame.draw.rect(health_surface, (50, 50, 50, 200), (10, 10, bar_width, bar_height), 2)
        
        # Цвет здоровья в зависимости от процента
        health_percent = self.player.health / 100
        if health_percent > 0.7:
            health_color = (100, 255, 100, 210)  # Зеленый
        elif health_percent > 0.3:
            health_color = (255, 255, 100, 210)  # Желтый
        else:
            health_color = (255, 100, 100, 210)  # Красный
        
        # Полоса здоровья
        current_width = int(bar_width * health_percent)
        pygame.draw.rect(health_surface, health_color, (10, 10, current_width, bar_height))
        
        # Текст здоровья
        health_text = self.hud_font.render(f"{self.player.health}/100", True, (255, 255, 255))
        text_rect = health_text.get_rect(center=(bar_width//2 + 10, bar_height//2 + 10))
        health_surface.blit(health_text, text_rect)
        
        screen.blit(health_surface, (bar_x - 10, bar_y - 10))

    def change_level(self, new_level):
        self.current_level = new_level
        self.settings.data["initial_level"] = new_level
        self.settings.save_settings()
        # перемещаем игрока на точку спавна нового уровня
        level = self.levels[new_level]
        self.player.world_x = level.player_spawn['x']
        self.player.world_y = level.player_spawn['y']
        
        # Обновляем обработчик двери для нового уровня
        self.door_handler = DoorInteractionHandler(level.quest_system)
        self.door_handler.reset()

    def enter(self):
        pass

    def exit(self):
        pass
