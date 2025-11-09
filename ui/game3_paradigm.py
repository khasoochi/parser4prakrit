#!/usr/bin/env python3
"""
Game 3: Paradigm Completion (तालिका पूर्ति)
Fill in missing cells in declension/conjugation tables.
"""

import random
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QGroupBox, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class ParadigmCompletionGame(QWidget):
    """Game 3: Paradigm Completion - Fill in declension/conjugation tables."""

    def __init__(self, db, converter, settings, parent=None):
        super().__init__(parent)
        self.db = db
        self.converter = converter
        self.settings = settings
        self.parent_window = parent

        self.current_paradigm = None
        self.questions_count = 0
        self.correct_count = 0
        self.editable_cells = []

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        title = QLabel("तालिका पूर्ति (Paradigm Completion)")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Fill in the missing cells in the declension/conjugation table."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        # Root word display
        self.root_label = QLabel()
        self.root_label.setAlignment(Qt.AlignCenter)
        root_font = QFont()
        root_font.setPointSize(16)
        root_font.setBold(True)
        self.root_label.setFont(root_font)
        layout.addWidget(self.root_label)

        # Paradigm table
        self.table = QTableWidget()
        self.table.setMinimumHeight(300)
        layout.addWidget(self.table)

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

        self.check_button = QPushButton("✓ Check Answers")
        self.check_button.clicked.connect(self.check_answers)
        button_layout.addWidget(self.check_button)

        self.next_button = QPushButton("→ Next Paradigm")
        self.next_button.clicked.connect(self.next_paradigm)
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
        self.next_paradigm()

    def next_paradigm(self):
        """Generate a new paradigm to complete."""
        self.feedback_label.clear()

        script = self.settings.script_preference
        term_script = self.settings.grammar_terminology

        # Randomly choose noun (easier for paradigm view)
        noun = self.db.get_random_noun(difficulty=self.settings.difficulty, script=script)

        if not noun:
            QMessageBox.warning(self, "No Data", "No nouns available!")
            return

        # Get full paradigm
        paradigm = self.db.get_noun_paradigm(noun['root_hk'], script=script)

        if not paradigm:
            return

        self.current_paradigm = paradigm
        self.current_noun = noun

        # Display root
        self.root_label.setText(
            f"{self.converter.convert_term('root', term_script)}: {noun['root']} ({noun['meaning']}) - "
            f"{self.converter.convert_term(noun['gender'], term_script)}"
        )

        # Create table
        cases = list(paradigm.keys())
        numbers = ['singular', 'plural']

        self.table.setRowCount(len(cases))
        self.table.setColumnCount(3)  # Case label + 2 numbers

        # Set headers
        headers = [
            self.converter.convert_term('case', term_script),
            self.converter.convert_term('singular', term_script),
            self.converter.convert_term('plural', term_script)
        ]
        self.table.setHorizontalHeaderLabels(headers)

        # Fill table
        self.editable_cells = []

        for row, case in enumerate(cases):
            # Case label
            case_label = QTableWidgetItem(self.converter.convert_term(case, term_script))
            case_label.setFlags(Qt.ItemIsEnabled)
            case_label.setBackground(QColor(240, 240, 240))
            self.table.setItem(row, 0, case_label)

            # Forms for each number
            for col_idx, number in enumerate(numbers, start=1):
                form = paradigm[case].get(number, '')

                # 50% chance to hide the form (make it editable)
                if random.random() < 0.5 and form:
                    item = QTableWidgetItem('')
                    item.setBackground(QColor(255, 255, 200))  # Yellow for editable
                    self.editable_cells.append((row, col_idx, form))
                else:
                    item = QTableWidgetItem(form)
                    item.setFlags(Qt.ItemIsEnabled)
                    item.setBackground(QColor(240, 255, 240))  # Light green for filled

                self.table.setItem(row, col_idx, item)

        self.table.resizeColumnsToContents()

    def check_answers(self):
        """Check all filled answers."""
        if not self.editable_cells:
            return

        correct = 0
        total = len(self.editable_cells)

        for row, col, correct_answer in self.editable_cells:
            item = self.table.item(row, col)
            user_answer = item.text().strip()

            if user_answer == correct_answer:
                correct += 1
                item.setBackground(QColor(200, 255, 200))  # Light green
            else:
                item.setBackground(QColor(255, 200, 200))  # Light red
                item.setToolTip(f"Correct: {correct_answer}")

        self.questions_count += 1

        # Feedback
        accuracy = (correct / total) * 100 if total > 0 else 0

        if accuracy == 100:
            self.correct_count += 1
            self.feedback_label.setText(f"✓ Perfect! All {total} cells correct!")
            self.feedback_label.setStyleSheet("color: green; font-weight: bold;")
            if self.parent_window:
                self.parent_window.update_score(20, correct=True)
        else:
            self.feedback_label.setText(f"Filled {correct}/{total} cells correctly ({accuracy:.1f}%)")
            self.feedback_label.setStyleSheet("color: orange; font-weight: bold;")
            if self.parent_window:
                self.parent_window.update_score(5, correct=False)

        self.update_stats()

    def update_stats(self):
        """Update statistics display."""
        if self.questions_count > 0:
            accuracy = (self.correct_count / self.questions_count) * 100
            self.stats_label.setText(
                f"Paradigms: {self.questions_count} | Perfect: {self.correct_count} | Accuracy: {accuracy:.1f}%"
            )
        else:
            self.stats_label.setText("No paradigms completed yet.")

    def on_settings_changed(self):
        """Called when settings are changed."""
        if self.current_paradigm:
            self.next_paradigm()
