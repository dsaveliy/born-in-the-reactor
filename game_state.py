import pygame
from state import State, GameState
from player import Player
from level import Level
from settings_state import SettingsState
from weapon import Weapon, WeaponType
from hitscan import HitscanShot

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
                    if item in ["pistol", "rifle", "shotgun"] }
        )
        self.tracers = []


    def update(self, dt):
        # действия на клавиатуре
        # движение
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player.move("up", self.levels[self.current_level])
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.player.move("down", self.levels[self.current_level])
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player.move("left", self.levels[self.current_level])
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player.move("right", self.levels[self.current_level])
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

        if self.levels[self.current_level].transition_zone:
            zone = self.levels[self.current_level].transition_zone
            zone_rect = pygame.Rect(zone["x"], zone["y"], zone["width"], zone["height"])
            player_rect = pygame.Rect(self.player.world_x, self.player.world_y, self.player.width, self.player.height)
            if zone_rect.contains(player_rect):
                self.change_level(zone["target_level"])

        for enemy in self.levels[self.current_level].enemies:
            if enemy.update(dt, self.levels[self.current_level], self.player):
                self.levels[self.current_level].enemies.remove(enemy)

    def render(self, screen):
        self.levels[self.current_level].render(screen, self.player.world_x, self.player.world_y) # сначала рисуем уровень(с учетом позиции игрока)
        self.player.render(screen) # игрок
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

        # отрисовка портала на следующий уровень
        zone = self.levels[self.current_level].transition_zone
        if zone:
            offset = pygame.Vector2(self.player.world_x - 400, self.player.world_y - 300)
            rect = pygame.Rect(zone["x"], zone["y"], zone["width"], zone["height"])
            pygame.draw.rect(screen, (0, 255, 255), rect.move(-offset), 2)

        # отрисовка HUD(сейчас - демо)
        # TODO
        font = pygame.font.SysFont("Arial", 24)

        health_text = font.render(f"Health: {self.player.health}", True, (255, 255, 255))
        screen.blit(health_text, (10, 10))

        weapon = self.player.weapons[self.player.current_weapon]
        weapon_text = font.render(
            f"{self.player.current_weapon.value.upper()}",
            True, (255, 255, 255))
        screen.blit(weapon_text, (10, 40))

        ammo_text = font.render(
            f"{weapon.ammo}/{weapon.stats['max_ammo']}",
            True, (255, 255, 255))
        screen.blit(ammo_text, (10, 70))

        if weapon.is_reloading:
            reload_text = font.render("RELOADING...", True, (255, 100, 100))
            screen.blit(reload_text, (10, 100))

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