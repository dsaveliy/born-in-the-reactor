import pygame
from state import State
from player import Player
from level import Level
from config.settings import Settings
from weapon import Weapon, WeaponType
from hitscan import HitscanShot

class GameplayState:
    def __init__(self, game):
        self.game = game
        self.settings = Settings()
        self.tracers = []
        
        # Загружаем уровни
        self.levels = {
            "intro": Level("assets/lvls/gomel.json"),
            "gomel_streets": Level("assets/lvls/gomel.json"),
            # "military_base": Level("assets/lvls/military.json")
        }
        
        # Получаем начальный уровень из настроек
        self.current_level = self.settings.get_initial_level()
        
        # Проверка на случай если уровень в настройках не существует
        if self.current_level not in self.levels:
            self.current_level = "intro"
            print(f"Warning: Level {self.current_level} not found, using 'intro'")
        
        level = self.levels[self.current_level]
        player_settings = self.settings.get_player_settings()
        
        # Создаем игрока с настройками из файла
        self.player = Player(
            x=level.player_spawn['x'],
            y=level.player_spawn['y'],
            health=player_settings.get("initial_health", 100),
            ammo=player_settings.get("initial_ammo", 30)
        )


    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player.move("up", self.levels[self.current_level])
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.player.move("down", self.levels[self.current_level])
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player.move("left", self.levels[self.current_level])
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player.move("right", self.levels[self.current_level])

        self.player.update(dt)
    
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # ЛКМ
            result = self.player.hitscan_fire(self.levels[self.current_level],
                                              camera_offset=pygame.Vector2(self.player.world_x - 400, self.player.world_y - 300))
            if result:
                start, end, dmg = result
                self.tracers.append(HitscanShot(start, end, dmg))


        # Обновляем трейсеры
        for tracer in self.tracers[:]:
            tracer.update(dt)
            if not tracer.is_alive():
                self.tracers.remove(tracer)


        if keys[pygame.K_r]:
            self.player.reload()
            print("Перезарядка...")

        # Смена оружия
        if keys[pygame.K_1]:
            self.player.switch_weapon(WeaponType.PISTOL)
        if keys[pygame.K_2]:
            self.player.switch_weapon(WeaponType.RIFLE)
        if keys[pygame.K_3]:
            self.player.switch_weapon(WeaponType.SHOTGUN)

        for enemy in self.levels[self.current_level].enemies:
            enemy.update(dt, self.levels[self.current_level], self.player)




    def render(self, screen):
        # Сначала рисуем уровень с учетом позиции игрока
        self.levels[self.current_level].draw(screen, self.player.world_x, self.player.world_y)
        
        # Затем рисуем игрока (он всегда в центре)
        self.player.draw(screen)

        for enemy in self.levels[self.current_level].enemies:
            enemy.render(screen, camera_offset=pygame.Vector2(self.player.world_x - 400, self.player.world_y - 300))


        font = pygame.font.SysFont("Arial", 20)
        weapon = self.player.weapons[self.player.current_weapon]

        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            aim_start, aim_end = self.player.get_aim_line()
            offset = pygame.Vector2(self.player.world_x - 400, self.player.world_y - 300)
            pygame.draw.line(screen, (200, 200, 50), aim_start - offset, aim_end - offset, 1)


        # Название оружия
        weapon_text = font.render(
            f"{self.player.current_weapon.value.upper()}",
            True, (255, 255, 255))
        screen.blit(weapon_text, (10, 40))

        # Патроны
        ammo_text = font.render(
            f"{weapon.ammo}/{weapon.stats['max_ammo']}",
            True, (255, 255, 255))
        screen.blit(ammo_text, (10, 70))

        # Перезарядка
        if weapon.is_reloading:
            reload_text = font.render("RELOADING...", True, (255, 100, 100))
            screen.blit(reload_text, (10, 100))

        # Отрисовка HUD
        # TODO
        font = pygame.font.SysFont("Arial", 24)
        health_text = font.render(f"Health: {self.player.health}", True, (255, 255, 255))
        screen.blit(health_text, (10, 10))

        for tracer in self.tracers:
            tracer.render(screen)

    def enter(self):
        print("ENTER ENTERED")

    def change_level(self, new_level):
        self.current_level = new_level
        self.settings.data["initial_level"] = new_level
        self.settings.save_settings()
        
        # Перемещаем игрока на точку спавна нового уровня
        level = self.levels[new_level]
        self.player.world_x = level.player_spawn['x']
        self.player.world_y = level.player_spawn['y']

    def exit(self):
        # Очистка ресурсов при выходе из состояния
        pass