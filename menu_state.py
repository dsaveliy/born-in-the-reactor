import pygame
import json
import math
from state import State, GameState

class MainMenuState(State):
    def __init__(self, game):
        super().__init__(game)
        try:
            self.font = pygame.font.Font("assets/fonts/ShareTechMono-Regular.ttf", 32)
            self.title_font = pygame.font.Font("assets/fonts/Orbitron-Bold.ttf", 48)
        except FileNotFoundError:
            print("Error loading fonts, using default")
            self.font = pygame.font.Font(None, 36)
            self.title_font = pygame.font.Font(None, 48)
        
        # Player sprite properties
        self.player_x = 400  # Center of screen
        self.player_y = 300
        self.player_width = 39
        self.player_height = 48
        self.player_speed = 1.5  # Slower speed for menu
        self.anim_speed = 0.3  # Slower animation for menu
        self.facing = "right"
        self.anim_index = 0
        self.anim_timer = 0
        self.is_moving = False
        self.error_message = None  # For displaying errors
        self.error_timer = 0  # To auto-clear error messages
        self.action_cooldown = 0  # Prevent immediate input after state entry

        # Load player sprites with error handling
        self.animations = {}
        sprite_files = {
            "up": ["assets/player/up_0.png", "assets/player/up_1.png"],
            "down": ["assets/player/down_0.png", "assets/player/down_1.png"],
            "left": ["assets/player/left_0.png", "assets/player/left_1.png"],
            "right": ["assets/player/right_0.png", "assets/player/right_1.png"]
        }
        for direction, files in sprite_files.items():
            self.animations[direction] = []
            for file in files:
                try:
                    sprite = pygame.image.load(file).convert_alpha()
                    self.animations[direction].append(sprite)
                except FileNotFoundError:
                    print(f"Error loading sprite {file}, using placeholder")
                    self.animations[direction].append(pygame.Surface((self.player_width, self.player_height)))
                    self.animations[direction][-1].fill((255, 0, 0))  # Red placeholder

        self.options = ["Play", "Settings", "Stats", "Help", "Exit"]
        self.selected_option = 0
        self.action_triggered = False

        try:
            with open("assets/main/main.json", "r", encoding='utf-8') as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading main.json: {e}")
            self.config = {
                "background": "assets/bgs/main_menu2.png",
                "icons": []
            }

        try:
            self.main_background = pygame.image.load(self.config["background"]).convert()
            self.main_background = pygame.transform.scale(self.main_background, (800, 600))
        except FileNotFoundError:
            print(f"Error loading background {self.config['background']}")
            self.main_background = pygame.Surface((800, 600))
            self.main_background.fill((20, 20, 40))

        self.icons = []
        for icon in self.config.get("icons", []):
            try:
                img = pygame.image.load(icon["image"]).convert_alpha()
                img = pygame.transform.scale(img, (icon["width"], icon["height"]))
                self.icons.append({
                    "image": img,
                    "rect": pygame.Rect(icon["x"], icon["y"], icon["width"], icon["height"]),
                    "name": icon["name"],
                    "tooltip": icon["tooltip"],
                    "hover_alpha": 0  # For fade-in effect
                })
            except (FileNotFoundError, KeyError) as e:
                print(f"Error loading icon {icon.get('image', 'unknown')}: {e}")

        self.active_icon = None
        self.tooltip = None
        self.tooltip_alpha = 0  # For tooltip fade-in
        self.text_pulse = 0  # For pulsing text background

    def enter(self):
        print("Entered Main Menu State")
        self.selected_option = 0
        self.error_message = None
        self.error_timer = 0
        self.action_triggered = False
        self.player_x = 400
        self.player_y = 300
        self.facing = "right"
        self.is_moving = False
        self.anim_index = 0
        self.anim_timer = 0
        self.tooltip = None
        self.active_icon = None
        self.tooltip_alpha = 0
        self.text_pulse = 0
        self.action_cooldown = 0.2  # 0.2s cooldown to ignore immediate inputs
        pygame.event.clear()  # Clear event queue
        pygame.key.get_pressed()  # Flush keyboard state
        for icon in self.icons:
            icon["hover_alpha"] = 0

    def exit(self):
        print("Exiting Main Menu State")
        pygame.event.clear()  # Clear event queue on exit

    def update(self, dt):
        # Update action cooldown
        if self.action_cooldown > 0:
            self.action_cooldown -= dt
            return  # Skip input processing during cooldown

        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        # Update error message timer
        if self.error_message:
            self.error_timer += dt
            if self.error_timer >= 3.0:  # Clear error after 3 seconds
                self.error_message = None
                self.error_timer = 0

        # Handle player movement
        moved = False
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.facing = "up"
            self.player_y -= self.player_speed
            moved = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.facing = "down"
            self.player_y += self.player_speed
            moved = True
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.facing = "left"
            self.player_x -= self.player_speed
            moved = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.facing = "right"
            self.player_x += self.player_speed
            moved = True

        # Clamp player position to screen boundaries
        self.player_x = max(self.player_width / 2, min(self.player_x, 800 - self.player_width / 2))
        self.player_y = max(self.player_height / 2, min(self.player_y, 600 - self.player_height / 2))

        # Update player animation
        self.is_moving = moved
        if moved:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_index = (self.anim_index + 1) % 2
                self.anim_timer = 0
        else:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed * 2:  # Slower idle animation
                self.anim_index = (self.anim_index + 1) % 2
                self.anim_timer = 0
            if self.anim_timer == 0:
                self.anim_index = 0  # Reset to first frame when idle

        # Update tooltip and icon hover effects
        self.tooltip = None
        self.active_icon = None
        player_rect = pygame.Rect(
            self.player_x - self.player_width / 2,
            self.player_y - self.player_height / 2,
            self.player_width,
            self.player_height
        )
        mouse_rect = pygame.Rect(mouse_pos[0], mouse_pos[1], 1, 1)
        for icon in self.icons:
            if player_rect.colliderect(icon["rect"]) or mouse_rect.colliderect(icon["rect"]):
                self.tooltip = icon["tooltip"]
                self.active_icon = icon
                icon["hover_alpha"] = min(icon["hover_alpha"] + 500 * dt, 100)  # Fade in
            else:
                icon["hover_alpha"] = max(icon["hover_alpha"] - 500 * dt, 0)  # Fade out

        # Update tooltip fade-in
        if self.tooltip:
            self.tooltip_alpha = min(self.tooltip_alpha + 500 * dt, 255)
        else:
            self.tooltip_alpha = max(self.tooltip_alpha - 500 * dt, 0)

        # Update text pulse effect
        self.text_pulse += dt
        if self.text_pulse >= 1.0:
            self.text_pulse = 0

        if keys[pygame.K_DOWN] and not self.action_triggered:
            self.selected_option = (self.selected_option + 1) % len(self.options)
            print(f"Selected option: {self.options[self.selected_option]}")
            self.action_triggered = True
        if keys[pygame.K_UP] and not self.action_triggered:
            self.selected_option = (self.selected_option - 1) % len(self.options)
            print(f"Selected option: {self.options[self.selected_option]}")
            self.action_triggered = True

        if keys[pygame.K_RETURN] and not self.action_triggered:
            self.action_triggered = True
            print(f"Enter pressed, selected_option={self.selected_option}")
            if self.selected_option == 0:
                try:
                    if GameState.GAMEPLAY not in self.game.states:
                        raise ValueError("Gameplay state not initialized")
                    print("Starting game with intro cutscene")
                    # Запускаем интро катсцену, которая перейдет к геймплею
                    self.game.play_cutscene("assets/cutscenes/intro.json", GameState.GAMEPLAY)
                    self.error_message = None
                    self.error_timer = 0
                except Exception as e:
                    print(f"Failed to start game: {type(e).__name__}: {e}")
                    self.error_message = "Cannot start game: Level not found"
                    self.error_timer = 0
            elif self.selected_option == 1:
                print("Transitioning to GameState.SETTINGS")
                self.game.change_state(GameState.SETTINGS)
                self.error_message = None
                self.error_timer = 0
            elif self.selected_option == 2:
                print("Transitioning to GameState.STATS")
                self.game.change_state(GameState.STATS)
                self.error_message = None
                self.error_timer = 0
            elif self.selected_option == 3:
                print("Transitioning to GameState.HELP")
                self.game.change_state(GameState.HELP)
                self.error_message = None
                self.error_timer = 0
            elif self.selected_option == 4:
                print("Exiting game")
                self.game.running = False
                self.error_message = None
                self.error_timer = 0
        elif self.tooltip:
            if (keys[pygame.K_m] or (mouse_clicked and self.tooltip == "Press M for Settings")) and not self.action_triggered:
                self.action_triggered = True
                print("Transitioning to GameState.SETTINGS via icon")
                self.game.change_state(GameState.SETTINGS)
                self.error_message = None
                self.error_timer = 0
            elif (keys[pygame.K_t] or (mouse_clicked and self.tooltip == "Press T for Stats")) and not self.action_triggered:
                self.action_triggered = True
                print("Transitioning to GameState.STATS via icon")
                self.game.change_state(GameState.STATS)
                self.error_message = None
                self.error_timer = 0
            elif (keys[pygame.K_h] or (mouse_clicked and self.tooltip == "Press H for Help")) and not self.action_triggered:
                self.action_triggered = True
                print("Transitioning to GameState.HELP via icon")
                self.game.change_state(GameState.HELP)
                self.error_message = None
                self.error_timer = 0
        elif keys[pygame.K_q]:
            print("Exiting game via Q")
            self.game.running = False
            self.error_message = None
            self.error_timer = 0

        if not keys[pygame.K_RETURN] and not keys[pygame.K_m] and not keys[pygame.K_t] and not keys[pygame.K_h] and not mouse_clicked and not keys[pygame.K_ESCAPE] and not keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
            self.action_triggered = False

    def render(self, screen):
        # Calculate pulse_alpha for all rendering blocks
        pulse_alpha = 180 + int(30 * (1 + math.sin(self.text_pulse * math.pi)) / 2)  # Pulse between 180-210

        screen.blit(self.main_background, (0, 0))
        # Render title
        title = self.title_font.render("BORN IN THE REACTOR", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 10))
        
        # Render "Press Enter to play" with pulsing background
        play_text = self.font.render("Press Enter to play", True, (255, 255, 255))
        play_rect = play_text.get_rect(center=(400, 100))
        background_rect = play_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), background_rect)
        screen.blit(play_text, play_rect)

        # Render icons with hover effect and tooltips
        for icon in self.icons:
            icon_surface = icon["image"].copy()
            if icon["hover_alpha"] > 0:
                # Add glow effect by drawing a semi-transparent white rect
                glow_surface = pygame.Surface((icon["rect"].width + 10, icon["rect"].height + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (255, 255, 255, int(icon["hover_alpha"])), glow_surface.get_rect())
                screen.blit(glow_surface, (icon["rect"].x - 5, icon["rect"].y - 5))
            screen.blit(icon_surface, icon["rect"].topleft)
            if self.active_icon == icon and self.tooltip_alpha > 0:
                tooltip_text = self.font.render(icon["tooltip"], True, (255, 255, 255))
                tooltip_text.set_alpha(int(self.tooltip_alpha))
                tooltip_rect = tooltip_text.get_rect(center=(icon["rect"].x + icon["rect"].width / 2, icon["rect"].y - 30))
                tooltip_bg_rect = tooltip_rect.inflate(10, 5)
                tooltip_bg = pygame.Surface(tooltip_bg_rect.size, pygame.SRCALPHA)
                tooltip_bg.fill((0, 0, 0, int(self.tooltip_alpha * 0.7)))
                screen.blit(tooltip_bg, tooltip_bg_rect)
                screen.blit(tooltip_text, tooltip_rect)

        # Render player sprite
        sprite = self.animations[self.facing][self.anim_index]
        scaled_sprite = pygame.transform.scale(sprite, (self.player_width, self.player_height))
        draw_pos = (self.player_x - self.player_width // 2, self.player_y - self.player_height // 2)
        screen.blit(scaled_sprite, draw_pos)

        # Render "Press Q to quit" with pulsing background
        quit_text = self.font.render("Press Q to quit", True, (255, 255, 255))
        quit_rect = quit_text.get_rect(center=(400, 570))
        background_rect = quit_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), background_rect)
        screen.blit(quit_text, quit_rect)

        # Render error message if any
        if self.error_message:
            error_text = self.font.render(self.error_message, True, (255, 50, 50))
            error_rect = error_text.get_rect(center=(400, 100))
            error_bg_rect = error_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), background_rect)
            screen.blit(error_text, error_rect)