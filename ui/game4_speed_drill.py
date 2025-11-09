#!/usr/bin/env python3
"""
Game 4: Speed Drill (द्रुत अभ्यास)
Rapid-fire questions with timer, mixing all types.
"""

import random
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QGroupBox, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont


class SpeedDrillGame(QWidget):
    """Game 4: Speed Drill - Rapid-fire timed questions."""

    def __init__(self, db, converter, settings, parent=None):
        super().__init__(parent)
        self.db = db
        self.converter = converter
        self.settings = settings
        self.parent_window = parent

        self.current_question = None
        self.questions_count = 0
        self.correct_count = 0
        self.time_remaining = 120  # 2 minutes
        self.combo = 0
        self.is_running = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        title = QLabel("द्रुत अभ्यास (Speed Drill)")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Timer and combo display
        timer_layout = QHBoxLayout()

        self.timer_label = QLabel("⏱ 2:00")
        timer_font = QFont()
        timer_font.setPointSize(20)
        timer_font.setBold(True)
        self.timer_label.setFont(timer_font)
        timer_layout.addWidget(self.timer_label)

        timer_layout.addStretch()

        self.combo_label = QLabel("🔥 Combo: x1")
        combo_font = QFont()
        combo_font.setPointSize(16)
        self.combo_label.setFont(combo_font)
        timer_layout.addWidget(self.combo_label)

        layout.addLayout(timer_layout)

        # Progress bar (shows questions answered)
        self.progress = QProgressBar()
        self.progress.setMaximum(50)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Question display
        question_group = QGroupBox("Question")
        question_layout = QVBoxLayout()
        question_group.setLayout(question_layout)

        self.question_label = QLabel()
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setWordWrap(True)
        q_font = QFont()
        q_font.setPointSize(16)
        self.question_label.setFont(q_font)
        question_layout.addWidget(self.question_label)

        layout.addWidget(question_group)

        # Answer input
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Type your answer and press Enter...")
        answer_font = QFont()
        answer_font.setPointSize(16)
        self.answer_input.setFont(answer_font)
        self.answer_input.returnPressed.connect(self.check_and_next)
        layout.addWidget(self.answer_input)

        # Feedback
        self.feedback_label = QLabel()
        self.feedback_label.setAlignment(Qt.AlignCenter)
        feedback_font = QFont()
        feedback_font.setPointSize(12)
        self.feedback_label.setFont(feedback_font)
        layout.addWidget(self.feedback_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.start_button = QPushButton("▶ Start Sprint")
        self.start_button.clicked.connect(self.start_game)
        button_layout.addWidget(self.start_button)

        self.skip_button = QPushButton("⏭ Skip (-5 pts)")
        self.skip_button.clicked.connect(self.skip_question)
        self.skip_button.setEnabled(False)
        button_layout.addWidget(self.skip_button)

        layout.addLayout(button_layout)

        # Stats
        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.stats_label)

        layout.addStretch()

        self.update_stats()

    def start_game(self):
        """Start the speed drill."""
        self.questions_count = 0
        self.correct_count = 0
        self.time_remaining = 120
        self.combo = 1
        self.is_running = True

        self.start_button.setEnabled(False)
        self.skip_button.setEnabled(True)
        self.answer_input.setEnabled(True)
        self.progress.setValue(0)

        self.timer.start(1000)  # Update every second
        self.next_question()

    def update_timer(self):
        """Update the countdown timer."""
        if self.time_remaining > 0:
            self.time_remaining -= 1
            minutes = self.time_remaining // 60
            seconds = self.time_remaining % 60
            self.timer_label.setText(f"⏱ {minutes}:{seconds:02d}")

            # Change color as time runs out
            if self.time_remaining <= 10:
                self.timer_label.setStyleSheet("color: red; font-weight: bold;")
            elif self.time_remaining <= 30:
                self.timer_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.end_game()

    def next_question(self):
        """Generate next question."""
        if not self.is_running:
            return

        self.feedback_label.clear()
        self.answer_input.clear()

        script = self.settings.script_preference
        term_script = self.settings.grammar_terminology

        # Randomly choose verb or noun
        if random.choice([True, False]):
            data = self.db.get_random_verb_form(
                difficulty=self.settings.difficulty,
                script=script
            )
            if data:
                question = (
                    f"{data['root']} - "
                    f"{self.converter.convert_term(data['tense'], term_script)}, "
                    f"{self.converter.convert_term(data['person'], term_script)}, "
                    f"{self.converter.convert_term(data['number'], term_script)}"
                )
                self.current_question = data
        else:
            data = self.db.get_random_noun_form(
                difficulty=self.settings.difficulty,
                script=script
            )
            if data:
                question = (
                    f"{data['root']} - "
                    f"{self.converter.convert_term(data['case'], term_script)}, "
                    f"{self.converter.convert_term(data['number'], term_script)}"
                )
                self.current_question = data

        if self.current_question:
            self.question_label.setText(f"Question {self.questions_count + 1}/50:\n{question}")
            self.answer_input.setFocus()

    def check_and_next(self):
        """Check answer and move to next question."""
        if not self.current_question or not self.is_running:
            return

        user_answer = self.answer_input.text().strip()
        correct_answer = self.current_question['form']

        self.questions_count += 1
        self.progress.setValue(self.questions_count)

        if user_answer == correct_answer:
            self.correct_count += 1
            self.combo += 1
            self.feedback_label.setText("✓ Correct!")
            self.feedback_label.setStyleSheet("color: green;")

            # Update score with combo multiplier
            points = 5 * self.combo
            if self.parent_window:
                self.parent_window.update_score(points, correct=True)
        else:
            self.combo = 1
            self.feedback_label.setText(f"✗ Wrong! Answer: {correct_answer}")
            self.feedback_label.setStyleSheet("color: red;")

            if self.parent_window:
                self.parent_window.update_score(0, correct=False)

        self.combo_label.setText(f"🔥 Combo: x{self.combo}")
        self.update_stats()

        # Check if reached 50 questions
        if self.questions_count >= 50:
            self.end_game()
        else:
            self.next_question()

    def skip_question(self):
        """Skip current question with penalty."""
        if self.parent_window:
            self.parent_window.update_score(-5, correct=False)

        self.combo = 1
        self.combo_label.setText(f"🔥 Combo: x{self.combo}")
        self.next_question()

    def end_game(self):
        """End the game and show results."""
        self.is_running = False
        self.timer.stop()
        self.answer_input.setEnabled(False)
        self.skip_button.setEnabled(False)
        self.start_button.setEnabled(True)

        accuracy = (self.correct_count / self.questions_count * 100) if self.questions_count > 0 else 0

        self.question_label.setText(
            f"🏁 Game Over!\n\n"
            f"Questions answered: {self.questions_count}\n"
            f"Correct: {self.correct_count}\n"
            f"Accuracy: {accuracy:.1f}%\n\n"
            f"Click 'Start Sprint' to play again!"
        )

    def update_stats(self):
        """Update statistics display."""
        if self.questions_count > 0:
            accuracy = (self.correct_count / self.questions_count) * 100
            self.stats_label.setText(
                f"Answered: {self.questions_count} | Correct: {self.correct_count} | Accuracy: {accuracy:.1f}%"
            )
        else:
            self.stats_label.setText("Click 'Start Sprint' to begin!")

    def on_settings_changed(self):
        """Called when settings are changed."""
        pass  # Don't change mid-game
