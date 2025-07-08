import pygame
import random

class Enemy:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.health = 30
        self.speed = 50
        self.width = 20 
        self.height = 20
        self.direction = pygame.Vector2(1, 0)
        self.direction_change_timer = 0
        self.chasing = False
        self.start_chase_distance = 200  # начало преследования
        self.stop_chase_distance = 300   # конец преследования
        self.attack_radius = 30
        self.attack_damage = 10
        self.attack_cooldown = 1.0  # секунды
        self.attack_timer = 0.0

    
    def update(self, dt, level, player):
        player_pos = pygame.Vector2(player.world_x, player.world_y)
        distance = self.position.distance_to(player_pos)
    
        # Логика агрессии
        if not self.chasing and distance < self.start_chase_distance:
            self.chasing = True
        elif self.chasing and distance > self.stop_chase_distance:
            self.chasing = False
    
        if self.chasing:
            # Преследуем игрока
            direction_to_player = (player_pos - self.position)
            if direction_to_player.length() > 0:
                self.direction = direction_to_player.normalize()
            print("ПРЕСЛЕДОВАНИЕ")
        else:
            # Блуждание
            self.direction_change_timer -= dt
            if self.direction_change_timer <= 0:
                self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                if self.direction.length() > 0:
                    self.direction = self.direction.normalize()
                self.direction_change_timer = random.uniform(1, 3)
            
        # Движение с коллизией
        dx = self.direction.x * self.speed * dt
        dy = self.direction.y * self.speed * dt
    
        self.position.x += dx
        if level.is_position_blocked(self.position.x, self.position.y, self.width, self.height):
            self.position.x -= dx
    
        self.position.y += dy
        if level.is_position_blocked(self.position.x, self.position.y, self.width, self.height):
            self.position.y -= dy

        # Обновление таймера атаки
        self.attack_timer -= dt
        # Проверка на возможность атаковать
        if self.position.distance_to(player_pos) < self.attack_radius:
            if self.attack_timer <= 0:
                player.health -= self.attack_damage
                print(f"⚠ Игрок получил урон! HP = {player.health}")
                self.attack_timer = self.attack_cooldown

    
    def render(self, screen, camera_offset):
        screen_pos = self.position - camera_offset
        pygame.draw.rect(screen, (0, 0, 255), (screen_pos.x - 10, screen_pos.y - 10, 20, 20))