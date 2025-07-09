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
    
    def switch_weapon(self, weapon_type):
        if weapon_type in self.inventory:
            self.current_weapon = weapon_type
    
    def fire(self):
        return self.weapons[self.current_weapon].fire()
    
    def reload(self):
        self.weapons[self.current_weapon].start_reload()
    
    def update(self, dt: float):
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
        # двигаем мир в противоположную сторону 
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

        # проверка коллизий
        if level.is_position_blocked(self.world_x, self.world_y, self.width, self.height):
            # откат
            if direction == "up":
                self.world_y += self.speed
            elif direction == "down":
                self.world_y -= self.speed
            elif direction == "left":
                self.world_x += self.speed
            elif direction == "right":
                self.world_x -= self.speed

        self.is_moving = True



    def render(self, screen):
        # отрисовка тела игрока
        sprite = self.animations[self.facing][self.anim_index]
        scaled_sprite = pygame.transform.scale(sprite, (self.width, self.height))
        draw_pos = (self.screen_x - self.width // 2, self.screen_y - self.height // 2)
        screen.blit(scaled_sprite, draw_pos)

        # отрисовка оружия по центру игрока
        weapon = self.weapons[self.current_weapon]
        weapon_sprite, scale_size = weapon.get_current_sprite_and_size(self.facing)
        weapon_sprite = pygame.transform.scale(weapon_sprite, scale_size)

        weapon_pos = (self.screen_x - weapon_sprite.get_width() // 2,
                      self.screen_y - weapon_sprite.get_height() // 2 + self.height // 3)
        screen.blit(weapon_sprite, weapon_pos)


    def hitscan_fire(self, level, camera_offset):
        weapon = self.weapons[self.current_weapon]
        if self.fire_timer > 0 or not weapon.fire():
            return None  # пока нельзя стрелять
        self.fire_timer = weapon.stats.get("fire_delay", 0.2)  # обновляем кулдаун в зависимости от оружия
        # координаты выстрела
        start, end = self.get_aim_line()

        # проверка попадания
        for enemy in level.enemies[:]:
            enemy_rect = pygame.Rect(enemy.position.x, enemy.position.y, enemy.width, enemy.height)
            if enemy_rect.clipline(start, end):
                enemy.health -= weapon.stats["damage"]
                if enemy.health <= 0 and not enemy.is_dead:
                    enemy.die()
        return (start - camera_offset, end - camera_offset, weapon.stats["damage"])

    def get_aim_line(self):
        # возвращает мировые координаты линии прицела(начало и конец)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen_from = pygame.Vector2(self.screen_x, self.screen_y)
        screen_to = pygame.Vector2(mouse_x, mouse_y)
        direction = (screen_to - screen_from)
    
        if direction.length_squared() == 0:
            direction = pygame.Vector2(1, 0)
    
        direction = direction.normalize()
        start = pygame.Vector2(self.world_x, self.world_y)
        end = start + direction * self.weapons[self.current_weapon].range
        return start, end