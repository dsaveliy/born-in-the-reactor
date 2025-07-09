import pygame
from weapon import Weapon, WeaponType
from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Player:
    def __init__(self, x, y, health=100, ammo=0, inventory=[WeaponType.PISTOL, "medkit"]):
        # выгружаю картинки
        self.animations = {
            "up":    [pygame.image.load("assets/player/up_0.png").convert_alpha(),
                      pygame.image.load("assets/player/up_1.png").convert_alpha()],
            "down":  [pygame.image.load("assets/player/down_0.png").convert_alpha(),
                      pygame.image.load("assets/player/down_1.png").convert_alpha()],
            "left":  [pygame.image.load("assets/player/left_0.png").convert_alpha(),
                      pygame.image.load("assets/player/left_1.png").convert_alpha()],
            "right": [pygame.image.load("assets/player/right_0.png").convert_alpha(),
                      pygame.image.load("assets/player/right_1.png").convert_alpha()]
        }
        self.facing = "right"
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.2 # секунда на смену кадра
        self.is_moving = False
        # координаты относительно игрового мира
        self.world_x = x
        self.world_y = y
        # центр экрана
        self.screen_x = SCREEN_WIDTH / 2
        self.screen_y = SCREEN_HEIGHT / 2
        # размеры героя
        self.width = 39
        self.height = 48
        self.health = health
        self.speed = 2
        self.ammo = ammo
        self.inventory = inventory
        self.weapons = {
            #WeaponType.PISTOL: Weapon(WeaponType.PISTOL),
            WeaponType.RIFLE: Weapon(WeaponType.RIFLE)
            #WeaponType.SHOTGUN: Weapon(WeaponType.SHOTGUN)
        }
        self.current_weapon = WeaponType.RIFLE
        self.fire_timer = 0.0
        # разворот в сторону стрельбы
        self.forced_facing = None
        self.forced_facing_timer = 0
        self.forced_facing_duration = 0.4
    
    def switch_weapon(self, weapon_type):
        if weapon_type in self.inventory:
            self.current_weapon = weapon_type
    
    def fire(self):
        return self.weapons[self.current_weapon].fire()
    
    def reload(self):
        self.weapons[self.current_weapon].start_reload()
    
    def update(self, dt: float):
        if self.forced_facing_timer > 0:
            self.forced_facing_timer -= dt
            if self.forced_facing_timer <= 0:
                self.forced_facing = None
        self.weapons[self.current_weapon].update(dt)
        weapon = self.weapons[self.current_weapon]
        if weapon.is_reloading:
            self.weapon_state = "reload"
        elif weapon.just_fired:
            self.weapon_state = "shoot"
        else:
            self.weapon_state = "side"
        self.weapons[self.current_weapon].finish_reload()
        if self.fire_timer > 0:
            self.fire_timer -= dt
        if self.is_moving:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_index = (self.anim_index + 1) % 2
                self.anim_timer = 0
        else:
            self.anim_index = 0
        self.just_fired = False
        self.is_moving = False


    def move(self, direction, level):
        # Коэффициент для диагонального движения (1/sqrt(2) ≈ 0.707)
        diagonal_speed = self.speed * 0.7071

        # Сохраняем оригинальную позицию для возможного отката
        original_x = self.world_x
        original_y = self.world_y

        # Обрабатываем все возможные направления движения
        if direction == "up":
            self.facing = "up"
            self.world_y -= self.speed
        elif direction == "down":
            self.facing = "down"
            self.world_y += self.speed
        elif direction == "left":
            self.facing = "left"
            self.world_x -= self.speed
        elif direction == "right":
            self.facing = "right"
            self.world_x += self.speed
        elif direction == "up_left":
            self.facing = "left"  # или можно сделать комбинированное направление
            self.world_x -= diagonal_speed
            self.world_y -= diagonal_speed
        elif direction == "up_right":
            self.facing = "right"
            self.world_x += diagonal_speed
            self.world_y -= diagonal_speed
        elif direction == "down_left":
            self.facing = "left"
            self.world_x -= diagonal_speed
            self.world_y += diagonal_speed
        elif direction == "down_right":
            self.facing = "right"
            self.world_x += diagonal_speed
            self.world_y += diagonal_speed

        # Проверка коллизий с уровнем
        if level.is_position_blocked(self.world_x, self.world_y, self.width, self.height):
            self.world_x = original_x
            self.world_y = original_y
            self.is_moving = False
            return

        # Проверка коллизий с врагами
        player_rect = pygame.Rect(
            self.world_x - self.width//2,
            self.world_y - self.height//2,
            self.width, self.height
        )

        collision_occurred = False
        for enemy in level.enemies:
            enemy_rect = pygame.Rect(
                enemy.position.x - enemy.width//2,
                enemy.position.y - enemy.height//2,
                enemy.width, enemy.height
            )
            if player_rect.colliderect(enemy_rect) and not enemy.is_dead:
                collision_occurred = True
                break
            
        if collision_occurred:
            self.world_x = original_x
            self.world_y = original_y
            self.is_moving = False
        else:
            self.is_moving = True




    def render(self, screen):
        # отрисовка тела игрока
        current_facing = self.get_current_facing()
        sprite = self.animations[current_facing][self.anim_index]
        scaled_sprite = pygame.transform.scale(sprite, (self.width, self.height))
        draw_pos = (self.screen_x - self.width // 2, self.screen_y - self.height // 2)
        screen.blit(scaled_sprite, draw_pos)

        # отрисовка оружия по центру игрока
        weapon = self.weapons[self.current_weapon]
        weapon_sprite, scale_size = weapon.get_current_sprite_and_size(current_facing)
        weapon_sprite = pygame.transform.scale(weapon_sprite, scale_size)

        weapon_pos = (self.screen_x - weapon_sprite.get_width() // 2,
                      self.screen_y - weapon_sprite.get_height() // 2 + self.height // 3)
        screen.blit(weapon_sprite, weapon_pos)


    def hitscan_fire(self, level, camera_offset):
        weapon = self.weapons[self.current_weapon]
        if self.fire_timer > 0 or not weapon.fire():
            return None

        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.update_facing_direction(mouse_x, mouse_y)

        self.fire_timer = weapon.stats.get("fire_delay", 0.2)
        start, end = self.get_aim_line()

        # Проверка столкновения луча с препятствиями
        for obstacle in level.obstacles:
            obstacle_rect = pygame.Rect(obstacle['x'], obstacle['y'], obstacle['width'], obstacle['height'])
            intersection = obstacle_rect.clipline(start, end)
            if intersection:
                end = pygame.Vector2(intersection[0])
                break

        for object in level.objects_decor:
            object_rect = pygame.Rect(object['x'], object['y'], object['width'], object['height'])
            intersection = object_rect.clipline(start, end)
            if intersection:
                end = pygame.Vector2(intersection[0])
                break

        # Проверка попадания во врагов
        for enemy in level.enemies[:]:
            enemy_rect = pygame.Rect(enemy.position.x, enemy.position.y, enemy.width, enemy.height)
            if enemy_rect.clipline(start, end):
                enemy.health -= weapon.stats["damage"]
                if enemy.health <= 0 and not enemy.is_dead:
                    enemy.die()

        return (start - camera_offset, end - camera_offset, weapon.stats["damage"])

    def get_aim_line(self):
        # возвращает мировые координаты линии прицела (начало и конец)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen_from = pygame.Vector2(self.screen_x, self.screen_y)
        screen_to = pygame.Vector2(mouse_x, mouse_y)
        direction = (screen_to - screen_from)
    
        if direction.length_squared() == 0:
            direction = pygame.Vector2(1, 0)
    
        direction = direction.normalize()
        start = pygame.Vector2(self.world_x, self.world_y) + direction * 20  # <-- Сдвиг на 20 пикселей
        end = start + direction * self.weapons[self.current_weapon].range
        return start, end
    
    def update_facing_direction(self, mouse_x, mouse_y):
        direction_x = mouse_x - self.screen_x
        direction_y = mouse_y - self.screen_y

        # угол между игроком и курсором
        angle = pygame.math.Vector2(direction_x, direction_y).angle_to((1, 0))

        # направление (аналогично Enemy.get_facing_direction())
        if -45 <= angle < 45:
            new_facing = "right"
        elif 45 <= angle < 135:
            new_facing = "up"
        elif angle >= 135 or angle < -135:
            new_facing = "left"
        else:
            new_facing = "down"

        if new_facing != self.forced_facing:
            self.forced_facing = new_facing
            self.forced_facing_timer = self.forced_facing_duration

    def get_current_facing(self):
        if self.forced_facing and self.forced_facing_timer > 0:
            return self.forced_facing
        return self.facing
