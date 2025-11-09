#!/usr/bin/env python3
"""
Game 2: Word Identification (शब्द पहचान)
Given an inflected form, identify the root and grammatical features.
"""

import random
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QMessageBox, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class WordIdentificationGame(QWidget):
    """Game 2: Word Identification - Identify root and grammatical features from inflected form."""

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
        title = QLabel("शब्द पहचान (Word Identification)")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Identify the root word and grammatical features of the given inflected form."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        # Inflected form display
        form_group = QGroupBox("Identify this form")
        form_layout = QVBoxLayout()
        form_group.setLayout(form_layout)

        self.form_label = QLabel()
        self.form_label.setAlignment(Qt.AlignCenter)
        form_font = QFont()
        form_font.setPointSize(24)
        form_font.setBold(True)
        self.form_label.setFont(form_font)
        form_layout.addWidget(self.form_label)

        layout.addWidget(form_group)

        # Root selection
        self.root_group = QGroupBox("1. Select Root Word:")
        self.root_layout = QVBoxLayout()
        self.root_group.setLayout(self.root_layout)
        self.root_button_group = QButtonGroup()
        layout.addWidget(self.root_group)

        # Grammatical feature 1
        self.feature1_group = QGroupBox()
        self.feature1_layout = QVBoxLayout()
        self.feature1_group.setLayout(self.feature1_layout)
        self.feature1_button_group = QButtonGroup()
        layout.addWidget(self.feature1_group)

        # Grammatical feature 2
        self.feature2_group = QGroupBox()
        self.feature2_layout = QVBoxLayout()
        self.feature2_group.setLayout(self.feature2_layout)
        self.feature2_button_group = QButtonGroup()
        layout.addWidget(self.feature2_group)

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

        self.check_button = QPushButton("✓ Check Answer")
        self.check_button.clicked.connect(self.check_answer)
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
        self.check_button.setEnabled(True)
        self.next_button.setEnabled(False)

        # Randomly choose between verb and noun
        if random.choice([True, False]):
            self.generate_verb_question()
        else:
            self.generate_noun_question()

    def generate_verb_question(self):
        """Generate a verb identification question."""
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

        # Display inflected form
        self.form_label.setText(verb_data['form'])

        # Get all verbs for choices
        all_verbs = self.db.get_all_verbs(script=script)
        correct_root = verb_data['root']

        # Create root choices (including correct answer + 3 distractors)
        root_choices = [correct_root]
        other_verbs = [v['root'] for v in all_verbs if v['root'] != correct_root]
        root_choices.extend(random.sample(other_verbs, min(3, len(other_verbs))))
        random.shuffle(root_choices)

        # Clear and populate root choices
        self.clear_button_group(self.root_button_group, self.root_layout)
        for i, root in enumerate(root_choices):
            rb = QRadioButton(root)
            self.root_button_group.addButton(rb, i)
            self.root_layout.addWidget(rb)
            if i == 0:
                rb.setChecked(True)

        # Tense choices
        tenses = ['present', 'past', 'future']
        self.feature1_group.setTitle(f"2. Select {self.converter.convert_term('tense', term_script)}:")
        self.clear_button_group(self.feature1_button_group, self.feature1_layout)
        for i, tense in enumerate(tenses):
            rb = QRadioButton(self.converter.convert_term(tense, term_script))
            rb.setProperty('value', tense)
            self.feature1_button_group.addButton(rb, i)
            self.feature1_layout.addWidget(rb)
            if i == 0:
                rb.setChecked(True)

        # Number choices
        numbers = ['singular', 'plural']
        self.feature2_group.setTitle(f"3. Select {self.converter.convert_term('number', term_script)}:")
        self.clear_button_group(self.feature2_button_group, self.feature2_layout)
        for i, num in enumerate(numbers):
            rb = QRadioButton(self.converter.convert_term(num, term_script))
            rb.setProperty('value', num)
            self.feature2_button_group.addButton(rb, i)
            self.feature2_layout.addWidget(rb)
            if i == 0:
                rb.setChecked(True)

    def generate_noun_question(self):
        """Generate a noun identification question."""
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

        # Display inflected form
        self.form_label.setText(noun_data['form'])

        # Get all nouns for choices
        all_nouns = self.db.get_all_nouns(script=script)
        correct_root = noun_data['root']

        # Create root choices
        root_choices = [correct_root]
        other_nouns = [n['root'] for n in all_nouns if n['root'] != correct_root]
        root_choices.extend(random.sample(other_nouns, min(3, len(other_nouns))))
        random.shuffle(root_choices)

        # Clear and populate root choices
        self.clear_button_group(self.root_button_group, self.root_layout)
        for i, root in enumerate(root_choices):
            rb = QRadioButton(root)
            self.root_button_group.addButton(rb, i)
            self.root_layout.addWidget(rb)
            if i == 0:
                rb.setChecked(True)

        # Case choices (first 4 common cases)
        cases = ['nominative', 'accusative', 'instrumental', 'genitive']
        self.feature1_group.setTitle(f"2. Select {self.converter.convert_term('case', term_script)}:")
        self.clear_button_group(self.feature1_button_group, self.feature1_layout)
        for i, case in enumerate(cases):
            rb = QRadioButton(self.converter.convert_term(case, term_script))
            rb.setProperty('value', case)
            self.feature1_button_group.addButton(rb, i)
            self.feature1_layout.addWidget(rb)
            if i == 0:
                rb.setChecked(True)

        # Number choices
        numbers = ['singular', 'plural']
        self.feature2_group.setTitle(f"3. Select {self.converter.convert_term('number', term_script)}:")
        self.clear_button_group(self.feature2_button_group, self.feature2_layout)
        for i, num in enumerate(numbers):
            rb = QRadioButton(self.converter.convert_term(num, term_script))
            rb.setProperty('value', num)
            self.feature2_button_group.addButton(rb, i)
            self.feature2_layout.addWidget(rb)
            if i == 0:
                rb.setChecked(True)

    def clear_button_group(self, button_group, layout):
        """Clear all buttons from a button group and layout."""
        # Remove all buttons from group
        for button in button_group.buttons():
            button_group.removeButton(button)
            button.deleteLater()

        # Clear layout
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def check_answer(self):
        """Check if the selected answers are correct."""
        if not self.current_question:
            return

        # Get selected root
        selected_root_btn = self.root_button_group.checkedButton()
        if not selected_root_btn:
            QMessageBox.warning(self, "No Selection", "Please select a root word!")
            return

        selected_root = selected_root_btn.text()
        correct_root = self.current_question['root']

        # Get selected feature 1
        selected_f1_btn = self.feature1_button_group.checkedButton()
        selected_f1 = selected_f1_btn.property('value') if selected_f1_btn else None

        # Get selected feature 2
        selected_f2_btn = self.feature2_button_group.checkedButton()
        selected_f2 = selected_f2_btn.property('value') if selected_f2_btn else None

        # Check correctness
        root_correct = (selected_root == correct_root)

        if self.current_question['type'] == 'verb':
            f1_correct = (selected_f1 == self.current_question['tense'])
            f2_correct = (selected_f2 == self.current_question['number'])
            correct_f1 = self.current_question['tense']
            correct_f2 = self.current_question['number']
        else:  # noun
            f1_correct = (selected_f1 == self.current_question['case'])
            f2_correct = (selected_f2 == self.current_question['number'])
            correct_f1 = self.current_question['case']
            correct_f2 = self.current_question['number']

        all_correct = root_correct and f1_correct and f2_correct

        self.questions_count += 1

        # Display feedback
        if all_correct:
            self.correct_count += 1
            self.feedback_label.setText("✓ Perfect! All answers correct!")
            self.feedback_label.setStyleSheet("color: green; font-weight: bold;")
            if self.parent_window:
                self.parent_window.update_score(15, correct=True)
        else:
            feedback_parts = []
            if not root_correct:
                feedback_parts.append(f"Root: {correct_root} (you selected: {selected_root})")
            if not f1_correct:
                term_script = self.settings.grammar_terminology
                f1_name = 'tense' if self.current_question['type'] == 'verb' else 'case'
                feedback_parts.append(f"{f1_name.capitalize()}: {self.converter.convert_term(correct_f1, term_script)}")
            if not f2_correct:
                feedback_parts.append(f"Number: {self.converter.convert_term(correct_f2, term_script)}")

            self.feedback_label.setText("✗ Incorrect.\nCorrect answers:\n" + "\n".join(feedback_parts))
            self.feedback_label.setStyleSheet("color: red; font-weight: bold;")
            if self.parent_window:
                self.parent_window.update_score(0, correct=False)

        self.check_button.setEnabled(False)
        self.next_button.setEnabled(True)
        self.update_stats()

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
        if self.current_question:
            saved_state = (self.questions_count, self.correct_count)
            if self.current_question['type'] == 'verb':
                self.generate_verb_question()
            else:
                self.generate_noun_question()
            self.questions_count, self.correct_count = saved_state
            self.update_stats()
