import pygame
import json
import math
import os
from state import State, GameState

class SettingsState(State):
    def __init__(self, game):
        super().__init__(game)
        try:
            self.font = pygame.font.Font("assets/fonts/Orbitron-Bold.ttf", 24)
        except FileNotFoundError:
            print("Error loading Orbitron-Light font, using default")
            self.font = pygame.font.Font(None, 24)
        
        self.load_settings()
        self.message = None
        self.action_triggered = False
        self.text_pulse = 0  # For pulsing text background
        
        try:
            self.background = pygame.image.load("assets/bgs/settings_bg.png").convert()
            self.background = pygame.transform.scale(self.background, (800, 600))
        except FileNotFoundError:
            print("Error loading settings background")
            self.background = pygame.Surface((800, 600))
            self.background.fill((30, 30, 60))

    def load_settings(self, file_path="assets/settings/settings.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            # Validate initial_level to prevent KeyError in GameplayState
            if self.data.get("initial_level") not in ["gomel_streets", "hospital", "office"]:
                print(f"Invalid initial_level '{self.data.get('initial_level')}', resetting to 'gomel_streets'")
                self.data["initial_level"] = "gomel_streets"
                self.save_settings(file_path)
            # Ensure required settings exist
            if "sound_enabled" not in self.data:
                self.data["sound_enabled"] = True
            if "player" not in self.data:
                self.data["player"] = {}
            if "id" not in self.data["player"]:
                self.data["player"]["id"] = "default_player"
            if "photo" not in self.data["player"]:
                self.data["player"]["photo"] = "assets/player/default_avatar.png"
            if "nickname" not in self.data["player"]:
                self.data["player"]["nickname"] = "Survivor"
            if "health_damage_effect" not in self.data["player"]:
                self.data["player"]["health_damage_effect"] = True
            if "aim_line" not in self.data["player"]:
                self.data["player"]["aim_line"] = False
            if "shot_animation" not in self.data["player"]:
                self.data["player"]["shot_animation"] = True
                self.save_settings(file_path)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading settings: {e}")
            self.data = {
                "initial_level": "gomel_streets",
                "sound_enabled": True,
                "player": {
                    "id": "default_player",
                    "photo": "assets/player/default_avatar.png",
                    "nickname": "Survivor",
                    "initial_health": 100,
                    "initial_ammo": {
                        "pistol": 30,
                        "rifle": 50,
                        "shotgun": 20
                    },
                    "health_damage_effect": True,
                    "aim_line": False,
                    "shot_animation": True
                }
            }
            self.save_settings(file_path)

    def save_settings(self, file_path="assets/settings/settings.json"):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get_initial_level(self):
        return self.data.get("initial_level", "gomel_streets")

    def get_player_settings(self):
        return self.data.get("player", {})

    def enter(self):
        print("Entered Settings State")
        self.message = None
        self.action_triggered = False
        self.text_pulse = 0

    def exit(self):
        print("Exiting Settings State")

    def update(self, dt):
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        # Update text pulse effect
        self.text_pulse += dt
        if self.text_pulse >= 1.0:
            self.text_pulse = 0

        if keys[pygame.K_ESCAPE] and not self.action_triggered:
            self.game.change_state(GameState.MAIN_MENU)
            self.action_triggered = True

        # Dynamic toggle logic for settings
        if mouse_clicked and not self.action_triggered:
            # Toggle sound
            if 200 < mouse_pos[0] < 400 and 200 < mouse_pos[1] < 250:
                self.data["sound_enabled"] = not self.data["sound_enabled"]
                self.save_settings()
                self.action_triggered = True
            # Toggle health damage effect
            elif 450 < mouse_pos[0] < 650 and 200 < mouse_pos[1] < 250:
                self.data["player"]["health_damage_effect"] = not self.data["player"]["health_damage_effect"]
                self.save_settings()
                self.action_triggered = True
            # Toggle aiming line
            elif 200 < mouse_pos[0] < 400 and 350 < mouse_pos[1] < 400:
                self.data["player"]["aim_line"] = not self.data["player"]["aim_line"]
                self.save_settings()
                self.action_triggered = True
            # Toggle shot animation
            elif 450 < mouse_pos[0] < 650 and 350 < mouse_pos[1] < 400:
                self.data["player"]["shot_animation"] = not self.data["player"]["shot_animation"]
                self.save_settings()
                self.action_triggered = True

        if not keys[pygame.K_ESCAPE] and not mouse_clicked:
            self.action_triggered = False

    def render(self, screen):
        # Calculate pulse_alpha for all rendering blocks
        pulse_alpha = 180 + int(30 * (1 + math.sin(self.text_pulse * math.pi)) / 2)  # Pulse between 180-210

        screen.blit(self.background, (0, 0))
        
        # Render title
        title_text = self.font.render("Settings", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(400, 50))
        title_bg_rect = title_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), title_bg_rect)
        screen.blit(title_text, title_rect)

        # Render initial level
        level_text = self.font.render(f"Current Level: {self.get_initial_level()}", True, (255, 255, 255))
        level_rect = level_text.get_rect(center=(400, 100))
        level_bg_rect = level_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), level_bg_rect)
        screen.blit(level_text, level_rect)

        # Render sound (left column)
        sound_label = self.font.render("Sound", True, (255, 255, 255))
        sound_label_rect = sound_label.get_rect(center=(300, 175))
        sound_label_bg_rect = sound_label_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), sound_label_bg_rect)
        screen.blit(sound_label, sound_label_rect)

        sound_status = self.font.render("ON" if self.data["sound_enabled"] else "OFF", True, (255, 255, 255))
        sound_status_rect = sound_status.get_rect(center=(300, 225))
        sound_status_bg_rect = sound_status_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), sound_status_bg_rect)
        screen.blit(sound_status, sound_status_rect)

        # Render health damage effect (right column)
        health_effect_label = self.font.render("Health Damage Effect", True, (255, 255, 255))
        health_effect_label_rect = health_effect_label.get_rect(center=(550, 175))
        health_effect_bg_rect = health_effect_label_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), health_effect_bg_rect)
        screen.blit(health_effect_label, health_effect_label_rect)

        health_effect_status = self.font.render("ON" if self.data["player"]["health_damage_effect"] else "OFF", True, (255, 255, 255))
        health_effect_status_rect = health_effect_status.get_rect(center=(550, 225))
        health_effect_status_bg_rect = health_effect_status_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), health_effect_status_bg_rect)
        screen.blit(health_effect_status, health_effect_status_rect)

        # Render aiming line (left column)
        aim_line_label = self.font.render("Aiming Line", True, (255, 255, 255))
        aim_line_label_rect = aim_line_label.get_rect(center=(300, 325))
        aim_line_bg_rect = aim_line_label_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), aim_line_bg_rect)
        screen.blit(aim_line_label, aim_line_label_rect)

        aim_line_status = self.font.render("ON" if self.data["player"]["aim_line"] else "OFF", True, (255, 255, 255))
        aim_line_status_rect = aim_line_status.get_rect(center=(300, 375))
        aim_line_status_bg_rect = aim_line_status_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), aim_line_status_bg_rect)
        screen.blit(aim_line_status, aim_line_status_rect)

        # Render shot animation (right column)
        shot_anim_label = self.font.render("Shot Animation", True, (255, 255, 255))
        shot_anim_label_rect = shot_anim_label.get_rect(center=(550, 325))
        shot_anim_bg_rect = shot_anim_label_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), shot_anim_bg_rect)
        screen.blit(shot_anim_label, shot_anim_label_rect)

        shot_anim_status = self.font.render("ON" if self.data["player"]["shot_animation"] else "OFF", True, (255, 255, 255))
        shot_anim_status_rect = shot_anim_status.get_rect(center=(550, 375))
        shot_anim_status_bg_rect = shot_anim_status_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), shot_anim_status_bg_rect)
        screen.blit(shot_anim_status, shot_anim_status_rect)

        # Render return prompt
        return_text = self.font.render("Press ESC to return", True, (255, 255, 255))
        return_rect = return_text.get_rect(center=(400, 540))
        return_bg_rect = return_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), return_bg_rect)
        screen.blit(return_text, return_rect)
# import pygame
# import json
# import math
# import os
# from enum import Enum
# from state import State, GameState

# class AvatarType(Enum):
#     DEFAULT = "assets/player/default_avatar.png"
#     BEL = "assets/player/bel.png"
#     SAV = "assets/player/sav.png"

# class SettingsState(State):
#     def __init__(self, game):
#         super().__init__(game)
#         try:
#             self.font = pygame.font.Font("assets/fonts/Orbitron-Bold.ttf", 24)
#         except FileNotFoundError:
#             print("Error loading Orbitron-Light font, using default")
#             self.font = pygame.font.Font(None, 24)
        
#         self.load_settings()
#         self.message = None
#         self.action_triggered = False
#         self.text_pulse = 0
#         self.nickname_input_active = False
#         self.nickname_temp = self.data["player"]["nickname"]
        
#         try:
#             self.background = pygame.image.load("assets/bgs/settings_bg.png").convert()
#             self.background = pygame.transform.scale(self.background, (800, 600))
#         except FileNotFoundError:
#             print("Error loading settings background")
#             self.background = pygame.Surface((800, 600))
#             self.background.fill((30, 30, 60))

#     def load_settings(self, file_path="assets/settings/settings.json"):
#         try:
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 self.data = json.load(f)
#             if self.data.get("initial_level") not in ["gomel_streets", "hospital", "office"]:
#                 print(f"Invalid initial_level '{self.data.get('initial_level')}', resetting to 'gomel_streets'")
#                 self.data["initial_level"] = "gomel_streets"
#                 self.save_settings(file_path)
#             if "sound_enabled" not in self.data:
#                 self.data["sound_enabled"] = True
#             if "player" not in self.data:
#                 self.data["player"] = {}
#             if "id" not in self.data["player"]:
#                 self.data["player"]["id"] = "default_player"
#             if "photo" not in self.data["player"]:
#                 self.data["player"]["photo"] = AvatarType.DEFAULT.value
#             if "nickname" not in self.data["player"]:
#                 self.data["player"]["nickname"] = "Survivor"
#             if "health_damage_effect" not in self.data["player"]:
#                 self.data["player"]["health_damage_effect"] = True
#             if "aim_line" not in self.data["player"]:
#                 self.data["player"]["aim_line"] = False
#             if "shot_animation" not in self.data["player"]:
#                 self.data["player"]["shot_animation"] = True
#             # Validate avatar
#             if self.data["player"]["photo"] not in [avatar.value for avatar in AvatarType]:
#                 self.data["player"]["photo"] = AvatarType.DEFAULT.value
#                 self.save_settings(file_path)
#         except (FileNotFoundError, json.JSONDecodeError) as e:
#             print(f"Error loading settings: {e}")
#             self.data = {
#                 "initial_level": "gomel_streets",
#                 "sound_enabled": True,
#                 "player": {
#                     "id": "default_player",
#                     "photo": AvatarType.DEFAULT.value,
#                     "nickname": "Survivor",
#                     "initial_health": 100,
#                     "initial_ammo": {
#                         "pistol": 30,
#                         "rifle": 50,
#                         "shotgun": 20
#                     },
#                     "health_damage_effect": True,
#                     "aim_line": False,
#                     "shot_animation": True
#                 }
#             }
#             self.save_settings(file_path)

#     def save_settings(self, file_path="assets/settings/settings.json"):
#         try:
#             os.makedirs(os.path.dirname(file_path), exist_ok=True)
#             with open(file_path, 'w', encoding='utf-8') as f:
#                 json.dump(self.data, f, indent=4, ensure_ascii=False)
#         except Exception as e:
#             print(f"Error saving settings: {e}")

#     def get_initial_level(self):
#         return self.data.get("initial_level", "gomel_streets")

#     def get_player_settings(self):
#         return self.data.get("player", {})

#     def enter(self):
#         print("Entered Settings State")
#         self.message = None
#         self.action_triggered = False
#         self.text_pulse = 0
#         self.nickname_input_active = False
#         self.nickname_temp = self.data["player"]["nickname"]

#     def exit(self):
#         print("Exiting Settings State")
#         if self.nickname_input_active:
#             self.data["player"]["nickname"] = self.nickname_temp
#             self.save_settings()
#         self.nickname_input_active = False

#     def update(self, dt):
#         keys = pygame.key.get_pressed()
#         mouse_pos = pygame.mouse.get_pos()
#         mouse_clicked = pygame.mouse.get_pressed()[0]
        
#         self.text_pulse += dt
#         if self.text_pulse >= 1.0:
#             self.text_pulse = 0

#         if keys[pygame.K_ESCAPE] and not self.action_triggered:
#             self.game.change_state(GameState.MAIN_MENU)
#             self.action_triggered = True
#             if self.nickname_input_active:
#                 self.data["player"]["nickname"] = self.nickname_temp
#                 self.save_settings()
#                 self.nickname_input_active = False

#         if mouse_clicked and not self.action_triggered:
#             # Toggle sound
#             if 200 < mouse_pos[0] < 400 and 200 < mouse_pos[1] < 250:
#                 self.data["sound_enabled"] = not self.data["sound_enabled"]
#                 self.save_settings()
#                 self.action_triggered = True
#             # Toggle health damage effect
#             elif 450 < mouse_pos[0] < 650 and 200 < mouse_pos[1] < 250:
#                 self.data["player"]["health_damage_effect"] = not self.data["player"]["health_damage_effect"]
#                 self.save_settings()
#                 self.action_triggered = True
#             # Toggle aiming line
#             elif 200 < mouse_pos[0] < 400 and 350 < mouse_pos[1] < 400:
#                 self.data["player"]["aim_line"] = not self.data["player"]["aim_line"]
#                 self.save_settings()
#                 self.action_triggered = True
#             # Toggle shot animation
#             elif 450 < mouse_pos[0] < 650 and 350 < mouse_pos[1] < 400:
#                 self.data["player"]["shot_animation"] = not self.data["player"]["shot_animation"]
#                 self.save_settings()
#                 self.action_triggered = True
#             # Toggle avatar
#             elif 200 < mouse_pos[0] < 400 and 500 < mouse_pos[1] < 550:
#                 current_avatar = self.data["player"]["photo"]
#                 avatars = [avatar.value for avatar in AvatarType]
#                 current_idx = avatars.index(current_avatar) if current_avatar in avatars else 0
#                 next_idx = (current_idx + 1) % len(avatars)
#                 self.data["player"]["photo"] = avatars[next_idx]
#                 self.save_settings()
#                 self.action_triggered = True
#             # Toggle nickname input
#             elif 450 < mouse_pos[0] < 650 and 500 < mouse_pos[1] < 550:
#                 self.nickname_input_active = not self.nickname_input_active
#                 if not self.nickname_input_active:
#                     self.data["player"]["nickname"] = self.nickname_temp
#                     self.save_settings()
#                 self.action_triggered = True

#         # Handle nickname input
#         for event in pygame.event.get():
#             if event.type == pygame.KEYDOWN and self.nickname_input_active:
#                 if event.key == pygame.K_RETURN:
#                     self.nickname_input_active = False
#                     self.data["player"]["nickname"] = self.nickname_temp
#                     self.save_settings()
#                     self.action_triggered = True
#                 elif event.key == pygame.K_BACKSPACE:
#                     self.nickname_temp = self.nickname_temp[:-1]
#                 elif event.key == pygame.K_ESCAPE:
#                     self.nickname_input_active = False
#                     self.nickname_temp = self.data["player"]["nickname"]
#                     self.action_triggered = True
#                 elif len(self.nickname_temp) < 20 and event.unicode.isprintable():
#                     self.nickname_temp += event.unicode

#         if not keys[pygame.K_ESCAPE] and not mouse_clicked and not any(event.type == pygame.KEYDOWN for event in pygame.event.get()):
#             self.action_triggered = False

#     def render(self, screen):
#         pulse_alpha = 180 + int(30 * (1 + math.sin(self.text_pulse * math.pi)) / 2)

#         screen.blit(self.background, (0, 0))
        
#         title_text = self.font.render("Settings", True, (255, 255, 255))
#         title_rect = title_text.get_rect(center=(400, 50))
#         title_bg_rect = title_rect.inflate(20, 10)
#         pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), title_bg_rect)
#         screen.blit(title_text, title_rect)

#         level_text = self.font.render(f"Current Level: {self.get_initial_level()}", True, (255, 255, 255))
#         level_rect = level_text.get_rect(center=(400, 100))
#         level_bg_rect = level_rect.inflate(20, 10)
#         pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), level_bg_rect)
#         screen.blit(level_text, level_rect)

#         sound_label = self.font.render("Sound", True, (255, 255, 255))
#         sound_label_rect = sound_label.get_rect(center=(300, 175))
#         sound_label_bg_rect = sound_label_rect.inflate(20, 10)
#         pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), sound_label_bg_rect)
#         screen.blit(sound_label, sound_label_rect)

#         sound_status = self.font.render("ON" if self.data["sound_enabled"] else "OFF", True, (255, 255, 255))
#         sound_status_rect = sound_status.get_rect(center=(300, 225))
#         sound_status_bg_rect = sound_status_rect.inflate(20, 10)
#         pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), sound_status_bg_rect)
#         screen.blit(sound_status, sound_status_rect)

#         health_effect_label = self.font.render("Health Damage Effect", True, (255, 255, 255))
#         health_effect_label_rect = health_effect_label.get_rect(center=(550, 175))
#         health_effect_bg_rect = health_effect_label_rect.inflate(20, 10)
#         pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), health_effect_bg_rect)
#         screen.blit(health_effect_label, health_effect_label_rect)

#         health_effect_status = self.font.render("ON" if self.data["player"]["health_damage_effect"] else "OFF", True, (255, 255, 255))
#         health_effect_status_rect = health_effect_status.get_rect(center=(550, 225))
#         health_effect_status_bg_rect = health_effect_status_rect.inflate(20, 10)
#         pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), health_effect_status_bg_rect)
#         screen.blit(health_effect_status, health_effect_status_rect)

#         aim_line_label = self.font.render("Aiming Line", True, (255, 255, 255))
#         aim_line_label_rect = aim_line_label.get_rect(center=(300, 325))
#         aim_line_bg_rect = aim_line_label_rect.inflate(20, 10)
#         pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), aim_line_bg_rect)
#         screen.blit(aim_line_label, aim_line_label_rect)

#         aim_line_status = self.font.render("ON" if self.data["player"]["aim_line"] else "OFF", True, (255, 255, 255))
#         aim_line_status_rect = aim_line_status.get_rect(center=(300, 375))
#         aim_line_status_bg_rect = aim_line_status_rect.inflate(20, 10)
#         pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), aim_line_status_bg_rect)
#         screen.blit(aim_line_status, aim_line_status_rect)

#         shot_anim_label = self.font.render("Shot Animation", True, (255, 255, 255))
#         shot_anim_label_rect = shot_anim_label.get_rect(center=(550, 325))
#         shot_anim_bg_rect = shot_anim_label_rect.inflate(20, 10)
#         pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), shot_anim_bg_rect)
#         screen.blit(shot_anim_label, shot_anim_label_rect)

#         shot_anim_status = self.font.render("ON" if self.data["player"]["shot_animation"] else "OFF", True, (255, 255, 255))
#         shot_anim_status_rect = shot_anim_status.get_rect(center=(550, 375))
#         shot_anim_status_bg_rect = shot_anim_status_rect.inflate(20, 10)
#         pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), shot_anim_status_bg_rect)
#         screen.blit(shot_anim_status, shot_anim_status_rect)

#         # Render avatar selection
#         avatar_label = self.font.render("Avatar", True, (255, 255, 255))
#         avatar_label_rect = avatar_label.get_rect(center=(300, 475))
#         avatar_label_bg_rect = avatar_label_rect.inflate(20, 10)
#         pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), avatar_label_bg_rect)
#         screen.blit(avatar_label, avatar_label_rect)

#         current_avatar = self.data["player"]["photo"]
#         avatar_name = next((avatar.name for avatar in AvatarType if avatar.value == current_avatar), "Default")
#         avatar_status = self.font.render(avatar_name, True, (255, 255, 255))
#         avatar_status_rect = avatar_status.get_rect(center=(300, 525))
#         avatar_status_bg_rect = avatar_status_rect.inflate(20, 10)
#         pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), avatar_status_bg_rect)
#         screen.blit(avatar_status, avatar_status_rect)

#         # Render nickname input
#         nickname_label = self.font.render("Nickname", True, (255, 255, 255))
#         nickname_label_rect = nickname_label.get_rect(center=(550, 475))
#         nickname_label_bg_rect = nickname_label_rect.inflate(20, 10)
#         pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), nickname_label_bg_rect)
#         screen.blit(nickname_label, nickname_label_rect)

#         nickname_display = self.nickname_temp if self.nickname_input_active else self.data["player"]["nickname"]
#         nickname_text = self.font.render(nickname_display or "Enter nickname", True, (255, 255, 255))
#         nickname_rect = nickname_text.get_rect(center=(550, 525))
#         nickname_bg_rect = nickname_rect.inflate(20, 10)
#         pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), nickname_bg_rect)
#         if self.nickname_input_active:
#             pygame.draw.rect(screen, (255, 255, 255, pulse_alpha), nickname_bg_rect, 2)
#         screen.blit(nickname_text, nickname_rect)

#         return_text = self.font.render("Press ESC to return", True, (255, 255, 255))
#         return_rect = return_text.get_rect(center=(400, 570))
#         return_bg_rect = return_rect.inflate(20, 10)
#         pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), return_bg_rect)
#         screen.blit(return_text, return_rect)