import pygame
from state import State, GameState
from player import Player
from level import Level
from settings_state import SettingsState
from weapon import Weapon, WeaponType
from hitscan import HitscanShot
from effects import DamageEffect

class GameplayState:
    def __init__(self, game):
        self.game = game
        self.settings = SettingsState(game)  # Create a temporary SettingsState instance
        self.current_level = self.settings.get_initial_level()
        player_settings = self.settings.get_player_settings()
        self.levels = { # загрузка уровней
            "gomel_streets": Level("assets/lvls/gomel.json"),
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

    def update(self, dt):
        # проверка прохода двери
        if self.levels[self.current_level].transition_zone:
            zone = self.levels[self.current_level].transition_zone
            zone_rect = pygame.Rect(
                zone["x"], 
                zone["y"], 
                zone["width"], 
                zone["height"]
            )

            player_rect = pygame.Rect(
                self.player.world_x - self.player.width//2,
                self.player.world_y - self.player.height//2,
                self.player.width, 
                self.player.height
            )

            if zone_rect.contains(player_rect):
                self.change_level(zone["target_level"])
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
        # перезарядка
        if keys[pygame.K_r]:
            self.player.reload()
        # действия на мыши
        # выстрелы
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # лкм
            result = self.player.hitscan_fire(self.levels[self.current_level],
                    camera_offset=pygame.Vector2(self.player.world_x - 400, self.player.world_y - 300))
            if result:
                start, end, dmg = result
                self.tracers.append(HitscanShot(start, end, dmg)) # выстрел
        # обновление трейсеров
        for tracer in self.tracers[:]:
            tracer.update(dt)
            if not tracer.is_alive():
                self.tracers.remove(tracer)
        # обновление объектов
        self.player.update(dt)

        if self.player.health <= 0:
            self.game.change_state(GameState.MAIN_MENU)
            self.player.health = 100

        for enemy in self.levels[self.current_level].enemies:
            if enemy.update(dt, self.levels[self.current_level], self.player):
                self.levels[self.current_level].enemies.remove(enemy)
        # эффект крови
        current_health = self.player.health
        if hasattr(self, 'last_health') and current_health < self.last_health:
            self.damage_effect.trigger()
        self.last_health = current_health
        
        self.damage_effect.update(dt)


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
        font = pygame.font.SysFont("Arial", 24)
        
        # Здоровье
        health_text = font.render(f"Health: {self.player.health}", True, (255, 255, 255))
        screen.blit(health_text, (10, 10))
        
        # Оружие
        weapon = self.player.weapons[self.player.current_weapon]
        weapon_text = font.render(
            f"{self.player.current_weapon.value.upper()}",
            True, (255, 255, 255))
        screen.blit(weapon_text, (10, 40))
        
        # Боеприпасы
        ammo_text = font.render(
            f"{weapon.ammo}/{weapon.stats['max_ammo']}",
            True, (255, 255, 255))
        screen.blit(ammo_text, (10, 70))
        
        # Перезарядка
        if weapon.is_reloading:
            reload_text = font.render("RELOADING...", True, (255, 100, 100))
            screen.blit(reload_text, (10, 100))
        
        # Инвентарь с хардкодом RIFLE
        inventory_text = font.render("Inventory: RIFLE", True, (255, 255, 255))
        screen.blit(inventory_text, (10, 130))

    def change_level(self, new_level):
        self.current_level = new_level
        self.settings.data["initial_level"] = new_level
        self.settings.save_settings()
        # перемещаем игрока на точку спавна нового уровня
        level = self.levels[new_level]
        self.player.world_x = level.player_spawn['x']
        self.player.world_y = level.player_spawn['y']

    def enter(self):
        pass

    def exit(self):
        pass