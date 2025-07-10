import pygame
import json
import math
from state import State, GameState

class HelpState(State):
    def __init__(self, game):
        super().__init__(game)
        try:
            self.font = pygame.font.Font("assets/fonts/ShareTechMono-Regular.ttf", 32)
        except FileNotFoundError:
            print("Error loading fonts, using default")
            self.font = pygame.font.Font(None, 36)

        try:
            with open("assets/main/help.json", "r") as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading help.json: {e}")
            self.config = {
                "background": "assets/bgs/help_bg.png",
                "options": [
                    {"name": "Description", "message": "Born in the Reactor is a gripping 2D survival shooter..."},
                    {"name": "Hotkeys", "message": "WASD/Arrows: Move, Left Mouse: Shoot, 1/2/3: Switch Weapon (Pistol/Rifle/Shotgun), R: Reload, I: Inventory, Enter: Select, ESC: Back, Q: Quit, M: Settings, T: Stats, H: Help"},
                    {"name": "About", "message": "BORN IN THE REACTOR, Developed by Davydovich Saveliy & Kamyno Maxim, 2025"},
                    {"name": "Back to Menu", "message": ""}
                ]
            }

        try:
            self.background = pygame.image.load(self.config["background"]).convert()
            self.background = pygame.transform.scale(self.background, (800, 600))
        except FileNotFoundError:
            print(f"Error loading help background {self.config['background']}")
            self.background = pygame.Surface((800, 600))
            self.background.fill((40, 60, 40))

        self.options = [option["name"] for option in self.config["options"]]
        self.messages = {option["name"]: option["message"] for option in self.config["options"]}
        self.selected_option = 0
        self.message = None
        self.action_triggered = False
        self.text_pulse = 0
        self.option_rects = []  # Store rectangles for mouse interaction
        self.back_rect = pygame.Rect(0, 0, 0, 0)  # Rectangle for "Back to Menu" button
        self.scroll_offset = 0  # For scrolling "Description"

    def enter(self):
        print("Entered Help State")
        self.selected_option = 0
        self.message = None
        self.action_triggered = False
        self.text_pulse = 0
        self.option_rects = []
        self.scroll_offset = 0

    def exit(self):
        print("Exiting Help State")
        pygame.event.clear()  # Clear input events to prevent residual input

    def update(self, dt):
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        mouse_scroll = pygame.mouse.get_rel()[1]  # Mouse wheel movement

        # Update text pulse effect
        self.text_pulse += dt
        if self.text_pulse >= 1.0:
            self.text_pulse = 0

        if self.message and self.options[self.selected_option] == "Description":
            # Handle scrolling for "Description" with reduced speed
            if keys[pygame.K_UP] or mouse_scroll > 0:
                self.scroll_offset = max(self.scroll_offset - 10, 0)
            elif keys[pygame.K_DOWN] or mouse_scroll < 0:
                # Calculate max scroll based on total height of wrapped lines
                max_scroll = max(0, sum(self.font.size(line)[1] for line in self.get_wrapped_lines(self.message)) - 300)
                self.scroll_offset = min(self.scroll_offset + 10, max_scroll)
            # Handle popup navigation
            if (keys[pygame.K_RETURN] or (mouse_clicked and self.back_rect.collidepoint(mouse_pos))) and not self.action_triggered:
                self.message = None
                self.scroll_offset = 0
                self.action_triggered = True
        elif self.message:
            # Handle popup navigation for other messages
            if (keys[pygame.K_RETURN] or (mouse_clicked and self.back_rect.collidepoint(mouse_pos))) and not self.action_triggered:
                self.message = None
                self.action_triggered = True
        else:
            if keys[pygame.K_ESCAPE] and not self.action_triggered:
                print("Returning to main menu from Help via ESC")
                pygame.event.clear()  # Clear input to prevent carryover
                self.game.change_state(GameState.MAIN_MENU)
                self.action_triggered = True
            elif keys[pygame.K_DOWN] and not self.action_triggered:
                self.selected_option = (self.selected_option + 1) % len(self.options)
                print(f"Selected option: {self.options[self.selected_option]}")
                self.action_triggered = True
            elif keys[pygame.K_UP] and not self.action_triggered:
                self.selected_option = (self.selected_option - 1) % len(self.options)
                print(f"Selected option: {self.options[self.selected_option]}")
                self.action_triggered = True
            elif (keys[pygame.K_RETURN] or (mouse_clicked and self.option_rects and self.option_rects[self.selected_option].collidepoint(mouse_pos))) and not self.action_triggered:
                self.action_triggered = True
                print(f"Enter pressed, selected_option={self.selected_option}")
                if self.options[self.selected_option] == "Back to Menu":
                    print("Returning to main menu from Help via Back to Menu")
                    pygame.event.clear()  # Clear input to prevent carryover
                    self.game.change_state(GameState.MAIN_MENU)
                else:
                    self.message = self.messages[self.options[self.selected_option]]

        if not keys[pygame.K_RETURN] and not keys[pygame.K_UP] and not keys[pygame.K_DOWN] and not keys[pygame.K_ESCAPE] and not mouse_clicked:
            self.action_triggered = False

    def get_wrapped_lines(self, text):
        # Helper method to get wrapped lines
        max_width = 560  # popup_width - 40
        lines = text.split("\n")
        wrapped_lines = []
        for line in lines:
            words = line.split()
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                if self.font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        wrapped_lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                wrapped_lines.append(current_line.strip())
        return wrapped_lines

    def render(self, screen):
        # Calculate pulse_alpha for all rendering blocks
        pulse_alpha = 180 + int(30 * (1 + math.sin(self.text_pulse * math.pi)) / 2)  # Pulse between 180-210

        screen.blit(self.background, (0, 0))
        self.option_rects = []  # Reset rectangles each frame
        for i, option in enumerate(self.options):
            # All text black, selected option has a background
            color = (0, 0, 0)
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(400, 150 + i * 50))
            self.option_rects.append(rect)
            if i == self.selected_option:
                # Add semi-transparent background for selected option
                background_rect = rect.inflate(20, 10)
                pygame.draw.rect(screen, (255, 255, 255, pulse_alpha), background_rect)
            screen.blit(text, rect)

        if self.message:
            # Render white popup window
            popup_width, popup_height = 600, 400
            popup_x, popup_y = (800 - popup_width) // 2, (600 - popup_height) // 2
            popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
            pygame.draw.rect(screen, (255, 255, 255), popup_rect)
            pygame.draw.rect(screen, (0, 0, 0), popup_rect, 2)  # Black border

            # Render wrapped text (already black)
            wrapped_lines = self.get_wrapped_lines(self.message)
            y_offset = popup_y + 20 - (self.scroll_offset if self.options[self.selected_option] == "Description" else 0)
            visible_height = popup_y + 340  # 400 - 60 (button space)
            for line in wrapped_lines:
                line_text = self.font.render(line, True, (0, 0, 0))
                if y_offset + 40 > popup_y and y_offset < visible_height:  # Only render within visible area
                    screen.blit(line_text, (popup_x + 20, y_offset))
                y_offset += 40  # Line height

            # Render "Back to Menu" button (already black)
            back_text = self.font.render("Back to Menu", True, (0, 0, 0))
            self.back_rect = back_text.get_rect(center=(popup_x + popup_width // 2, popup_y + popup_height - 40))
            pygame.draw.rect(screen, (200, 200, 200), self.back_rect.inflate(20, 10))
            screen.blit(back_text, self.back_rect)

            # Simple scrollbar (visual indicator, non-interactive)
            if self.options[self.selected_option] == "Description" and len(wrapped_lines) * 40 > 300:
                scrollbar_height = (300 / (len(wrapped_lines) * 40)) * 300
                scrollbar_y = popup_y + 20 + (self.scroll_offset / (len(wrapped_lines) * 40 - 300)) * (300 - scrollbar_height)
                pygame.draw.rect(screen, (150, 150, 150), (popup_x + popup_width - 20, scrollbar_y, 10, scrollbar_height))