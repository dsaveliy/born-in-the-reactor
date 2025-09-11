# import pygame
# import json
# import math
# from state import State, GameState

# class HelpState(State):
#     def __init__(self, game):
#         super().__init__(game)
#         try:
#             self.font = pygame.font.Font("assets/fonts/ShareTechMono-Regular.ttf", 32)
#         except FileNotFoundError:
#             print("Error loading fonts, using default")
#             self.font = pygame.font.Font(None, 36)

#         try:
#             with open("assets/main/help.json", "r", encoding='utf-8') as f:
#                 self.config = json.load(f)
#         except (FileNotFoundError, json.JSONDecodeError) as e:
#             print(f"Error loading help.json: {e}")
#             self.config = {
#                 "background": "assets/bgs/help_bg.png",
#                 "options": [
#                     {"name": "Description", "message": "Born in the Reactor is a gripping 2D survival shooter..."},
#                     {"name": "Hotkeys", "message": "WASD/Arrows: Move, Left Mouse: Shoot, 1/2/3: Switch Weapon (Pistol/Rifle/Shotgun), R: Reload, I: Inventory, Enter: Select, ESC: Back, Q: Quit, M: Settings, T: Stats, H: Help"},
#                     {"name": "About", "message": "BORN IN THE REACTOR, Developed by Davydovich Saveliy & Kamyno Maxim, 2025"},
#                     {"name": "Back to Menu", "message": ""}
#                 ]
#             }

#         try:
#             self.background = pygame.image.load(self.config["background"]).convert()
#             self.background = pygame.transform.scale(self.background, (800, 600))
#         except FileNotFoundError:
#             print(f"Error loading help background {self.config['background']}")
#             self.background = pygame.Surface((800, 600))
#             self.background.fill((40, 60, 40))

#         self.options = [option["name"] for option in self.config["options"]]
#         self.messages = {option["name"]: option["message"] for option in self.config["options"]}
#         self.selected_option = 0
#         self.last_keyboard_selected = 0  # Запоминаем последний выбор клавиатурой
#         self.message = None
#         self.action_triggered = False
#         self.text_pulse = 0
#         self.option_rects = []  # Store rectangles for mouse interaction
#         self.options_bounding_rect = None  # Ограничивающий прямоугольник для всех кнопок
#         self.back_rect = pygame.Rect(0, 0, 0, 0)  # Rectangle for "Back to Menu" button
#         self.scroll_offset = 0  # For scrolling "Description"

#     def enter(self):
#         print("Entered Help State")
#         self.selected_option = 0
#         self.last_keyboard_selected = 0
#         self.message = None
#         self.action_triggered = False
#         self.text_pulse = 0
#         self.option_rects = []
#         self.options_bounding_rect = None
#         self.scroll_offset = 0

#     def exit(self):
#         print("Exiting Help State")
#         pygame.event.clear()  # Clear input events to prevent residual input

#     def update(self, dt):
#         keys = pygame.key.get_pressed()
#         mouse_pos = pygame.mouse.get_pos()
#         mouse_clicked = pygame.mouse.get_pressed()[0]  # Left click
#         mouse_pressed = pygame.mouse.get_pressed()  # All buttons
#         mouse_scroll = self.game.mouse_wheel  # Wheel scroll from Game

#         # Update text pulse effect
#         self.text_pulse += dt
#         if self.text_pulse >= 1.0:
#             self.text_pulse = 0

#         # Проверка ховера мыши только если нет сообщения (в главном меню опций)
#         if not self.message:
#             hovered = -1
#             for i, rect in enumerate(self.option_rects):
#                 if rect.collidepoint(mouse_pos):
#                     hovered = i
#                     break
#             if hovered != -1:
#                 self.selected_option = hovered  # Меняем выделение на ховер
#             elif self.options_bounding_rect and not self.options_bounding_rect.collidepoint(mouse_pos):
#                 self.selected_option = self.last_keyboard_selected  # Возврат к клавиатурному выбору, если курсор вне области кнопок

#         if self.message and self.options[self.selected_option] == "Description":
#             # Calculate max scroll
#             wrapped_lines = self.get_wrapped_lines(self.message)
#             total_drawn_height = len(wrapped_lines) * 40
#             visible_text_height = 320
#             max_scroll = max(0, total_drawn_height - visible_text_height)

#             # Handle scrolling for "Description" with keyboard
#             if keys[pygame.K_UP]:
#                 self.scroll_offset = max(self.scroll_offset - 10, 0)
#             elif keys[pygame.K_DOWN]:
#                 self.scroll_offset = min(self.scroll_offset + 10, max_scroll)

#             # Прокрутка при зажатой правой кнопке мыши (drag)
#             if mouse_pressed[2]:  # Right button
#                 _, dy = pygame.mouse.get_rel()
#                 self.scroll_offset -= dy  # Move up: increase offset, show lower text
#                 self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

#             # Прокрутка колесом мыши
#             if mouse_scroll != 0:
#                 self.scroll_offset -= mouse_scroll * 30  # y > 0: scroll up, decrease offset
#                 self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

#             # Handle popup navigation
#             if (keys[pygame.K_RETURN] or (mouse_clicked and self.back_rect.collidepoint(mouse_pos))) and not self.action_triggered:
#                 self.message = None
#                 self.scroll_offset = 0
#                 self.action_triggered = True
#         elif self.message:
#             # Handle popup navigation for other messages
#             if (keys[pygame.K_RETURN] or (mouse_clicked and self.back_rect.collidepoint(mouse_pos))) and not self.action_triggered:
#                 self.message = None
#                 self.action_triggered = True
#         else:
#             if keys[pygame.K_ESCAPE] and not self.action_triggered:
#                 print("Returning to main menu from Help via ESC")
#                 pygame.event.clear()  # Clear input to prevent carryover
#                 self.game.change_state(GameState.MAIN_MENU)
#                 self.action_triggered = True
#             elif keys[pygame.K_DOWN] and not self.action_triggered:
#                 self.selected_option = (self.selected_option + 1) % len(self.options)
#                 self.last_keyboard_selected = self.selected_option  # Обновляем только при клавиатуре
#                 print(f"Selected option: {self.options[self.selected_option]}")
#                 self.action_triggered = True
#             elif keys[pygame.K_UP] and not self.action_triggered:
#                 self.selected_option = (self.selected_option - 1) % len(self.options)
#                 self.last_keyboard_selected = self.selected_option  # Обновляем только при клавиатуре
#                 print(f"Selected option: {self.options[self.selected_option]}")
#                 self.action_triggered = True
#             elif (keys[pygame.K_RETURN] or (mouse_clicked and self.option_rects and self.option_rects[self.selected_option].collidepoint(mouse_pos))) and not self.action_triggered:
#                 self.action_triggered = True
#                 print(f"Enter pressed, selected_option={self.selected_option}")
#                 if self.options[self.selected_option] == "Back to Menu":
#                     print("Returning to main menu from Help via Back to Menu")
#                     pygame.event.clear()  # Clear input to prevent carryover
#                     self.game.change_state(GameState.MAIN_MENU)
#                 else:
#                     self.message = self.messages[self.options[self.selected_option]]

#         if not keys[pygame.K_RETURN] and not keys[pygame.K_UP] and not keys[pygame.K_DOWN] and not keys[pygame.K_ESCAPE] and not mouse_clicked:
#             self.action_triggered = False

#     def get_wrapped_lines(self, text):
#         max_width = 560  # popup_width - 40
#         lines = text.split("\n")
#         wrapped_lines = []
#         for line in lines:
#             words = line.split()
#             current_line = ""
#             for word in words:
#                 test_line = current_line + word + " "
#                 if self.font.size(test_line)[0] <= max_width:
#                     current_line = test_line
#                 else:
#                     if current_line:
#                         wrapped_lines.append(current_line.strip())
#                     current_line = word + " "
#             if current_line:
#                 wrapped_lines.append(current_line.strip())
#         return wrapped_lines

#     def render(self, screen):
#         pulse_alpha = 180 + int(30 * (1 + math.sin(self.text_pulse * math.pi)) / 2)  # Pulse between 180-210

#         screen.blit(self.background, (0, 0))
#         self.option_rects = []  # Reset rectangles each frame
#         for i, option in enumerate(self.options):
#             color = (0, 0, 0)
#             text = self.font.render(option, True, color)
#             rect = text.get_rect(center=(400, 150 + i * 50))
#             self.option_rects.append(rect)
#             if i == self.selected_option:
#                 background_rect = rect.inflate(20, 10)
#                 pygame.draw.rect(screen, (255, 255, 255, pulse_alpha), background_rect)
#             screen.blit(text, rect)

#         # Вычисляем узкий ограничивающий прямоугольник
#         if self.option_rects:
#             max_left = max(r.left for r in self.option_rects)
#             min_right = min(r.right for r in self.option_rects)
#             min_top = min(r.top for r in self.option_rects)
#             max_bottom = max(r.bottom for r in self.option_rects)
#             width = min_right - max_left
#             height = max_bottom - min_top
#             if width > 0 and height > 0:
#                 self.options_bounding_rect = pygame.Rect(max_left, min_top, width, height)
#             else:
#                 self.options_bounding_rect = None

#         if self.message:
#             popup_width, popup_height = 600, 400
#             popup_x, popup_y = (800 - popup_width) // 2, (600 - popup_height) // 2
#             popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
#             pygame.draw.rect(screen, (255, 255, 255), popup_rect)
#             pygame.draw.rect(screen, (0, 0, 0), popup_rect, 2)  # Black border

#             wrapped_lines = self.get_wrapped_lines(self.message)
#             y_offset = popup_y + 7 - (self.scroll_offset if self.options[self.selected_option] == "Description" else 0)  # 7px top margin
#             visible_height = popup_y + 7 + 320  # Adjusted for increased text space (320px visible text height)
#             for line in wrapped_lines:
#                 line_text = self.font.render(line, True, (0, 0, 0))
#                 if y_offset + 40 > popup_y + 7 and y_offset < visible_height:
#                     screen.blit(line_text, (popup_x + 20, y_offset))
#                 y_offset += 40  # Line height

#             back_text = self.font.render("Back to Menu", True, (0, 0, 0))
#             self.back_rect = back_text.get_rect(center=(popup_x + popup_width // 2, popup_y + popup_height - 40))
#             pygame.draw.rect(screen, (200, 200, 200), self.back_rect.inflate(20, 10))
#             screen.blit(back_text, self.back_rect)

#             if self.options[self.selected_option] == "Description" and len(wrapped_lines) * 40 > 320:
#                 scrollbar_height = (320 / (len(wrapped_lines) * 40)) * 320  # Adjusted for visible text height
#                 scrollbar_y = popup_y + 7 + (self.scroll_offset / (len(wrapped_lines) * 40 - 320)) * (320 - scrollbar_height)
#                 pygame.draw.rect(screen, (150, 150, 150), (popup_x + popup_width - 20, scrollbar_y, 10, scrollbar_height))
import pygame
import json
import math
from state import State, GameState

class HelpState(State):
    def __init__(self, game):
        super().__init__(game)
        try:
            self.font = pygame.font.Font("assets/fonts/ShareTechMono-Regular.ttf", 32)
            self.small_font = pygame.font.Font("assets/fonts/Orbitron-Bold.ttf", 24)
        except FileNotFoundError:
            print("Error loading fonts, using default")
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)

        try:
            with open("assets/main/help.json", "r", encoding='utf-8') as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading help.json: {e}")
            self.config = {
                "background": "assets/bgs/help_bg.jpg",
                "options": [
                    {"name": "Description", "message": "Born in the Reactor is a gripping 2D survival shooter set in a post-apocalyptic world ravaged by a catastrophic Chernobyl meltdown. You play as a lone survivor navigating the eerie streets of Gomel, abandoned hospitals, and a forsaken military base, all leading to the reactor's heart. Battle mutated creatures with limited weapons, uncover the disaster's dark secrets through environmental storytelling, and face a chilling final boss in a tense, atmospheric journey.\n\nWith dynamic combat and a haunting soundtrack, the game challenges your survival skills across four levels of increasing difficulty. Use WASD to move, mouse to aim and shoot, and explore to find health kits. The detailed narrative unfolds through the environment, offering a rich experience without excessive dialogue."},
                    {"name": "Hotkeys", "message": "WASD/Arrows: Move, Left Mouse: Shoot, 1/2/3: Switch Weapon (Pistol/Rifle/Shotgun), R: Reload, I: Inventory, Enter: Select, ESC: Back, Q: Quit, M: Settings, T: Stats, H: Help"},
                    {"name": "About", "message": "BORN IN THE REACTOR, Developed by Davydovich Saveliy & Kamyno Maxim, 2025"}
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
        self.last_keyboard_selected = 0  # Запоминаем последний выбор клавиатурой
        self.message = None
        self.action_triggered = False
        self.text_pulse = 0
        self.option_rects = []  # Store rectangles for mouse interaction
        self.options_bounding_rect = None  # Ограничивающий прямоугольник для всех кнопок
        self.back_rect = pygame.Rect(0, 0, 0, 0)  # Rectangle for "Back to Menu" button
        self.scroll_offset = 0  # For scrolling "Description"

    def enter(self):
        print("Entered Help State")
        self.selected_option = 0
        self.last_keyboard_selected = 0
        self.message = None
        self.action_triggered = False
        self.text_pulse = 0
        self.option_rects = []
        self.options_bounding_rect = None
        self.scroll_offset = 0

    def exit(self):
        print("Exiting Help State")
        pygame.event.clear()  # Clear input events to prevent residual input

    def update(self, dt):
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]  # Left click
        mouse_pressed = pygame.mouse.get_pressed()  # All buttons
        mouse_scroll = self.game.mouse_wheel  # Wheel scroll from Game

        # Update text pulse effect
        self.text_pulse += dt
        if self.text_pulse >= 1.0:
            self.text_pulse = 0

        # Проверка ховера мыши только если нет сообщения (в главном меню опций)
        if not self.message:
            hovered = -1
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(mouse_pos):
                    hovered = i
                    break
            if hovered != -1:
                self.selected_option = hovered  # Меняем выделение на ховер
            elif self.options_bounding_rect and not self.options_bounding_rect.collidepoint(mouse_pos):
                self.selected_option = self.last_keyboard_selected  # Возврат к клавиатурному выбору, если курсор вне области кнопок

        if self.message and self.options[self.selected_option] == "Description":
            # Calculate max scroll
            wrapped_lines = self.get_wrapped_lines(self.message)
            total_drawn_height = len(wrapped_lines) * 40
            visible_text_height = 360  # Increased for more text space
            max_scroll = max(0, total_drawn_height - visible_text_height)

            # Handle scrolling for "Description" with keyboard
            if keys[pygame.K_UP]:
                self.scroll_offset = max(self.scroll_offset - 10, 0)
            elif keys[pygame.K_DOWN]:
                self.scroll_offset = min(self.scroll_offset + 10, max_scroll)

            # Прокрутка при зажатой правой кнопке мыши (drag)
            if mouse_pressed[2]:  # Right button
                _, dy = pygame.mouse.get_rel()
                self.scroll_offset -= dy  # Move up: increase offset, show lower text
                self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

            # Прокрутка колесом мыши
            if mouse_scroll != 0:
                self.scroll_offset -= mouse_scroll * 30  # y > 0: scroll up, decrease offset
                self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

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
                self.last_keyboard_selected = self.selected_option  # Обновляем только при клавиатуре
                print(f"Selected option: {self.options[self.selected_option]}")
                self.action_triggered = True
            elif keys[pygame.K_UP] and not self.action_triggered:
                self.selected_option = (self.selected_option - 1) % len(self.options)
                self.last_keyboard_selected = self.selected_option  # Обновляем только при клавиатуре
                print(f"Selected option: {self.options[self.selected_option]}")
                self.action_triggered = True
            elif (keys[pygame.K_RETURN] or (mouse_clicked and self.option_rects and self.option_rects[self.selected_option].collidepoint(mouse_pos))) and not self.action_triggered:
                self.action_triggered = True
                print(f"Enter pressed, selected_option={self.selected_option}")
                self.message = self.messages[self.options[self.selected_option]]

        if not keys[pygame.K_RETURN] and not keys[pygame.K_UP] and not keys[pygame.K_DOWN] and not keys[pygame.K_ESCAPE] and not mouse_clicked:
            self.action_triggered = False

    def get_wrapped_lines(self, text):
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
        pulse_alpha = 180 + int(30 * (1 + math.sin(self.text_pulse * math.pi)) / 2)  # Pulse between 180-210

        screen.blit(self.background, (0, 0))
        self.option_rects = []  # Reset rectangles each frame
        for i, option in enumerate(self.options):
            color = (0, 0, 0)
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(400, 150 + i * 50))
            self.option_rects.append(rect)
            if i == self.selected_option:
                background_rect = rect.inflate(20, 10)
                pygame.draw.rect(screen, (255, 255, 255, pulse_alpha), background_rect)
            screen.blit(text, rect)

        # Вычисляем узкий ограничивающий прямоугольник
        if self.option_rects:
            max_left = max(r.left for r in self.option_rects)
            min_right = min(r.right for r in self.option_rects)
            min_top = min(r.top for r in self.option_rects)
            max_bottom = max(r.bottom for r in self.option_rects)
            width = min_right - max_left
            height = max_bottom - min_top
            if width > 0 and height > 0:
                self.options_bounding_rect = pygame.Rect(max_left, min_top, width, height)
            else:
                self.options_bounding_rect = None

        if self.message:
            popup_width, popup_height = 600, 400
            popup_x, popup_y = (800 - popup_width) // 2, (600 - popup_height) // 2
            popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
            pygame.draw.rect(screen, (255, 255, 255), popup_rect)
            pygame.draw.rect(screen, (0, 0, 0), popup_rect, 2)  # Black border

            wrapped_lines = self.get_wrapped_lines(self.message)
            y_offset = popup_y + 7 - (self.scroll_offset if self.options[self.selected_option] == "Description" else 0)  # 7px top margin
            visible_height = popup_y + 7 + 360  # Increased for more text space (360px visible text height)
            for line in wrapped_lines:
                line_text = self.font.render(line, True, (0, 0, 0))
                if y_offset + 40 > popup_y + 7 and y_offset < visible_height:
                    screen.blit(line_text, (popup_x + 20, y_offset))
                y_offset += 40  # Line height

            back_text = self.font.render("Back to Menu", True, (0, 0, 0))
            self.back_rect = back_text.get_rect(center=(popup_x + popup_width // 2, popup_y + popup_height - 40))
            pygame.draw.rect(screen, (200, 200, 200), self.back_rect.inflate(20, 10))
            screen.blit(back_text, self.back_rect)

            if self.options[self.selected_option] == "Description" and len(wrapped_lines) * 40 > 360:
                scrollbar_height = (360 / (len(wrapped_lines) * 40)) * 360  # Adjusted for visible text height
                scrollbar_y = popup_y + 7 + (self.scroll_offset / (len(wrapped_lines) * 40 - 360)) * (360 - scrollbar_height)
                pygame.draw.rect(screen, (150, 150, 150), (popup_x + popup_width - 20, scrollbar_y, 10, scrollbar_height))
        else:
            # Render "Press ESC to return"
            return_text = self.small_font.render("Press ESC to return", True, (255, 255, 255))
            return_rect = return_text.get_rect(center=(400, 500))
            return_bg_rect = return_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), return_bg_rect)
            screen.blit(return_text, return_rect)