import pygame
import sqlite3
import json
import os
from datetime import datetime
from state import State, GameState

class StatsState(State):
    def __init__(self, game):
        super().__init__(game)
        try:
            self.font = pygame.font.Font("assets/fonts/Orbitron-Bold.ttf", 36)
        except FileNotFoundError:
            print("Error loading Orbitron-Light font, using default")
            self.font = pygame.font.Font(None, 36)
        
        self.init_database()
        self.action_triggered = False
        
        try:
            self.background = pygame.image.load("assets/bgs/stats_bg.png").convert()
            self.background = pygame.transform.scale(self.background, (800, 600))
        except FileNotFoundError:
            print("Error loading stats background")
            self.background = pygame.Surface((800, 600))
            self.background.fill((50, 50, 50))

    def init_database(self):
        # Initialize SQLite database
        db_path = "assets/stats/stats.db"
        try:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            
            # Create table if it doesn't exist
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS high_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            self.conn.commit()
        except Exception as e:
            print(f"Error initializing database: {e}")
            self.conn = None
            self.cursor = None


    def add_score(self, player_name, score):
        if not self.conn:
            print("Database not available, cannot add score")
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.cursor.execute("""
                INSERT INTO high_scores (player_name, score, timestamp)
                VALUES (?, ?, ?)
            """, (player_name, score, timestamp))
            self.conn.commit()
            # Keep only top 10 scores
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

    def exit(self):
        print("Exiting Stats State")
        if self.conn:
            self.conn.close()

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