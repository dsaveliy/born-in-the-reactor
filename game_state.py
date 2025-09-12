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
        self.settings = SettingsState(game)  # создаем временный экземпляр настроек
        self.current_level = self.settings.get_initial_level()
        self.enemies_killed = 0  # отслеживаем счет
        player_settings = self.settings.get_player_settings()
        self.levels_completed = 0 # for points in changing level
        
        # загружаем шрифты для hud
        try:
            self.hud_font = pygame.font.Font("assets/fonts/ShareTechMono-Regular.ttf", 16)
            self.hud_title_font = pygame.font.Font("assets/fonts/Orbitron-Bold.ttf", 18)
        except FileNotFoundError:
            print("Error loading HUD fonts, using default")
            self.hud_font = pygame.font.Font(None, 16)
            self.hud_title_font = pygame.font.Font(None, 18)
        
        # кэшируем часто используемые тексты
        self.text_cache = {}
        
        # загружаем аватар игрока
        try:
            self.player_avatar = pygame.image.load(player_settings.get("photo", "assets/player/default_avatar.png")).convert_alpha()
            self.player_avatar = pygame.transform.scale(self.player_avatar, (30, 30))
        except FileNotFoundError:
            print("Error loading player avatar, using placeholder")
            self.player_avatar = pygame.Surface((30, 30))
            self.player_avatar.fill((100, 100, 100))
        
        # загружаем иконки оружия для hud
        self.weapon_icons = {}
        self.weapon_reload_icons = {}
        weapon_types = ["pistol", "rifle", "shotgun"]
        for weapon_type in weapon_types:
            try:
                if weapon_type == "rifle":
                    # у винтовки картинки в подпапках, берем right/side.png
                    icon_path = f"assets/weapons/{weapon_type}/right/side.png"
                    reload_path = f"assets/weapons/{weapon_type}/right/reload.png"
                elif weapon_type == "pistol":
                    # у пистолета картинки в подпапке right
                    icon_path = f"assets/weapons/{weapon_type}/right/side.png"
                    reload_path = f"assets/weapons/{weapon_type}/right/reload.png"
                elif weapon_type == "shotgun":
                    # у дробовика картинки в подпапке right
                    icon_path = f"assets/weapons/{weapon_type}/right/side.png"
                    reload_path = f"assets/weapons/{weapon_type}/right/reload.png"
                else:
                    # Fallback для неизвестных типов оружия
                    icon_path = f"assets/weapons/{weapon_type}/side.png"
                    reload_path = f"assets/weapons/{weapon_type}/reload.png"
                
                # обычная картинка оружия
                icon = pygame.image.load(icon_path).convert_alpha()
                self.weapon_icons[weapon_type] = pygame.transform.scale(icon, (80, 40))
                
                # картинка перезарядки
                reload_icon = pygame.image.load(reload_path).convert_alpha()
                self.weapon_reload_icons[weapon_type] = pygame.transform.scale(reload_icon, (80, 40))
            except FileNotFoundError:
                print(f"Error loading weapon icon for {weapon_type}")
                # создаем placeholder
                self.weapon_icons[weapon_type] = pygame.Surface((80, 40))
                self.weapon_icons[weapon_type].fill((150, 150, 150))
                self.weapon_reload_icons[weapon_type] = pygame.Surface((80, 40))
                self.weapon_reload_icons[weapon_type].fill((150, 150, 150))
        
        self.player_nickname = player_settings.get("nickname", "Survivor")
        
        self.levels = { # загружаем уровни
            "gomel_streets": Level("assets/lvls/gomel.json"),
            "home": Level("assets/lvls/home.json")
        }
        level = self.levels[self.current_level]
        self.player = Player( # создаем игрока
            x=level.player_spawn['x'],
            y=level.player_spawn['y'],
            health=player_settings.get("initial_health", 100),
            ammo=player_settings.get("initial_ammo", 0),
            inventory={ WeaponType[item.upper()] for item in player_settings.get("inventory", []) 
                    if item in ["pistol", "rifle", "shotgun"] },
            aim_line=player_settings.get("aim_line", 1),
            game=self.game,
        )
        self.tracers = []
        self.damage_effect = DamageEffect()
        
        # инициализация квестовой системы
        self.text_display_manager = TextDisplayManager()
        self.door_handler = DoorInteractionHandler(self.levels[self.current_level].quest_system)
        
        # загружаем и воспроизводим фоновую музыку (только если не играет)
        if hasattr(self.game, 'audio_manager'):
            self.game.audio_manager.load_music("assets/sounds/background_music.wav")
            # проверяем, не играет ли уже музыка
            if not pygame.mixer.music.get_busy():
                self.game.audio_manager.play_music()

    def update(self, dt):
        # обновляем квестовую систему
        current_level = self.levels[self.current_level]
        current_level.quest_system.update(dt)
        
        # проверяем проход двери с квестовой логикой
        if current_level.transition_zone:
            player_rect = pygame.Rect(
                self.player.world_x - self.player.width//2,
                self.player.world_y - self.player.height//2,
                self.player.width, 
                self.player.height
            )

            # используем новый обработчик двери
            if self.door_handler.check_door_interaction(player_rect, current_level.transition_zone):
                target_level = current_level.transition_zone["target_level"]
                print("Playing home escape cutscene")
                self.game.play_cutscene(
                    "assets/cutscenes/home_escape.json", 
                    GameState.GAMEPLAY,
                    target_level=target_level
                )
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
                
                # звук выстрела
                if self.player.current_weapon:
                    weapon_type = self.player.current_weapon.value
                    if weapon_type == "pistol":
                        self.game.audio_manager.play_sound('shoot_pistol')
                    elif weapon_type == "rifle":
                        self.game.audio_manager.play_sound('shoot_rifle')
                    elif weapon_type == "shotgun":
                        self.game.audio_manager.play_sound('shoot_shotgun')
                # Check for enemy kills
                for enemy in self.levels[self.current_level].enemies[:]:
                    enemy_rect = pygame.Rect(enemy.position.x, enemy.position.y, enemy.width, enemy.height)
                    if enemy_rect.clipline(start, end) and enemy.health <= 0 and not enemy.is_dead:
                        self.enemies_killed += 1  # Increment score

        # обновляем трейсеры
        for tracer in self.tracers[:]:
            tracer.update(dt)
            if not tracer.is_alive():
                self.tracers.remove(tracer)
        # обновляем объекты
        self.player.update(dt)
        
        # проверяем сбор квестовых предметов
        self._check_quest_item_collection(current_level)

        # if self.player.health <= 0:
        #     self.game.change_state(GameState.MAIN_MENU)
        #     self.player.health = 100
        if self.player.health <= 0:
            print(f"Player died, transitioning to GameOverState with score: {self.enemies_killed}")
            self.game.change_state(GameState.GAME_OVER, score=self.enemies_killed)
            self.reset_game()  # Reset game state

        # обновляем врагов с оптимизацией - не каждый кадр
        for i, enemy in enumerate(self.levels[self.current_level].enemies):
            # обновляем каждого врага через кадр для экономии ресурсов
            if i % 2 == 0 or len(self.levels[self.current_level].enemies) < 5:
                if enemy.update(dt, self.levels[self.current_level], self.player):
                    self.levels[self.current_level].enemies.remove(enemy)
                    self.enemies_killed += 1  # увеличиваем счет за убитых врагов
        # эффект крови
        current_health = self.player.health
        if hasattr(self, 'last_health') and current_health < self.last_health:
            self.damage_effect.trigger()
        self.last_health = current_health
        
        self.damage_effect.update(dt)
    
    def _get_cached_text(self, text, font, color=(255, 255, 255)):
        """Получает кэшированный текст или создает новый"""
        cache_key = f"{text}_{font}_{color}"
        if cache_key not in self.text_cache:
            self.text_cache[cache_key] = font.render(text, True, color)
        return self.text_cache[cache_key]
    
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
                # проверяем, можно ли добавить предмет в инвентарь
                item_added = False
                
                if quest_item.item_type == "pistol":
                    # проверяем, можно ли добавить пистолет
                    if self.player.item_manager.can_add_item(ItemType.PISTOL):
                        self.player.inventory.add(WeaponType.PISTOL)
                        if WeaponType.PISTOL not in self.player.weapons:
                            self.player.weapons[WeaponType.PISTOL] = Weapon(WeaponType.PISTOL)
                            # устанавливаем поднятое оружие как активное
                            self.player.current_weapon = WeaponType.PISTOL
                        item_added = self.player.add_item(ItemType.PISTOL)
                    else:
                        print(f"Cannot collect {quest_item.item_type}: inventory full!")
                        
                        
                elif quest_item.item_type == "medkit":
                    if self.player.item_manager.can_add_item(ItemType.MEDKIT):
                        item_added = self.player.add_item(ItemType.MEDKIT)
                    else:
                        print(f"Cannot collect {quest_item.item_type}: consumable inventory full!")
                        
                elif quest_item.item_type == "ammo":
                    if self.player.item_manager.can_add_item(ItemType.AMMO):
                        item_added = self.player.add_item(ItemType.AMMO)
                    else:
                        print(f"Cannot collect {quest_item.item_type}: consumable inventory full!")
                
                # если предмет был успешно добавлен, помечаем его как собранный
                if item_added:
                    quest_item.is_collected = True
                    
                    # предмет собран
                    level.quest_system.trigger_event(
                        QuestEventType.ITEM_COLLECTED, 
                        {"item_type": quest_item.item_type}
                    )
                    
                    print(f"Collected {quest_item.item_type}!")
                    print(f"Inventory status: {self.player.item_manager.get_inventory_status()}")
                
                break  # обрабатываем только один предмет за кадр


    def render(self, screen):
        self.levels[self.current_level].render(screen, self.player.world_x, self.player.world_y) # сначала рисуем уровень (с учетом позиции игрока)
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

        # отрисовка hud
        self._render_hud(screen)
        
        # отрисовка квестового текста над полосой здоровья
        current_level = self.levels[self.current_level]
        if current_level.quest_system.current_message:
            # находим y-позицию полосы здоровья (из _render_health_bar)
            health_bar_y = screen.get_height() - 50
            self.text_display_manager.render_text_above_health(
                screen, 
                current_level.quest_system.current_message.text, 
                health_bar_y
            )

    def _render_hud(self, screen):
        # отрисовка креативного hud в разных частях экрана
        # получаем информацию об оружии
        weapon = None
        if self.player.current_weapon and self.player.current_weapon in self.player.weapons:
            weapon = self.player.weapons[self.player.current_weapon]
        
        # получаем название уровня
        level_name = self.levels[self.current_level].name
        
        # 1. левый верхний угол - аватар, имя и уровень
        self._render_player_info(screen, level_name)
        
        # 2. правый нижний угол - большой логотип активного оружия
        self._render_weapon_info(screen, weapon)
        
        # 3. левый нижний угол - компактный инвентарь
        self._render_inventory(screen)
        
        # 4. нижний центр - здоровье (креативно)
        self._render_health_bar(screen)
    
    def _render_player_info(self, screen, level_name):
        # отрисовка информации о игроке в левом верхнем углу
        # создаем фон для блока игрока
        info_width = 200
        info_height = 80
        info_surface = pygame.Surface((info_width, info_height), pygame.SRCALPHA)
        
        # рисуем полупрозрачный фон с градиентом
        pygame.draw.rect(info_surface, (0, 0, 0, 120), (0, 0, info_width, info_height))
        pygame.draw.rect(info_surface, (100, 100, 255, 80), (0, 0, info_width, info_height), 2)
        
        # аватар и никнейм
        info_surface.blit(self.player_avatar, (10, 10))
        nickname_text = self.hud_title_font.render(self.player_nickname, True, (255, 255, 255))
        info_surface.blit(nickname_text, (50, 15))
        
        # название уровня
        level_text = self.hud_font.render(f"Level: {level_name}", True, (200, 200, 255))
        info_surface.blit(level_text, (10, 45))
        
        screen.blit(info_surface, (10, 10))
    
    def _render_weapon_info(self, screen, weapon):
        # отрисовка большого логотипа активного оружия справа
        # если нет оружия - не отображаем блок
        if weapon is None:
            return
            
        # создаем фон для блока оружия
        weapon_width = 120  # уменьшили в 1.5 раза (180/1.5 = 120)
        weapon_height = 67   # уменьшили в 1.5 раза (100/1.5 ≈ 67)
        weapon_surface = pygame.Surface((weapon_width, weapon_height), pygame.SRCALPHA)
        
        # добавляем легкую красную подсветку во время перезарядки
        if weapon.is_reloading:
            # полупрозрачный красный фон
            pygame.draw.rect(weapon_surface, (255, 100, 100, 50), (0, 0, weapon_width, weapon_height))
            # красная рамка
            #pygame.draw.rect(weapon_surface, (255, 150, 150, 150), (0, 0, weapon_width, weapon_height), 2)
        
        # большая картинка текущего оружия
        if weapon.is_reloading:
            # используем картинку перезарядки
            current_weapon_icon = self.weapon_reload_icons.get(weapon.type.value, self.weapon_reload_icons["rifle"])
        else:
            # используем обычную картинку оружия
            current_weapon_icon = self.weapon_icons.get(weapon.type.value, self.weapon_icons["rifle"])
        
        weapon_surface.blit(current_weapon_icon, (20, 7))  # скорректировали позицию
        
        # боеприпасы обычным шрифтом (уменьшили размер)
        if weapon.is_reloading:
            # во время перезарядки делаем патроны ярко-красными
            ammo_color = (255, 50, 50)
        else:
            # обычная цветовая схема патронов
            ammo_color = (255, 100, 100) if weapon.ammo < 5 else (255, 255, 100) if weapon.ammo < 15 else (100, 255, 100)
        
        ammo_text = self.hud_font.render(f"{weapon.ammo}/{weapon.stats['max_ammo']}", True, ammo_color)
        ammo_rect = ammo_text.get_rect(center=(weapon_width//2, 53))  # скорректировали позицию
        weapon_surface.blit(ammo_text, ammo_rect)
        
        # убираем текст перезарядки - теперь используется картинка
        
        # позиционируем в правом нижнем углу
        screen.blit(weapon_surface, (screen.get_width() - weapon_width - 10, screen.get_height() - weapon_height - 15))
    
    def _render_inventory(self, screen):
        # отрисовка компактного инвентаря слева
        # создаем фон для инвентаря
        inv_width = 200
        inv_height = 120
        inv_surface = pygame.Surface((inv_width, inv_height), pygame.SRCALPHA)
        
        # заголовок инвентаря
        inventory_text = self.hud_font.render("Inventory:", True, (200, 200, 200))
        inv_surface.blit(inventory_text, (10, 10))
        
        # первая строка - оружие (пистолет, автомат, дробовик)
        weapon_y = 35
        weapon_icon_x = 10
        
        # список всех типов оружия для отображения
        weapon_types_to_show = ["pistol", "rifle", "shotgun"]
        
        for weapon_key in weapon_types_to_show:
            if weapon_key in self.weapon_icons:
                # увеличенные иконки для оружия
                weapon_icon = pygame.transform.scale(self.weapon_icons[weapon_key], (40, 20))
                
                # проверяем, есть ли это оружие в инвентаре и активно ли оно
                weapon_in_inventory = False
                is_current_weapon = False
                
                for weapon_type in self.player.inventory:
                    weapon_type_key = weapon_type.value if hasattr(weapon_type, 'value') else str(weapon_type)
                    if weapon_type_key == weapon_key:
                        weapon_in_inventory = True
                        if weapon_type == self.player.current_weapon:
                            is_current_weapon = True
                        break
                
                # если оружие есть в инвентаре, показываем его
                if weapon_in_inventory:
                    inv_surface.blit(weapon_icon, (weapon_icon_x, weapon_y))
                #else:
                    # # показываем серую версию для отсутствующего оружия
                    # gray_icon = pygame.transform.scale(self.weapon_icons[weapon_key], (40, 20))
                    # gray_surface = pygame.Surface(gray_icon.get_size(), pygame.SRCALPHA)
                    # gray_surface.fill((100, 100, 100, 100))
                    # gray_icon.blit(gray_surface, (0, 0), special_flags=pygame.BLEND_MULT)
                    # inv_surface.blit(gray_icon, (weapon_icon_x, weapon_y))
                
                weapon_icon_x += 50
        
        # вторая строка - слоты для расходных предметов (медкиты, патроны)
        consumables_y = 65
        slot_x = 10
        
        # получаем все предметы в инвентаре
        all_items = self.player.item_manager.get_all_items_with_count()
        consumable_items = [item for item in all_items if item.item_type in [ItemType.MEDKIT, ItemType.AMMO]]
        
        # показываем слоты для расходных предметов
        max_slots = 4  # 4 слота для предметов
        for i in range(max_slots):
            slot_rect = pygame.Rect(slot_x, consumables_y, 35, 20)
            
            if i < len(consumable_items):
                # есть предмет для отображения
                item = consumable_items[i]
                
                # рисуем фон слота (зелёный если есть предметы)
                pygame.draw.rect(inv_surface, (50, 100, 50, 150), slot_rect)
                pygame.draw.rect(inv_surface, (100, 200, 100, 200), slot_rect, 1)
                
                # рисуем спрайт предмета
                if item.sprite:
                    sprite_rect = item.sprite.get_rect(center=slot_rect.center)
                    inv_surface.blit(item.sprite, sprite_rect)
                
                # убираем счётчики - каждый слот = 1 предмет
            else:
                # пустой слот
                pygame.draw.rect(inv_surface, (50, 50, 50, 150), slot_rect)
                pygame.draw.rect(inv_surface, (100, 100, 100, 200), slot_rect, 1)
                
                # добавляем знак "+" для обозначения пустого слота
                plus_text = self.hud_font.render("+", True, (150, 150, 150))
                plus_rect = plus_text.get_rect(center=slot_rect.center)
                inv_surface.blit(plus_text, plus_rect)
            
            slot_x += 40  # уменьшаем расстояние между слотами
        
        # позиционируем в левом нижнем углу, но чуть выше
        screen.blit(inv_surface, (10, screen.get_height() - inv_height + 5))
    
    def _render_health_bar(self, screen):
        # креативная отрисовка здоровья в нижнем центре
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # размеры полосы здоровья
        bar_width = 300
        bar_height = 25
        bar_x = (screen_width - bar_width) // 2
        bar_y = screen_height - 50
        
        # создаем поверхность для полосы здоровья
        health_surface = pygame.Surface((bar_width + 20, bar_height + 20), pygame.SRCALPHA)
        
        # фон полосы здоровья
        pygame.draw.rect(health_surface, (0, 0, 0, 150), (10, 10, bar_width, bar_height))
        pygame.draw.rect(health_surface, (50, 50, 50, 200), (10, 10, bar_width, bar_height), 2)
        
        # цвет здоровья в зависимости от процента
        health_percent = self.player.health / 100
        if health_percent > 0.7:
            health_color = (100, 255, 100, 210)  # зеленый
        elif health_percent > 0.3:
            health_color = (255, 255, 100, 210)  # желтый
        else:
            health_color = (255, 100, 100, 210)  # красный
        
        # полоса здоровья
        current_width = int(bar_width * health_percent)
        pygame.draw.rect(health_surface, health_color, (10, 10, current_width, bar_height))
        
        # текст здоровья
        health_text = self.hud_font.render(f"{self.player.health}/100", True, (255, 255, 255))
        text_rect = health_text.get_rect(center=(bar_width//2 + 10, bar_height//2 + 10))
        health_surface.blit(health_text, text_rect)
        
        screen.blit(health_surface, (bar_x - 10, bar_y - 10))

    def change_level(self, new_level):
        self.levels_completed += 1
        level_points = 100 * self.levels_completed  # Example: 100 points per level, scaling with difficulty
        self.enemies_killed += level_points  # Add to total score (enemies_killed is used as score)
        print(f"Level completed! Added {level_points} points. Total score: {self.enemies_killed}")

        self.current_level = new_level
        self.settings.data["initial_level"] = new_level
        self.settings.save_settings()
        # перемещаем игрока на точку спавна нового уровня
        level = self.levels[new_level]
        self.player.world_x = level.player_spawn['x']
        self.player.world_y = level.player_spawn['y']
        
        # обновляем обработчик двери для нового уровня
        self.door_handler = DoorInteractionHandler(level.quest_system)
        self.door_handler.reset()

    def reset_game(self):
        print("Resetting game state")
        self.enemies_killed = 0
        self.levels_completed = 0
        self.player.health = self.settings.get_player_settings().get("initial_health", 100)
        if hasattr(self.player, 'ammo'):
            self.player.ammo = self.settings.get_player_settings().get("initial_ammo", 0)
        self.tracers = []
        # self.text_display_manager.reset()
        self.damage_effect.reset()
        level = self.levels[self.current_level]
        self.player.world_x = level.player_spawn['x']
        self.player.world_y = level.player_spawn['y']
        # Reset enemies' counted status to allow re-counting kills
        for enemy in self.levels[self.current_level].enemies:
            enemy.counted = False

    def enter(self):
        self.levels_completed = 0
        pass

    def exit(self):
        # останавливаем фоновую музыку при выходе из геймплея
        if hasattr(self.game, 'audio_manager'):
            self.game.audio_manager.stop_music()
