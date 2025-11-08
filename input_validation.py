"""
Input validation utilities for Prakrit verb analyzer.

This module provides comprehensive input validation and sanitization functions
to ensure safe and correct processing of user inputs.
"""

import re
from typing import Tuple, Optional


class InputValidator:
    """Validator class for Prakrit verb form inputs."""

    # Maximum reasonable length for a verb form (prevents DoS attacks)
    MAX_INPUT_LENGTH = 200

    # Minimum length for a meaningful verb form
    MIN_INPUT_LENGTH = 1

    # Valid character ranges for different scripts
    DEVANAGARI_RANGE = r'[\u0900-\u097F]'
    HK_VALID_CHARS = r'[a-zA-Z0-9_]'

    # Suspicious patterns that might indicate malicious input
    SUSPICIOUS_PATTERNS = [
        r'<script',  # HTML/JS injection
        r'javascript:',  # JS protocol
        r'on\w+\s*=',  # Event handlers
        r'[\x00-\x08\x0B-\x0C\x0E-\x1F]',  # Control characters
    ]

    @classmethod
    def validate_verb_form(cls, text: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a verb form input.

        Args:
            text: The input text to validate

        Returns:
            Tuple of (is_valid, error_message)
            If valid: (True, None)
            If invalid: (False, error_description)
        """
        # Check if input is None
        if text is None:
            return False, "Input cannot be None"

        # Check if input is a string
        if not isinstance(text, str):
            return False, f"Input must be a string, got {type(text).__name__}"

        # Strip whitespace for validation
        text_stripped = text.strip()

        # Check for empty input
        if len(text_stripped) == 0:
            return False, "Input cannot be empty or whitespace-only"

        # Check minimum length
        if len(text_stripped) < cls.MIN_INPUT_LENGTH:
            return False, f"Input too short (minimum {cls.MIN_INPUT_LENGTH} character)"

        # Check maximum length
        if len(text_stripped) > cls.MAX_INPUT_LENGTH:
            return False, f"Input too long (maximum {cls.MAX_INPUT_LENGTH} characters)"

        # Check for suspicious patterns
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False, "Input contains potentially malicious content"

        # Check if input contains only valid characters
        # Valid: Devanagari, Latin letters, diacritics, space, hyphen, underscore
        valid_pattern = r'^[a-zA-Zāīūṛṝḷḹéóṁḥṅñṭḍṇśṣḻ\u0900-\u097F\s\-_]+$'
        if not re.match(valid_pattern, text_stripped):
            return False, "Input contains invalid characters for Prakrit text"

        return True, None

    @classmethod
    def sanitize_verb_form(cls, text: str) -> str:
        """
        Sanitize a verb form input by removing/replacing problematic characters.

        Args:
            text: The input text to sanitize

        Returns:
            Sanitized text

        Note:
            This function should be called after validation passes.
        """
        if not isinstance(text, str):
            return ""

        # Strip leading/trailing whitespace
        text = text.strip()

        # Normalize multiple spaces to single space
        text = re.sub(r'\s+', ' ', text)

        # Remove any remaining control characters
        text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)

        return text

    @classmethod
    def normalize_hk_input(cls, text: str) -> str:
        """
        Normalize Harvard-Kyoto transliteration input.

        Args:
            text: HK transliteration text

        Returns:
            Normalized text with common variations standardized

        Example:
            >>> normalize_hk_input("M")  # Anusvara
            'M'
            >>> normalize_hk_input("H")  # Visarga
            'H'
        """
        # Normalize common HK variations
        # (This can be expanded based on observed input patterns)
        text = text.replace('~', 'M')  # Alternative anusvara
        text = text.replace('^', 'M')  # Another alternative

        return text

    @classmethod
    def validate_script(cls, text: str, expected_script: str) -> bool:
        """
        Validate that text matches the expected script.

        Args:
            text: Input text
            expected_script: 'devanagari' or 'hk'

        Returns:
            True if text appears to be in the expected script
        """
        if expected_script == 'devanagari':
            # Should contain at least one Devanagari character
            return bool(re.search(cls.DEVANAGARI_RANGE, text))
        elif expected_script == 'hk':
            # Should NOT contain Devanagari characters
            return not bool(re.search(cls.DEVANAGARI_RANGE, text))
        else:
            return False


def validate_and_sanitize(text: str) -> Tuple[bool, Optional[str], str]:
    """
    Convenience function to validate and sanitize input in one call.

    Args:
        text: Input text

    Returns:
        Tuple of (is_valid, error_message, sanitized_text)
    """
    is_valid, error = InputValidator.validate_verb_form(text)

    if not is_valid:
        return False, error, ""

    sanitized = InputValidator.sanitize_verb_form(text)
    return True, None, sanitized
