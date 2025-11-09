#!/usr:bin/env python3
"""
Game 5: Matching Game (मिलान खेल)
Match words with their forms, or forms with grammatical descriptions.
"""

import random
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QMessageBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class MatchingGame(QWidget):
    """Game 5: Matching Game - Match forms with descriptions or roots."""

    def __init__(self, db, converter, settings, parent=None):
        super().__init__(parent)
        self.db = db
        self.converter = converter
        self.settings = settings
        self.parent_window = parent

        self.left_items = []
        self.right_items = []
        self.matches = {}  # Maps left index to right index
        self.user_matches = {}
        self.questions_count = 0
        self.correct_count = 0

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        title = QLabel("मिलान खेल (Matching Game)")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Match the inflected forms with their grammatical descriptions.\n"
            "Click an item on the left, then click its match on the right."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        # Matching area
        matching_layout = QHBoxLayout()

        # Left column
        left_group = QGroupBox("Inflected Forms")
        left_layout = QVBoxLayout()
        left_group.setLayout(left_layout)

        self.left_list = QListWidget()
        self.left_list.itemClicked.connect(self.on_left_clicked)
        left_layout.addWidget(self.left_list)

        matching_layout.addWidget(left_group)

        # Right column
        right_group = QGroupBox("Grammatical Descriptions")
        right_layout = QVBoxLayout()
        right_group.setLayout(right_layout)

        self.right_list = QListWidget()
        self.right_list.itemClicked.connect(self.on_right_clicked)
        right_layout.addWidget(self.right_list)

        matching_layout.addWidget(right_group)

        layout.addLayout(matching_layout)

        # Feedback
        self.feedback_label = QLabel()
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.feedback_label.setWordWrap(True)
        feedback_font = QFont()
        feedback_font.setPointSize(14)
        self.feedback_label.setFont(feedback_font)
        layout.addWidget(self.feedback_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.clear_button = QPushButton("Clear Matches")
        self.clear_button.clicked.connect(self.clear_matches)
        button_layout.addWidget(self.clear_button)

        self.check_button = QPushButton("✓ Check Matches")
        self.check_button.clicked.connect(self.check_matches)
        button_layout.addWidget(self.check_button)

        self.next_button = QPushButton("→ New Set")
        self.next_button.clicked.connect(self.next_set)
        button_layout.addWidget(self.next_button)

        layout.addLayout(button_layout)

        # Stats
        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.stats_label)

        self.update_stats()

        # Track selected items
        self.selected_left = None
        self.selected_right = None

    def start_game(self):
        """Start or restart the game."""
        self.questions_count = 0
        self.correct_count = 0
        self.update_stats()
        self.next_set()

    def next_set(self):
        """Generate a new set of items to match."""
        self.feedback_label.clear()
        self.user_matches = {}
        self.selected_left = None
        self.selected_right = None

        script = self.settings.script_preference
        term_script = self.settings.grammar_terminology

        # Get 4-5 random word forms
        num_items = random.randint(4, 5)
        forms = []

        for _ in range(num_items):
            if random.choice([True, False]):
                data = self.db.get_random_noun_form(
                    difficulty=self.settings.difficulty,
                    script=script
                )
                if data:
                    desc = (
                        f"{data['root']} - "
                        f"{self.converter.convert_term(data['case'], term_script)}, "
                        f"{self.converter.convert_term(data['number'], term_script)}"
                    )
                    forms.append((data['form'], desc))
            else:
                data = self.db.get_random_verb_form(
                    difficulty=self.settings.difficulty,
                    script=script
                )
                if data:
                    desc = (
                        f"{data['root']} - "
                        f"{self.converter.convert_term(data['tense'], term_script)}, "
                        f"{self.converter.convert_term(data['person'], term_script)}, "
                        f"{self.converter.convert_term(data['number'], term_script)}"
                    )
                    forms.append((data['form'], desc))

        if len(forms) < 3:
            QMessageBox.warning(self, "No Data", "Not enough data available!")
            return

        # Separate left and right items
        self.left_items = [form for form, _ in forms]
        self.right_items = [desc for _, desc in forms]

        # Shuffle right items
        right_shuffled = self.right_items.copy()
        random.shuffle(right_shuffled)

        # Create correct matches mapping
        self.matches = {}
        for i, left_form in enumerate(self.left_items):
            correct_desc = self.right_items[i]
            right_index = right_shuffled.index(correct_desc)
            self.matches[i] = right_index

        # Update right items to shuffled version
        self.right_items = right_shuffled

        # Populate lists
        self.left_list.clear()
        self.right_list.clear()

        for item in self.left_items:
            self.left_list.addItem(item)

        for item in self.right_items:
            self.right_list.addItem(item)

    def on_left_clicked(self, item):
        """Handle left item click."""
        self.selected_left = self.left_list.row(item)
        self.highlight_selections()
        self.try_match()

    def on_right_clicked(self, item):
        """Handle right item click."""
        self.selected_right = self.right_list.row(item)
        self.highlight_selections()
        self.try_match()

    def try_match(self):
        """Try to create a match if both sides are selected."""
        if self.selected_left is not None and self.selected_right is not None:
            # Create match
            self.user_matches[self.selected_left] = self.selected_right

            # Visual feedback
            self.left_list.item(self.selected_left).setBackground(QColor(200, 200, 255))
            self.right_list.item(self.selected_right).setBackground(QColor(200, 200, 255))

            # Clear selections
            self.selected_left = None
            self.selected_right = None
            self.highlight_selections()

    def highlight_selections(self):
        """Highlight currently selected items."""
        # Clear all highlights first (except matched ones)
        for i in range(self.left_list.count()):
            if i not in self.user_matches:
                self.left_list.item(i).setBackground(QColor(255, 255, 255))

        for i in range(self.right_list.count()):
            if i not in self.user_matches.values():
                self.right_list.item(i).setBackground(QColor(255, 255, 255))

        # Highlight selected
        if self.selected_left is not None:
            self.left_list.item(self.selected_left).setBackground(QColor(255, 255, 200))

        if self.selected_right is not None:
            self.right_list.item(self.selected_right).setBackground(QColor(255, 255, 200))

    def clear_matches(self):
        """Clear all matches."""
        self.user_matches = {}
        self.selected_left = None
        self.selected_right = None

        for i in range(self.left_list.count()):
            self.left_list.item(i).setBackground(QColor(255, 255, 255))

        for i in range(self.right_list.count()):
            self.right_list.item(i).setBackground(QColor(255, 255, 255))

    def check_matches(self):
        """Check if all matches are correct."""
        if len(self.user_matches) < len(self.left_items):
            QMessageBox.warning(
                self,
                "Incomplete",
                f"You've only matched {len(self.user_matches)}/{len(self.left_items)} items.\nMatch all items before checking!"
            )
            return

        correct = 0
        total = len(self.matches)

        for left_idx, right_idx in self.user_matches.items():
            if self.matches.get(left_idx) == right_idx:
                correct += 1
                self.left_list.item(left_idx).setBackground(QColor(200, 255, 200))
                self.right_list.item(right_idx).setBackground(QColor(200, 255, 200))
            else:
                self.left_list.item(left_idx).setBackground(QColor(255, 200, 200))
                self.right_list.item(right_idx).setBackground(QColor(255, 200, 200))

        self.questions_count += 1

        accuracy = (correct / total) * 100

        if correct == total:
            self.correct_count += 1
            self.feedback_label.setText(f"✓ Perfect! All {total} matches correct!")
            self.feedback_label.setStyleSheet("color: green; font-weight: bold;")
            if self.parent_window:
                self.parent_window.update_score(15, correct=True)
        else:
            self.feedback_label.setText(f"Matched {correct}/{total} correctly ({accuracy:.1f}%)")
            self.feedback_label.setStyleSheet("color: orange; font-weight: bold;")
            if self.parent_window:
                self.parent_window.update_score(5, correct=False)

        self.update_stats()

    def update_stats(self):
        """Update statistics display."""
        if self.questions_count > 0:
            accuracy = (self.correct_count / self.questions_count) * 100
            self.stats_label.setText(
                f"Sets: {self.questions_count} | Perfect: {self.correct_count} | Accuracy: {accuracy:.1f}%"
            )
        else:
            self.stats_label.setText("No sets completed yet. Click 'New Set' to start!")

    def on_settings_changed(self):
        """Called when settings are changed."""
        if self.left_items:
            self.next_set()
