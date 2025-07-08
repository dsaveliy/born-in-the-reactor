import pygame
from weapon import Weapon, WeaponType


class Player:
    def __init__(self, x, y, health=100, ammo=0):
        self.world_x = x
        self.world_y = y
        self.screen_x = 400  # Центр экрана
        self.screen_y = 300
        self.width = 30
        self.height = 30
        self.health = health  # Используем переданное значение
        self.speed = 3
        self.ammo = ammo  # Используем переданное значение
        self.weapons = {
            WeaponType.PISTOL: Weapon(WeaponType.PISTOL),
            WeaponType.RIFLE: Weapon(WeaponType.RIFLE),
            WeaponType.SHOTGUN: Weapon(WeaponType.SHOTGUN)
        }
        self.current_weapon = WeaponType.PISTOL
        self.inventory = [WeaponType.PISTOL, "medkit", WeaponType.RIFLE]
        self.fire_timer = 0.0
    
    def switch_weapon(self, weapon_type):
        """Смена оружия"""
        if weapon_type in self.inventory:
            self.current_weapon = weapon_type
    
    def fire(self):
        """Выстрел из текущего оружия"""
        return self.weapons[self.current_weapon].fire()
    
    def reload(self):
        """Перезарядка текущего оружия"""
        self.weapons[self.current_weapon].start_reload()
    
    def update(self, dt: float):
        """Обновление состояния оружия"""
        self.weapons[self.current_weapon].update(dt)
        self.weapons[self.current_weapon].finish_reload()
        if self.fire_timer > 0:
            self.fire_timer -= dt



    def move(self, direction, level):
        # Двигаем мир в противоположную сторону
        print(self.world_x, self.world_y)
        if direction == "up":
            self.world_y -= self.speed
        elif direction == "down":
            self.world_y += self.speed
        elif direction == "left":
            self.world_x -= self.speed
        elif direction == "right":
            self.world_x += self.speed

        # Проверка коллизий (теперь с мировыми координатами)
        if level.is_position_blocked(self.world_x, self.world_y, self.width, self.height):
            print("BLOCKED")
            # Откат движения при коллизии
            if direction == "up":
                self.world_y += self.speed
            elif direction == "down":
                self.world_y -= self.speed
            elif direction == "left":
                self.world_x += self.speed
            elif direction == "right":
                self.world_x -= self.speed

    def draw(self, screen):
        # Игрок всегда рисуется в центре экрана
        pygame.draw.rect(screen, (0, 255, 0), 
                        (self.screen_x - self.width//2, 
                         self.screen_y - self.height//2, 
                         self.width, self.height))
        
        weapon_pos = (self.screen_x, self.screen_y - 10)
        self.weapons[self.current_weapon].draw(screen, weapon_pos)
        
    def hitscan_fire(self, level, camera_offset):
        weapon = self.weapons[self.current_weapon]

        if self.fire_timer > 0 or not weapon.fire():
            return None  # пока нельзя стрелять

        # Обновляем кулдаун в зависимости от оружия
        self.fire_timer = weapon.stats.get("fire_delay", 0.2)  # по умолчанию 0.2 сек

        # Направление
        mouse_x, mouse_y = pygame.mouse.get_pos()
        from_screen = pygame.Vector2(self.screen_x, self.screen_y)
        to_screen = pygame.Vector2(mouse_x, mouse_y)
        direction = (to_screen - from_screen).normalize()

        start = pygame.Vector2(self.world_x, self.world_y)
        end = start + direction * 800

        # Проверка попадания
        for enemy in level.enemies[:]:
            enemy_rect = pygame.Rect(enemy.position.x, enemy.position.y, enemy.width, enemy.height)
            if enemy_rect.clipline(start, end):
                enemy.health -= weapon.stats["damage"]
                print(f"🎯 Попадание! HP = {enemy.health}")
                if enemy.health <= 0:
                    level.enemies.remove(enemy)
                break

        return (start - camera_offset, end - camera_offset, weapon.stats["damage"])

    def get_aim_line(self):
        """Возвращает мировые координаты линии прицела (начало и конец)"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen_from = pygame.Vector2(self.screen_x, self.screen_y)
        screen_to = pygame.Vector2(mouse_x, mouse_y)
        direction = (screen_to - screen_from)
    
        if direction.length_squared() == 0:
            direction = pygame.Vector2(1, 0)
    
        direction = direction.normalize()
        start = pygame.Vector2(self.world_x, self.world_y)
        end = start + direction * 800
        return start, end
