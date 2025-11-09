#!/usr/bin/env python3
"""
Main window for Prakrit Games application.
Provides unified interface with game selection and settings.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QComboBox, QSpinBox,
    QGroupBox, QCheckBox, QMessageBox, QStatusBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from core.db_handler import PrakritDatabase
from core.script_converter import ScriptConverter
from utils.settings import Settings


class MainWindow(QMainWindow):
    """Main application window with game selection and unified interface."""

    def __init__(self):
        super().__init__()

        # Initialize core components
        try:
            self.db = PrakritDatabase()
            self.converter = ScriptConverter()
            self.settings = Settings()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize application:\n{e}")
            sys.exit(1)

        # Game tracking
        self.current_game = None
        self.score = 0
        self.streak = 0
        self.questions_answered = 0

        self.init_ui()
        self.apply_settings()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("प्राकृत शब्द खेल (Prakrit Word Games)")
        self.setGeometry(100, 100, 1024, 768)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Header with title and controls
        header = self.create_header()
        main_layout.addWidget(header)

        # Game selection buttons
        game_selection = self.create_game_selection()
        main_layout.addWidget(game_selection)

        # Stacked widget for different games
        self.game_stack = QStackedWidget()
        main_layout.addWidget(self.game_stack, stretch=1)

        # Add placeholder pages for each game
        self.welcome_page = self.create_welcome_page()
        self.game_stack.addWidget(self.welcome_page)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status_bar()

    def create_header(self):
        """Create header with title and settings controls."""
        header = QWidget()
        layout = QHBoxLayout()
        header.setLayout(layout)

        # Title
        title = QLabel("प्राकृत शब्द खेल")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        layout.addStretch()

        # Script selector
        script_label = QLabel("Script:")
        layout.addWidget(script_label)

        self.script_combo = QComboBox()
        self.script_combo.addItems(['Devanagari', 'IAST', 'ISO 15919', 'Harvard-Kyoto'])
        self.script_combo.setCurrentText('Devanagari')
        self.script_combo.currentTextChanged.connect(self.on_script_changed)
        layout.addWidget(self.script_combo)

        # Difficulty selector
        diff_label = QLabel("Difficulty:")
        layout.addWidget(diff_label)

        self.diff_combo = QComboBox()
        self.diff_combo.addItems(['Easy', 'Medium', 'Hard'])
        self.diff_combo.setCurrentText('Medium')
        self.diff_combo.currentTextChanged.connect(self.on_difficulty_changed)
        layout.addWidget(self.diff_combo)

        # Settings button
        settings_btn = QPushButton("⚙ Settings")
        settings_btn.clicked.connect(self.show_settings_dialog)
        layout.addWidget(settings_btn)

        return header

    def create_game_selection(self):
        """Create game selection buttons."""
        group = QGroupBox("Select Game")
        layout = QHBoxLayout()
        group.setLayout(layout)

        games = [
            ("Game 1:\nForm Quiz", 1),
            ("Game 2:\nWord ID", 2),
            ("Game 3:\nParadigm", 3),
            ("Game 4:\nSpeed Drill", 4),
            ("Game 5:\nMatching", 5),
        ]

        for game_name, game_id in games:
            btn = QPushButton(game_name)
            btn.setMinimumHeight(60)
            btn.clicked.connect(lambda checked, gid=game_id: self.switch_game(gid))
            layout.addWidget(btn)

        return group

    def create_welcome_page(self):
        """Create welcome/home page."""
        page = QWidget()
        layout = QVBoxLayout()
        page.setLayout(layout)

        welcome_text = QLabel(
            "Welcome to Prakrit Word Games!\n\n"
            "Select a game from the buttons above to begin learning Prakrit.\n\n"
            "Features:\n"
            "• 5 different game types to practice verb and noun forms\n"
            "• Multiple script options (Devanagari, IAST, ISO 15919, Harvard-Kyoto)\n"
            "• Adjustable difficulty levels\n"
            "• Progress tracking and statistics\n\n"
            "Choose a game to start!"
        )
        welcome_text.setAlignment(Qt.AlignCenter)
        welcome_text.setWordWrap(True)

        welcome_font = QFont()
        welcome_font.setPointSize(14)
        welcome_text.setFont(welcome_font)

        layout.addStretch()
        layout.addWidget(welcome_text)
        layout.addStretch()

        return page

    def switch_game(self, game_id):
        """Switch to a specific game."""
        # Import game modules dynamically
        if game_id == 1:
            from ui.game1_form_quiz import FormQuizGame
            if not hasattr(self, 'game1_widget'):
                self.game1_widget = FormQuizGame(self.db, self.converter, self.settings, self)
                self.game_stack.addWidget(self.game1_widget)
            self.game_stack.setCurrentWidget(self.game1_widget)
            self.current_game = self.game1_widget

        elif game_id == 2:
            from ui.game2_identification import WordIdentificationGame
            if not hasattr(self, 'game2_widget'):
                self.game2_widget = WordIdentificationGame(self.db, self.converter, self.settings, self)
                self.game_stack.addWidget(self.game2_widget)
            self.game_stack.setCurrentWidget(self.game2_widget)
            self.current_game = self.game2_widget

        elif game_id == 3:
            from ui.game3_paradigm import ParadigmCompletionGame
            if not hasattr(self, 'game3_widget'):
                self.game3_widget = ParadigmCompletionGame(self.db, self.converter, self.settings, self)
                self.game_stack.addWidget(self.game3_widget)
            self.game_stack.setCurrentWidget(self.game3_widget)
            self.current_game = self.game3_widget

        elif game_id == 4:
            from ui.game4_speed_drill import SpeedDrillGame
            if not hasattr(self, 'game4_widget'):
                self.game4_widget = SpeedDrillGame(self.db, self.converter, self.settings, self)
                self.game_stack.addWidget(self.game4_widget)
            self.game_stack.setCurrentWidget(self.game4_widget)
            self.current_game = self.game4_widget

        elif game_id == 5:
            from ui.game5_matching import MatchingGame
            if not hasattr(self, 'game5_widget'):
                self.game5_widget = MatchingGame(self.db, self.converter, self.settings, self)
                self.game_stack.addWidget(self.game5_widget)
            self.game_stack.setCurrentWidget(self.game5_widget)
            self.current_game = self.game5_widget

        # Start the game if it has a start method
        if hasattr(self.current_game, 'start_game'):
            self.current_game.start_game()

    def on_script_changed(self, text):
        """Handle script selection change."""
        script_map = {
            'Devanagari': 'devanagari',
            'IAST': 'iast',
            'ISO 15919': 'iso15919',
            'Harvard-Kyoto': 'hk'
        }
        script = script_map.get(text, 'devanagari')
        self.settings.script_preference = script
        self.settings.save_settings()

        # Update current game if active
        if self.current_game and hasattr(self.current_game, 'on_settings_changed'):
            self.current_game.on_settings_changed()

    def on_difficulty_changed(self, text):
        """Handle difficulty change."""
        self.settings.difficulty = text.lower()
        self.settings.save_settings()

        # Update current game if active
        if self.current_game and hasattr(self.current_game, 'on_settings_changed'):
            self.current_game.on_settings_changed()

    def show_settings_dialog(self):
        """Show settings dialog."""
        # TODO: Implement full settings dialog
        QMessageBox.information(
            self,
            "Settings",
            "Full settings dialog coming soon!\n\n"
            "Use the dropdowns in the header to change script and difficulty."
        )

    def update_status_bar(self):
        """Update status bar with current game info."""
        status_text = f"Score: {self.score} | Streak: {self.streak} | Questions: {self.questions_answered}"
        self.status_bar.showMessage(status_text)

    def update_score(self, points, correct=True):
        """Update score and streak."""
        self.score += points
        self.questions_answered += 1

        if correct:
            self.streak += 1
        else:
            self.streak = 0

        self.update_status_bar()

    def apply_settings(self):
        """Apply settings to UI."""
        # Set font size
        font = self.font()
        font.setPointSize(self.settings.font_size)
        self.setFont(font)

        # Set script combo
        script_display = {
            'devanagari': 'Devanagari',
            'iast': 'IAST',
            'iso15919': 'ISO 15919',
            'hk': 'Harvard-Kyoto'
        }
        self.script_combo.setCurrentText(
            script_display.get(self.settings.script_preference, 'Devanagari')
        )

        # Set difficulty combo
        self.diff_combo.setCurrentText(self.settings.difficulty.capitalize())


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)

    # Set application-wide font with Devanagari support
    app_font = QFont()
    app_font.setFamily("Noto Sans")  # Good Unicode support
    app_font.setPointSize(12)
    app.setFont(app_font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
