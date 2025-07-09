import json
import os

class Settings:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance.load_settings()
        return cls._instance
    
    def load_settings(self, file_path="assets/settings/settings.json"):
        try:
            with open(file_path, 'r') as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading settings: {e}")
            # Значения по умолчанию
            self.data = {
                "initial_level": "gomel_streets",
                "player": {
                    "initial_health": 100,
                    "initial_ammo": 30
                }
            }
    
    def get_initial_level(self):
        return self.data.get("initial_level", "intro")
    
    def get_player_settings(self):
        return self.data.get("player", {})
    
    def save_settings(self, file_path="assets/settings/settings.json"):
        try:
            with open(file_path, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")