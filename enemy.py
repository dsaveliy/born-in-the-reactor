import pygame
import random
import math

class Enemy:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.health = 30
        self.speed = 40
        self.width = 20
        self.height = 20
        self.direction = pygame.Vector2(1, 0)
        self.direction_change_timer = 0
        self.chasing = False
        self.start_chase_distance = 200  # начало преследования
        self.stop_chase_distance = 300   # конец преследования
        self.attack_radius = 50
        self.attack_damage = 10
        self.attack_cooldown = 1.0
        self.attack_timer = 0.0
        self.is_attacking = False
        
        # Загрузка спрайтов по направлениям
        # Для примера считаю, что есть папка assets/enemy с картинками up.png, down.png, left.png, right.png
        self.animations = {
            "move": {
                "up": [
                    pygame.image.load("assets/enemies/first/up_0.png").convert_alpha(),
                    pygame.image.load("assets/enemies/first/up_1.png").convert_alpha()
                ],
                "down": [
                    pygame.image.load("assets/enemies/first/down_0.png").convert_alpha(),
                    pygame.image.load("assets/enemies/first/down_1.png").convert_alpha()
                ],
                "left": [
                    pygame.image.load("assets/enemies/first/left_0.png").convert_alpha(),
                    pygame.image.load("assets/enemies/first/left_1.png").convert_alpha()
                ],
                "right": [
                    pygame.image.load("assets/enemies/first/right_0.png").convert_alpha(),
                    pygame.image.load("assets/enemies/first/right_1.png").convert_alpha()
                ]
            },
            "attack": {
                "up": pygame.image.load("assets/enemies/first/attack_up.png").convert_alpha(),
                "down": pygame.image.load("assets/enemies/first/attack_down.png").convert_alpha(),
                "left": pygame.image.load("assets/enemies/first/attack_left.png").convert_alpha(),
                "right": pygame.image.load("assets/enemies/first/attack_right.png").convert_alpha(),
            }
        }


        self.scale_sizes = {
            "up": (24, 44),
            "down": (30, 44),
            "left": (44, 36),
            "right": (44, 36),
            "death": (44, 36)
        }

        self.anim_index = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.2  # секунд между сменой кадров
        self.attack_display_time = 0.3  # время показа кадра атаки
        self.attack_display_timer = 0.0


        self.is_dead = False
        self.death_timer = 0
        self.death_duration = 3.0
        self.death_animations = {
            "up": pygame.image.load("assets/enemies/first/death_up.png").convert_alpha(),
            "down": pygame.image.load("assets/enemies/first/death_down.png").convert_alpha(),
            "left": pygame.image.load("assets/enemies/first/death_left.png").convert_alpha(),
            "right": pygame.image.load("assets/enemies/first/death_right.png").convert_alpha()
        }

    def die(self):
        self.is_dead = True
        self.death_timer = self.death_duration

    def update(self, dt, level, player):
        if self.is_dead:
            self.death_timer -= dt
            return self.death_timer <= 0 # для внешнего вызова

        player_pos = pygame.Vector2(player.world_x, player.world_y)
        distance = self.position.distance_to(player_pos)

        dx = 0
        dy = 0

        # проверка видимости игрока (нет стен между врагом и игроком)
        def can_see_player():
            start = self.position
            end = player_pos
            for obstacle in level.obstacles:
                obstacle_rect = pygame.Rect(
                    obstacle['x'],
                    obstacle['y'],
                    obstacle['width'],
                    obstacle['height']
                )
                if obstacle_rect.clipline(start, end):
                    return False
            return True

        # проверка атаки (только если игрок виден)
        if self.attack_timer <= 0 and distance < self.attack_radius and can_see_player():
            if player.health > 0:
                player.health -= self.attack_damage
                self.attack_timer = self.attack_cooldown
                self.is_attacking = True
                self.attack_display_timer = self.attack_display_time  # запускаем таймер показа атаки

        # обновляем таймеры
        self.attack_timer -= dt
        if self.attack_display_timer > 0:
            self.attack_display_timer -= dt
        else:
            self.is_attacking = False

        # если не атакуем — движение и анимация движения
        if not self.is_attacking:
            # обновляем состояние преследования (учитывая видимость игрока)
            if not self.chasing and distance < self.start_chase_distance and can_see_player():
                self.chasing = True
            elif self.chasing and (distance > self.stop_chase_distance or not can_see_player()):
                self.chasing = False

            if self.chasing:
                direction_to_player = (player_pos - self.position)
                if direction_to_player.length() > 0:
                    self.direction = direction_to_player.normalize()
            else:
                self.direction_change_timer -= dt
                if self.direction_change_timer <= 0:
                    self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                    if self.direction.length() > 0:
                        self.direction = self.direction.normalize()
                    self.direction_change_timer = random.uniform(1, 3)

            dx = self.direction.x * self.speed * dt
            dy = self.direction.y * self.speed * dt

            self.position.x += dx
            if level.is_position_blocked(self.position.x, self.position.y, self.width, self.height):
                self.position.x -= dx

            self.position.y += dy
            if level.is_position_blocked(self.position.x, self.position.y, self.width, self.height):
                self.position.y -= dy

            # анимация движения
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                facing = self.get_facing_direction()
                self.anim_index = (self.anim_index + 1) % len(self.animations["move"][facing])
        else:
            # при атаке не обновляем анимацию движения, показываем статичный кадр атаки
            self.anim_index = 0

        enemy_rect = pygame.Rect(
            self.position.x - self.width//2,
            self.position.y - self.height//2,
            self.width, self.height
        )
        
        # Проверка коллизии с игроком
        player_rect = pygame.Rect(
            player.world_x - player.width//2,
            player.world_y - player.height//2,
            player.width, player.height
        )
        
        if enemy_rect.colliderect(player_rect):
            # Откат движения врага
            self.position.x -= dx
            self.position.y -= dy


    def get_facing_direction(self):
        angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))
        if -45 <= angle < 45:
            return "right"
        elif 45 <= angle < 135:
            return "up"
        elif angle >= 135 or angle < -135:
            return "left"
        else:
            return "down"

    def render(self, screen, camera_offset):
        screen_pos = self.position - camera_offset
        if self.is_dead:
            sprite = self.death_animations[self.get_facing_direction()]
            scaled = pygame.transform.scale(sprite, (56, 14))
            screen.blit(scaled, (screen_pos.x - self.width//2, screen_pos.y - self.height//2))
        else:
            facing = self.get_facing_direction()

            if self.is_attacking:
                sprite = self.animations["attack"][facing]
            else:
                sprite = self.animations["move"][facing][self.anim_index]

            size = self.scale_sizes[facing]
            scaled_sprite = pygame.transform.scale(sprite, size)
            sprite_rect = scaled_sprite.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))
            screen.blit(scaled_sprite, sprite_rect)
