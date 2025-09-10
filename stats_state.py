import pygame
import json
import os
from datetime import datetime
from state import State, GameState

class StatsState(State):
    def __init__(self, game):
        super().__init__(game)
        try:
            self.font = pygame.font.Font("assets/fonts/Orbitron-Light.ttf", 36)
        except FileNotFoundError:
            print("Error loading Orbitron-Light font, using default")
            self.font = pygame.font.Font(None, 36)
        
        self.load_stats()
        self.action_triggered = False
        
        try:
            self.background = pygame.image.load("assets/bgs/stats_bg.png").convert()
            self.background = pygame.transform.scale(self.background, (800, 600))
        except FileNotFoundError:
            print("Error loading stats background")
            self.background = pygame.Surface((800, 600))
            self.background.fill((50, 50, 50))

    def load_stats(self, file_path="assets/stats/stats.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading stats: {e}")
            self.data = {
                "high_scores": []
            }

    def save_stats(self, file_path="assets/stats/stats.json"):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving stats: {e}")

    def add_score(self, player_name, score):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.data["high_scores"].append({
            "player_name": player_name,
            "score": score,
            "timestamp": timestamp
        })
        self.data["high_scores"] = sorted(
            self.data["high_scores"],
            key=lambda x: x["score"],
            reverse=True
        )[:10]
        self.save_stats()

    def get_high_scores(self):
        return self.data.get("high_scores", [])

    def enter(self):
        print("Entered Stats State")
        self.action_triggered = False

    def exit(self):
        print("Exiting Stats State")

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE] and not self.action_triggered:
            self.game.change_state(GameState.MAIN_MENU)
            self.action_triggered = True

        if not keys[pygame.K_ESCAPE]:
            self.action_triggered = False

    def render(self, screen):
        screen.blit(self.background, (0, 0))
        high_scores = self.get_high_scores()
        for i, score in enumerate(high_scores):
            text = self.font.render(
                f"{i+1}. {score['player_name']}: {score['score']} ({score['timestamp']})",
                True, (255, 255, 255)
            )
            screen.blit(text, (400 - text.get_width() // 2, 100 + i * 40))
        return_text = self.font.render("Press ESC to return", True, (255, 255, 255))
        screen.blit(return_text, (400 - return_text.get_width() // 2, 540))