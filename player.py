import pygame

class Player:
    def __init__(self, x, y, health=100, ammo=0):
        self.world_x = x
        self.world_y = y
        self.screen_x = 400  # Центр экрана
        self.screen_y = 300
        self.width = 30
        self.height = 30
        self.health = health  # Используем переданное значение
        self.speed = 5
        self.ammo = ammo  # Используем переданное значение
        self.inventory = ["pistol", "medkit"]
        self.current_weapon = "pistol"

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