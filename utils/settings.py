#!/usr/bin/env python3
"""
Settings management for Prakrit Games application.
Handles user preferences for scripts, display, gameplay, etc.
"""

import json
import os
from typing import Dict, Any


class Settings:
    """Manages application settings and user preferences."""

    DEFAULT_SETTINGS = {
        # Script preferences
        'script_preference': 'devanagari',  # Default script for Prakrit text
        'grammar_terminology': 'devanagari',  # Script for grammatical terms

        # Display settings
        'font_size': 16,  # Font size in points (12-24 range)
        'theme': 'light',  # 'light' or 'dark'

        # Audio settings
        'sound_enabled': True,
        'pronunciation_enabled': False,  # If pronunciation audio is available

        # Gameplay settings
        'difficulty': 'medium',  # 'easy', 'medium', 'hard'
        'timed_mode': False,  # Whether questions are timed
        'hints_enabled': True,  # Whether hints are available
        'timer_seconds': 10,  # Time per question in timed mode

        # User progress
        'current_user': 'default',
        'last_game': None,  # Last played game

        # Window settings
        'window_width': 1024,
        'window_height': 768,
        'window_maximized': False,
    }

    VALID_SCRIPTS = ['devanagari', 'iast', 'iso15919', 'hk']
    VALID_TERMINOLOGY = ['devanagari', 'roman', 'english']
    VALID_DIFFICULTIES = ['easy', 'medium', 'hard']
    VALID_THEMES = ['light', 'dark']

    def __init__(self, settings_file=None):
        """
        Initialize settings manager.

        Args:
            settings_file: Path to settings JSON file (optional)
        """
        if settings_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, 'data')
            os.makedirs(data_dir, exist_ok=True)
            settings_file = os.path.join(data_dir, 'settings.json')

        self.settings_file = settings_file
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load_settings()

    def load_settings(self):
        """Load settings from file. Create file with defaults if it doesn't exist."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Update settings with loaded values, keeping defaults for missing keys
                    self.settings.update(loaded)
            except Exception as e:
                print(f"Error loading settings: {e}. Using defaults.")
        else:
            # Save default settings
            self.save_settings()

    def save_settings(self):
        """Save current settings to file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")

    # Getters
    def get(self, key: str, default=None) -> Any:
        """Get a setting value."""
        return self.settings.get(key, default)

    def get_all(self) -> Dict:
        """Get all settings as a dictionary."""
        return self.settings.copy()

    # Setters with validation
    def set(self, key: str, value: Any):
        """Set a setting value."""
        # Validate certain settings
        if key == 'script_preference' and value not in self.VALID_SCRIPTS:
            raise ValueError(f"Invalid script: {value}. Must be one of {self.VALID_SCRIPTS}")

        if key == 'grammar_terminology' and value not in self.VALID_TERMINOLOGY:
            raise ValueError(f"Invalid terminology: {value}. Must be one of {self.VALID_TERMINOLOGY}")

        if key == 'difficulty' and value not in self.VALID_DIFFICULTIES:
            raise ValueError(f"Invalid difficulty: {value}. Must be one of {self.VALID_DIFFICULTIES}")

        if key == 'theme' and value not in self.VALID_THEMES:
            raise ValueError(f"Invalid theme: {value}. Must be one of {self.VALID_THEMES}")

        if key == 'font_size' and not (12 <= value <= 24):
            raise ValueError(f"Font size must be between 12 and 24, got {value}")

        self.settings[key] = value

    def update(self, settings_dict: Dict):
        """Update multiple settings at once."""
        for key, value in settings_dict.items():
            self.set(key, value)

    # Convenience properties
    @property
    def script_preference(self) -> str:
        """Get current script preference."""
        return self.settings['script_preference']

    @script_preference.setter
    def script_preference(self, value: str):
        """Set script preference with validation."""
        self.set('script_preference', value)

    @property
    def grammar_terminology(self) -> str:
        """Get grammatical terminology preference."""
        return self.settings['grammar_terminology']

    @grammar_terminology.setter
    def grammar_terminology(self, value: str):
        """Set grammatical terminology preference."""
        self.set('grammar_terminology', value)

    @property
    def font_size(self) -> int:
        """Get font size."""
        return self.settings['font_size']

    @font_size.setter
    def font_size(self, value: int):
        """Set font size."""
        self.set('font_size', value)

    @property
    def difficulty(self) -> str:
        """Get difficulty level."""
        return self.settings['difficulty']

    @difficulty.setter
    def difficulty(self, value: str):
        """Set difficulty level."""
        self.set('difficulty', value)

    @property
    def theme(self) -> str:
        """Get theme."""
        return self.settings['theme']

    @theme.setter
    def theme(self, value: str):
        """Set theme."""
        self.set('theme', value)

    @property
    def sound_enabled(self) -> bool:
        """Check if sound is enabled."""
        return self.settings['sound_enabled']

    @sound_enabled.setter
    def sound_enabled(self, value: bool):
        """Enable/disable sound."""
        self.settings['sound_enabled'] = value

    @property
    def hints_enabled(self) -> bool:
        """Check if hints are enabled."""
        return self.settings['hints_enabled']

    @hints_enabled.setter
    def hints_enabled(self, value: bool):
        """Enable/disable hints."""
        self.settings['hints_enabled'] = value

    @property
    def timed_mode(self) -> bool:
        """Check if timed mode is enabled."""
        return self.settings['timed_mode']

    @timed_mode.setter
    def timed_mode(self, value: bool):
        """Enable/disable timed mode."""
        self.settings['timed_mode'] = value

    def reset_to_defaults(self):
        """Reset all settings to default values."""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save_settings()


# Test if run directly
if __name__ == '__main__':
    print("Testing Settings Manager:")
    print("="*60)

    # Create settings instance
    settings = Settings()

    print("\n1. Default settings:")
    print(f"  Script preference: {settings.script_preference}")
    print(f"  Grammar terminology: {settings.grammar_terminology}")
    print(f"  Font size: {settings.font_size}")
    print(f"  Difficulty: {settings.difficulty}")

    print("\n2. Changing settings:")
    settings.script_preference = 'iast'
    settings.font_size = 18
    settings.difficulty = 'hard'
    settings.save_settings()
    print(f"  Script preference changed to: {settings.script_preference}")
    print(f"  Font size changed to: {settings.font_size}")
    print(f"  Difficulty changed to: {settings.difficulty}")

    print("\n3. Reloading settings:")
    settings2 = Settings()
    print(f"  Script preference (reloaded): {settings2.script_preference}")
    print(f"  Font size (reloaded): {settings2.font_size}")
    print(f"  Difficulty (reloaded): {settings2.difficulty}")

    print("\n4. Resetting to defaults:")
    settings2.reset_to_defaults()
    print(f"  Script preference (after reset): {settings2.script_preference}")
    print(f"  Font size (after reset): {settings2.font_size}")

    print("\n5. Validation test:")
    try:
        settings.script_preference = 'invalid_script'
    except ValueError as e:
        print(f"  Caught expected error: {e}")

    print("\n" + "="*60)
    print("Settings manager tests completed!")
