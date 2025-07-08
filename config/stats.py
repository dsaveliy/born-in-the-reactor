import json
import os
from datetime import datetime

class Stats:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Stats, cls).__new__(cls)
            cls._instance.load_stats()
        return cls._instance
    
    def load_stats(self, file_path="assets/stats/stats.json"):
        try:
            with open(file_path, 'r') as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading stats: {e}")
            # Default stats
            self.data = {
                "high_scores": []
            }
    
    def save_stats(self, file_path="assets/stats/stats.json"):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving stats: {e}")
    
    def add_score(self, player_name, score):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.data["high_scores"].append({
            "player_name": player_name,
            "score": score,
            "timestamp": timestamp
        })
        # Sort by score (descending) and keep only top 10
        self.data["high_scores"] = sorted(
            self.data["high_scores"],
            key=lambda x: x["score"],
            reverse=True
        )[:10]
        self.save_stats()
    
    def get_high_scores(self):
        return self.data.get("high_scores", [])