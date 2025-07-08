import pygame
from state import State, GameState
from player import Player
from level import Level
from config.settings import Settings

class GameplayState:
    def __init__(self, game):
        self.game = game
        self.settings = Settings()
        
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
        if keys[pygame.K_l]:  # Simulate level completion
            self.stats.add_score("Player1", 1000)
            print("Score added for Player1")
        if keys[pygame.K_ESCAPE]:
            self.game.change_state(GameState.MAIN_MENU)

    def render(self, screen):
        # Сначала рисуем уровень с учетом позиции игрока
        self.levels[self.current_level].draw(screen, self.player.world_x, self.player.world_y)
        
        # Затем рисуем игрока (он всегда в центре)
        self.player.draw(screen)
        
        # Отрисовка HUD
        # TODO
        font = pygame.font.SysFont("Arial", 24)
        health_text = font.render(f"Health: {self.player.health}", True, (255, 255, 255))
        screen.blit(health_text, (10, 10))

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