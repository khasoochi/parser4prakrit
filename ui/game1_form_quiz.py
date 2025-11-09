#!/usr/bin/env python3
"""
Game 1: Form Quiz (रूप प्रश्नोत्तरी)
Given a root word and grammatical specifications, type the correct inflected form.
"""

import random
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QGroupBox, QMessageBox, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class FormQuizGame(QWidget):
    """Game 1: Form Quiz - Test knowledge of word forms."""

    def __init__(self, db, converter, settings, parent=None):
        super().__init__(parent)
        self.db = db
        self.converter = converter
        self.settings = settings
        self.parent_window = parent

        self.current_question = None
        self.questions_count = 0
        self.correct_count = 0

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        title = QLabel("रूप प्रश्नोत्तरी (Form Quiz)")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Type the correct inflected form based on the root word and grammatical specifications."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        # Word type selection
        word_type_group = QGroupBox("Word Type")
        word_type_layout = QHBoxLayout()
        word_type_group.setLayout(word_type_layout)

        self.word_type_group = QButtonGroup()
        self.verb_radio = QRadioButton("Verbs")
        self.noun_radio = QRadioButton("Nouns")
        self.both_radio = QRadioButton("Both")
        self.both_radio.setChecked(True)

        self.word_type_group.addButton(self.verb_radio, 1)
        self.word_type_group.addButton(self.noun_radio, 2)
        self.word_type_group.addButton(self.both_radio, 3)

        word_type_layout.addWidget(self.verb_radio)
        word_type_layout.addWidget(self.noun_radio)
        word_type_layout.addWidget(self.both_radio)

        layout.addWidget(word_type_group)

        # Question display area
        question_group = QGroupBox("Question")
        question_layout = QVBoxLayout()
        question_group.setLayout(question_layout)

        self.root_label = QLabel()
        self.root_label.setAlignment(Qt.AlignCenter)
        root_font = QFont()
        root_font.setPointSize(20)
        self.root_label.setFont(root_font)
        question_layout.addWidget(self.root_label)

        self.grammar_label = QLabel()
        self.grammar_label.setAlignment(Qt.AlignCenter)
        self.grammar_label.setWordWrap(True)
        grammar_font = QFont()
        grammar_font.setPointSize(14)
        self.grammar_label.setFont(grammar_font)
        question_layout.addWidget(self.grammar_label)

        layout.addWidget(question_group)

        # Answer input
        answer_group = QGroupBox("Your Answer")
        answer_layout = QVBoxLayout()
        answer_group.setLayout(answer_layout)

        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Type your answer here...")
        answer_font = QFont()
        answer_font.setPointSize(16)
        self.answer_input.setFont(answer_font)
        self.answer_input.returnPressed.connect(self.check_answer)
        answer_layout.addWidget(self.answer_input)

        layout.addWidget(answer_group)

        # Feedback area
        self.feedback_label = QLabel()
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.feedback_label.setWordWrap(True)
        feedback_font = QFont()
        feedback_font.setPointSize(14)
        self.feedback_label.setFont(feedback_font)
        layout.addWidget(self.feedback_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.hint_button = QPushButton("💡 Hint")
        self.hint_button.clicked.connect(self.show_hint)
        button_layout.addWidget(self.hint_button)

        self.check_button = QPushButton("✓ Check Answer")
        self.check_button.clicked.connect(self.check_answer)
        self.check_button.setDefault(True)
        button_layout.addWidget(self.check_button)

        self.next_button = QPushButton("→ Next Question")
        self.next_button.clicked.connect(self.next_question)
        self.next_button.setEnabled(False)
        button_layout.addWidget(self.next_button)

        layout.addLayout(button_layout)

        # Stats
        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.stats_label)

        self.update_stats()

    def start_game(self):
        """Start or restart the game."""
        self.questions_count = 0
        self.correct_count = 0
        self.update_stats()
        self.next_question()

    def next_question(self):
        """Generate a new question."""
        self.feedback_label.clear()
        self.answer_input.clear()
        self.answer_input.setEnabled(True)
        self.check_button.setEnabled(True)
        self.next_button.setEnabled(False)

        # Determine word type
        word_type_id = self.word_type_group.checkedId()

        if word_type_id == 1:  # Verbs only
            self.generate_verb_question()
        elif word_type_id == 2:  # Nouns only
            self.generate_noun_question()
        else:  # Both
            if random.choice([True, False]):
                self.generate_verb_question()
            else:
                self.generate_noun_question()

    def generate_verb_question(self):
        """Generate a verb form question."""
        script = self.settings.script_preference
        term_script = self.settings.grammar_terminology

        # Get random verb form
        verb_data = self.db.get_random_verb_form(
            difficulty=self.settings.difficulty,
            script=script
        )

        if not verb_data:
            QMessageBox.warning(self, "No Data", "No verb forms available!")
            return

        self.current_question = verb_data
        self.current_question['type'] = 'verb'

        # Display question
        self.root_label.setText(f"{self.converter.convert_term('root', term_script)}: {verb_data['root']} ({verb_data['meaning']})")

        grammar_parts = [
            f"{self.converter.convert_term('tense', term_script)}: {self.converter.convert_term(verb_data['tense'], term_script)}",
            f"{self.converter.convert_term('person', term_script)}: {self.converter.convert_term(verb_data['person'], term_script)}",
            f"{self.converter.convert_term('number', term_script)}: {self.converter.convert_term(verb_data['number'], term_script)}"
        ]

        self.grammar_label.setText(" | ".join(grammar_parts))

    def generate_noun_question(self):
        """Generate a noun form question."""
        script = self.settings.script_preference
        term_script = self.settings.grammar_terminology

        # Get random noun form
        noun_data = self.db.get_random_noun_form(
            difficulty=self.settings.difficulty,
            script=script
        )

        if not noun_data:
            QMessageBox.warning(self, "No Data", "No noun forms available!")
            return

        self.current_question = noun_data
        self.current_question['type'] = 'noun'

        # Display question
        self.root_label.setText(f"{self.converter.convert_term('root', term_script)}: {noun_data['root']} ({noun_data['meaning']})")

        grammar_parts = [
            f"{self.converter.convert_term('case', term_script)}: {self.converter.convert_term(noun_data['case'], term_script)}",
            f"{self.converter.convert_term('number', term_script)}: {self.converter.convert_term(noun_data['number'], term_script)}",
            f"{self.converter.convert_term('gender', term_script)}: {self.converter.convert_term(noun_data['gender'], term_script)}"
        ]

        self.grammar_label.setText(" | ".join(grammar_parts))

    def check_answer(self):
        """Check if the answer is correct."""
        if not self.current_question:
            return

        user_answer = self.answer_input.text().strip()
        correct_answer = self.current_question['form']

        if not user_answer:
            QMessageBox.warning(self, "Empty Answer", "Please type your answer first!")
            return

        self.questions_count += 1

        # Check if answer is correct
        if user_answer == correct_answer:
            self.correct_count += 1
            self.feedback_label.setText(f"✓ Correct! The answer is: {correct_answer}")
            self.feedback_label.setStyleSheet("color: green; font-weight: bold;")

            # Update parent score
            if self.parent_window:
                self.parent_window.update_score(10, correct=True)
        else:
            self.feedback_label.setText(f"✗ Incorrect. The correct answer is: {correct_answer}\nYou wrote: {user_answer}")
            self.feedback_label.setStyleSheet("color: red; font-weight: bold;")

            # Update parent score
            if self.parent_window:
                self.parent_window.update_score(0, correct=False)

        self.answer_input.setEnabled(False)
        self.check_button.setEnabled(False)
        self.next_button.setEnabled(True)
        self.update_stats()

    def show_hint(self):
        """Show a hint for the current question."""
        if not self.current_question or not self.settings.hints_enabled:
            return

        correct_answer = self.current_question['form']

        # Show first half of the answer
        hint_length = len(correct_answer) // 2
        hint = correct_answer[:hint_length] + "..."

        QMessageBox.information(
            self,
            "Hint",
            f"The answer starts with: {hint}\n\nLength: {len(correct_answer)} characters"
        )

    def update_stats(self):
        """Update statistics display."""
        if self.questions_count > 0:
            accuracy = (self.correct_count / self.questions_count) * 100
            self.stats_label.setText(
                f"Questions: {self.questions_count} | Correct: {self.correct_count} | Accuracy: {accuracy:.1f}%"
            )
        else:
            self.stats_label.setText("No questions answered yet. Click 'Next Question' to start!")

    def on_settings_changed(self):
        """Called when settings are changed."""
        # Regenerate current question with new settings
        if self.current_question:
            # Save current state
            saved_state = (self.questions_count, self.correct_count)

            # Regenerate question
            if self.current_question['type'] == 'verb':
                self.generate_verb_question()
            else:
                self.generate_noun_question()

            # Restore state
            self.questions_count, self.correct_count = saved_state
            self.update_stats()
