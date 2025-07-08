import pygame
import json
import os
from state import State, GameState
from config.settings import Settings
from config.stats import Stats

class MainMenuState(State):
    def __init__(self, game):
        super().__init__(game)
        # Use thin post-apocalyptic font (Orbitron-Light)
        try:
            self.font = pygame.font.Font("assets/fonts/Orbitron-Light.ttf", 36)
            self.title_font = pygame.font.Font("assets/fonts/Orbitron-Light.ttf", 48)
        except FileNotFoundError:
            print("Error loading Orbitron-Light font, using default")
            self.font = pygame.font.Font(None, 36)
            self.title_font = pygame.font.Font(None, 48)
        
        self.settings = Settings()
        self.stats = Stats()
        self.main_options = ["Play", "Settings", "Stats", "Help", "Exit"]
        self.help_options = ["Description", "Hotkeys", "About", "Back"]
        self.options = self.main_options
        self.selected_option = 0
        self.in_help_menu = False
        self.show_stats = False
        self.show_settings = False
        self.message = None
        self.action_triggered = False

        # Load main.json
        try:
            with open("assets/main/main.json", "r") as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading main.json: {e}")
            self.config = {
                "background": "assets/bgs/main_menu.png",
                "stats_background": "assets/bgs/stats_bg.png",
                "settings_background": "assets/bgs/settings_bg.png",
                "help_background": "assets/bgs/help_bg.png",
                "icons": []
            }

        # Load backgrounds
        try:
            self.main_background = pygame.image.load(self.config["background"]).convert()
            self.main_background = pygame.transform.scale(self.main_background, (800, 600))
        except FileNotFoundError:
            print(f"Error loading background {self.config['background']}")
            self.main_background = pygame.Surface((800, 600))
            self.main_background.fill((20, 20, 40))

        try:
            self.stats_background = pygame.image.load(self.config["stats_background"]).convert()
            self.stats_background = pygame.transform.scale(self.stats_background, (800, 600))
        except FileNotFoundError:
            print(f"Error loading stats background {self.config['stats_background']}")
            self.stats_background = pygame.Surface((800, 600))
            self.stats_background.fill((50, 50, 50))

        try:
            self.settings_background = pygame.image.load(self.config["settings_background"]).convert()
            self.settings_background = pygame.transform.scale(self.settings_background, (800, 600))
        except FileNotFoundError:
            print(f"Error loading settings background {self.config['settings_background']}")
            self.settings_background = pygame.Surface((800, 600))
            self.settings_background.fill((30, 30, 60))

        try:
            self.help_background = pygame.image.load(self.config["help_background"]).convert()
            self.help_background = pygame.transform.scale(self.help_background, (800, 600))
        except FileNotFoundError:
            print(f"Error loading help background {self.config['help_background']}")
            self.help_background = pygame.Surface((800, 600))
            self.help_background.fill((40, 60, 40))

        # Load icons
        self.icons = []
        for icon in self.config.get("icons", []):
            try:
                img = pygame.image.load(icon["image"]).convert_alpha()
                img = pygame.transform.scale(img, (icon["width"], icon["height"]))
                self.icons.append({
                    "image": img,
                    "rect": pygame.Rect(icon["x"], icon["y"], icon["width"], icon["height"]),
                    "name": icon["name"],
                    "tooltip": icon["tooltip"]
                })
            except FileNotFoundError:
                print(f"Error loading icon {icon['image']}")

        # Green square
        self.square_pos = [400, 300]
        self.square_size = 30
        self.square_speed = 200
        self.square_rect = pygame.Rect(self.square_pos[0], self.square_pos[1], self.square_size, self.square_size)
        self.tooltip = None

    def enter(self):
        print("Entered Main Menu State")
        self.in_help_menu = False
        self.show_stats = False
        self.show_settings = False
        self.options = self.main_options
        self.selected_option = 0
        self.message = None
        self.action_triggered = False
        self.square_pos = [400, 300]
        self.tooltip = None

    def exit(self):
        print("Exiting Main Menu State")

    def update(self, dt):
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        # Move green square (disabled in stats, settings, or help submenu)
        if not self.show_stats and not self.show_settings and not self.in_help_menu:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.square_pos[1] -= self.square_speed * dt
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.square_pos[1] += self.square_speed * dt
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.square_pos[0] -= self.square_speed * dt
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.square_pos[0] += self.square_speed * dt

            # Constrain to screen bounds
            self.square_pos[0] = max(0, min(self.square_pos[0], 800 - self.square_size))
            self.square_pos[1] = max(0, min(self.square_pos[1], 600 - self.square_size))
            self.square_rect.topleft = self.square_pos

            # Check icon collisions for tooltips (square or mouse)
            self.tooltip = None
            mouse_rect = pygame.Rect(mouse_pos[0], mouse_pos[1], 1, 1)
            for icon in self.icons:
                if self.square_rect.colliderect(icon["rect"]) or mouse_rect.colliderect(icon["rect"]):
                    self.tooltip = icon["tooltip"]
                    break

        # Exit submenus with ESC
        if self.show_stats or self.show_settings or self.in_help_menu:
            if keys[pygame.K_ESCAPE] and not self.action_triggered:
                print(f"Exiting submenu: stats={self.show_stats}, settings={self.show_settings}, help={self.in_help_menu}")
                self.show_stats = False
                self.show_settings = False
                self.in_help_menu = False
                self.options = self.main_options
                self.selected_option = 0
                self.message = None
                self.tooltip = None
                self.action_triggered = True
        else:
            # Menu navigation
            if keys[pygame.K_DOWN] and not self.action_triggered:
                self.selected_option = (self.selected_option + 1) % len(self.options)
                print(f"Selected option: {self.options[self.selected_option]}")
            if keys[pygame.K_UP] and not self.action_triggered:
                self.selected_option = (self.selected_option - 1) % len(self.options)
                print(f"Selected option: {self.options[self.selected_option]}")

            # Menu actions (Enter)
            if keys[pygame.K_RETURN] and not self.action_triggered:
                self.action_triggered = True
                print(f"Enter pressed, selected_option={self.selected_option}, in_help_menu={self.in_help_menu}")
                if self.in_help_menu:
                    if self.selected_option == 0:  # Description
                        self.message = "A post-apocalyptic shooter set in a reactor."
                    elif self.selected_option == 1:  # Hotkeys
                        self.message = "WASD/Arrows: Move, Space: Shoot, I: Inventory"
                    elif self.selected_option == 2:  # About
                        self.message = "BORN IN THE REACTOR, developed by xAI, 2025"
                    elif self.selected_option == 3:  # Back
                        print("Returning to main menu from Help")
                        self.in_help_menu = False
                        self.options = self.main_options
                        self.selected_option = 0
                        self.message = None
                        self.tooltip = None
                else:
                    if self.selected_option == 0:  # Play
                        print("Transitioning to GameState.GAMEPLAY")
                        self.game.change_state(GameState.GAMEPLAY)
                    elif self.selected_option == 1:  # Settings
                        self.show_settings = True
                        self.options = []
                        current_level = self.settings.get_initial_level()
                        new_level = "gomel_streets" if current_level == "intro" else "intro"
                        self.settings.data["initial_level"] = new_level
                        self.settings.save_settings()
                        self.message = f"Initial level set to: {new_level}"
                        print(f"Entered Settings, level set to {new_level}")
                    elif self.selected_option == 2:  # Stats
                        self.show_stats = True
                        self.options = []
                        self.message = None
                        print("Entered Stats")
                    elif self.selected_option == 3:  # Help
                        self.in_help_menu = True
                        self.options = self.help_options
                        self.selected_option = 0
                        self.message = None
                        print("Entered Help")
                    elif self.selected_option == 4:  # Exit
                        print("Exiting game")
                        self.game.running = False
            # Icon-specific actions (keys or mouse click)
            elif self.tooltip and not self.in_help_menu:
                if (keys[pygame.K_s] or (mouse_clicked and self.tooltip == "Press S for Settings")) and not self.action_triggered:
                    self.action_triggered = True
                    self.show_settings = True
                    self.options = []
                    current_level = self.settings.get_initial_level()
                    new_level = "gomel_streets" if current_level == "intro" else "intro"
                    self.settings.data["initial_level"] = new_level
                    self.settings.save_settings()
                    self.message = f"Initial level set to: {new_level}"
                    print(f"Entered Settings via icon, level set to {new_level}")
                elif (keys[pygame.K_t] or (mouse_clicked and self.tooltip == "Press T for Stats")) and not self.action_triggered:
                    self.action_triggered = True
                    self.show_stats = True
                    self.options = []
                    self.message = None
                    print("Entered Stats via icon")
                elif (keys[pygame.K_h] or (mouse_clicked and self.tooltip == "Press H for Help")) and not self.action_triggered:
                    self.action_triggered = True
                    self.in_help_menu = True
                    self.options = self.help_options
                    self.selected_option = 0
                    self.message = None
                    print("Entered Help via icon")
            # Global quit
            elif keys[pygame.K_q]:
                print("Exiting game via Q")
                self.game.running = False

        # Reset action_triggered when all inputs are released
        if not keys[pygame.K_RETURN] and not keys[pygame.K_s] and not keys[pygame.K_t] and not keys[pygame.K_h] and not mouse_clicked and not keys[pygame.K_ESCAPE]:
            self.action_triggered = False

    def render(self, screen):
        # Select background based on state
        if self.show_stats:
            screen.blit(self.stats_background, (0, 0))
        elif self.show_settings:
            screen.blit(self.settings_background, (0, 0))
        elif self.in_help_menu:
            screen.blit(self.help_background, (0, 0))
        else:
            screen.blit(self.main_background, (0, 0))

        # Title at top (main menu only)
        if not self.show_stats and not self.show_settings and not self.in_help_menu:
            title = self.title_font.render("BORN IN THE REACTOR", True, (255, 255, 255))
            screen.blit(title, (400 - title.get_width() // 2, 10))

            # "Press enter to play"
            play_text = self.font.render("Press enter to play", True, (255, 255, 255))
            screen.blit(play_text, (400 - play_text.get_width() // 2, 80))

            # Render icons
            for icon in self.icons:
                screen.blit(icon["image"], icon["rect"].topleft)

            # Render green square
            pygame.draw.rect(screen, (0, 255, 0), self.square_rect)

            # Render tooltip
            if self.tooltip:
                tooltip_text = self.font.render(self.tooltip, True, (255, 255, 255))
                screen.blit(tooltip_text, (400 - tooltip_text.get_width() // 2, 240))

        # Render help submenu
        if self.in_help_menu:
            for i, option in enumerate(self.options):
                color = (255, 255, 255) if i != self.selected_option else (255, 200, 0)
                text = self.font.render(option, True, color)
                screen.blit(text, (400 - text.get_width() // 2, 150 + i * 50))

        # Render message (Settings or Help)
        if self.message and (self.show_settings or self.in_help_menu):
            message_text = self.font.render(self.message, True, (255, 255, 255))
            screen.blit(message_text, (400 - message_text.get_width() // 2, 240))

        # "Press Q to quit" (main menu) or "Press ESC to return" (submenus)
        if self.show_stats or self.show_settings or self.in_help_menu:
            return_text = self.font.render("Press ESC to return", True, (255, 255, 255))
            screen.blit(return_text, (400 - return_text.get_width() // 2, 540))
        else:
            quit_text = self.font.render("Press Q to quit", True, (255, 255, 255))
            screen.blit(quit_text, (400 - quit_text.get_width() // 2, 570))