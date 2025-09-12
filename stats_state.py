import pygame
import sqlite3
import json
import os
import math
from datetime import datetime
from state import State, GameState

class StatsState(State):
    def __init__(self, game):
        super().__init__(game)
        try:
            self.font = pygame.font.Font("assets/fonts/Orbitron-Bold.ttf", 28)
            self.small_font = pygame.font.Font("assets/fonts/Orbitron-Bold.ttf", 20)
        except FileNotFoundError:
            print("Error loading Orbitron-Light font, using default")
            self.font = pygame.font.Font(None, 28)
            self.small_font = pygame.font.Font(None, 20)
        
        self.init_database()
        self.action_triggered = False
        self.text_pulse = 0
        
        try:
            self.background = pygame.image.load("assets/bgs/stats_bg.png").convert()
            self.background = pygame.transform.scale(self.background, (800, 600))
        except FileNotFoundError:
            print("Error loading stats background")
            self.background = pygame.Surface((800, 600))
            self.background.fill((50, 50, 50))

    def init_database(self):
        db_path = "assets/stats/stats.db"
        try:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS high_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            self.conn.commit()
            
            # Check if the table is empty
            self.cursor.execute("SELECT COUNT(*) FROM high_scores")
            count = self.cursor.fetchone()[0]
            
            # Add 10 dummy scores if the table is empty
            if count == 0:
                dummy_scores = [
                    ("Player1", 1000, "06-09-25 10:00:00"),
                    ("Player2", 900, "03-09-25 10:15:00"),
                    ("Player3", 800, "04-09-25 10:30:00"),
                    ("Player4", 700, "01-09-25 10:45:00"),
                    ("Player5", 600, "07-09-25 11:00:00"),
                    ("Player6", 500, "06-09-25 11:15:00"),
                    ("Player7", 400, "03-09-25 11:30:00"),
                    ("Player8", 300, "04-09-25 11:45:00"),
                    ("Player9", 200, "06-09-25 12:00:00"),
                    ("Player10", 100, "06-09-25 12:15:00")
                ]
                self.cursor.executemany("""
                    INSERT INTO high_scores (player_name, score, timestamp)
                    VALUES (?, ?, ?)
                """, dummy_scores)
                self.conn.commit()
                print("Added 10 dummy scores to high_scores table")
                
        except Exception as e:
            print(f"Error initializing database: {e}")
            self.conn = None
            self.cursor = None

    def add_score(self, player_name, score):
        if not self.conn:
            print("Database not available, cannot add score")
            return
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        try:
            self.cursor.execute("""
                INSERT INTO high_scores (player_name, score, timestamp)
                VALUES (?, ?, ?)
            """, (player_name, score, timestamp))
            self.conn.commit()
            self.cursor.execute("""
                DELETE FROM high_scores
                WHERE id NOT IN (
                    SELECT id FROM high_scores
                    ORDER BY score DESC
                    LIMIT 10
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding score: {e}")

    def get_high_scores(self):
        if not self.conn:
            print("Database not available, returning empty scores")
            return []
        try:
            self.cursor.execute("""
                SELECT player_name, score, timestamp
                FROM high_scores
                ORDER BY score DESC
                LIMIT 10
            """)
            return [{"player_name": row[0], "score": row[1], "timestamp": row[2]} for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error fetching scores: {e}")
            return []

    def enter(self):
        print("Entered Stats State")
        self.action_triggered = False
        self.text_pulse = 0
        if not self.conn:
            self.init_database()

    def exit(self):
        print("Exiting Stats State")

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.text_pulse += dt
        if self.text_pulse >= 1.0:
            self.text_pulse = 0

        if keys[pygame.K_ESCAPE] and not self.action_triggered:
            self.game.change_state(GameState.MAIN_MENU)
            self.action_triggered = True

        if not keys[pygame.K_ESCAPE]:
            self.action_triggered = False

    def render(self, screen):
        pulse_alpha = 180 + int(30 * (1 + math.sin(self.text_pulse * math.pi)) / 2)
        screen.blit(self.background, (0, 0))
        high_scores = self.get_high_scores()
        
        if not high_scores:
            no_scores_text = self.font.render("No scores yet", True, (255, 255, 255))
            no_scores_rect = no_scores_text.get_rect(center=(400, 200))
            screen.blit(no_scores_text, no_scores_rect)
        else:
            for i, score in enumerate(high_scores):
                y_pos = 165 + i * 45
                text = self.font.render(
                    f"{i+1}. {score['player_name']}: {score['score']} ({score['timestamp'][:16]})",
                    True, (255, 255, 255)
                )
                text_rect = text.get_rect(center=(400, y_pos))
                screen.blit(text, text_rect)
        
        return_text = self.small_font.render("Press ESC to return", True, (255, 255, 255))
        return_rect = return_text.get_rect(center=(400, 577))
        return_bg_rect = return_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, pulse_alpha), return_bg_rect)
        screen.blit(return_text, return_rect)