"""
Database module for Prakrit verb analyzer.

Handles SQLite database operations for:
1. Verified verb forms validation
2. User feedback collection
3. Root information lookup
"""

import sqlite3
import json
import logging
import os
from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class PrakritDatabase:
    """Database handler for Prakrit verb forms and user feedback."""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize database connections.

        Args:
            data_dir: Directory containing database files
        """
        self.data_dir = data_dir
        self.verbs_db_path = os.path.join(data_dir, "prakrit_verbs.db")
        self.feedback_db_path = os.path.join(data_dir, "user_feedback.db")

        # Initialize databases if they don't exist
        self._init_databases()

    def _init_databases(self):
        """Initialize database tables if they don't exist."""
        try:
            # Create verbs database
            conn = sqlite3.connect(self.verbs_db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS verbs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    verb_form TEXT NOT NULL UNIQUE,
                    root TEXT NOT NULL,
                    tense TEXT NOT NULL,
                    person TEXT,
                    number TEXT,
                    mood TEXT,
                    voice TEXT,
                    source TEXT,
                    dialect TEXT,
                    confidence REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS roots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    root TEXT NOT NULL UNIQUE,
                    meaning TEXT,
                    class TEXT,
                    sanskrit_cognate TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create indices for faster lookup
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_verb_form ON verbs(verb_form)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_root ON verbs(root)')

            conn.commit()
            conn.close()

            # Create feedback database
            conn = sqlite3.connect(self.feedback_db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    verb_form TEXT NOT NULL,
                    selected_analysis TEXT NOT NULL,
                    all_analyses TEXT NOT NULL,
                    user_ip TEXT,
                    user_agent TEXT,
                    session_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_verb ON feedback(verb_form)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_date ON feedback(created_at)')

            conn.commit()
            conn.close()

            logger.info("Database tables initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing databases: {e}")

    def lookup_verb(self, verb_form: str) -> Optional[Dict[str, Any]]:
        """
        Look up a verb form in the database.

        Args:
            verb_form: The verb form to look up

        Returns:
            Dictionary with verb information if found, None otherwise
        """
        try:
            conn = sqlite3.connect(self.verbs_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM verbs WHERE verb_form = ? LIMIT 1
            ''', (verb_form,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            return None

        except Exception as e:
            logger.error(f"Error looking up verb '{verb_form}': {e}")
            return None

    def lookup_root(self, root: str) -> Optional[Dict[str, Any]]:
        """
        Look up a root in the database.

        Args:
            root: The root to look up

        Returns:
            Dictionary with root information if found, None otherwise
        """
        try:
            conn = sqlite3.connect(self.verbs_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM roots WHERE root = ? LIMIT 1
            ''', (root,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            return None

        except Exception as e:
            logger.error(f"Error looking up root '{root}': {e}")
            return None

    def add_feedback(
        self,
        verb_form: str,
        selected_analysis: Dict[str, Any],
        all_analyses: List[Dict[str, Any]],
        user_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Record user feedback about which analysis was correct.

        Args:
            verb_form: The verb form that was analyzed
            selected_analysis: The analysis the user marked as correct
            all_analyses: All analyses that were presented
            user_ip: User's IP address (optional, for analytics)
            user_agent: User's browser agent (optional)
            session_id: Session identifier (optional)

        Returns:
            True if feedback was recorded successfully
        """
        try:
            conn = sqlite3.connect(self.feedback_db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO feedback
                (verb_form, selected_analysis, all_analyses, user_ip, user_agent, session_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                verb_form,
                json.dumps(selected_analysis),
                json.dumps(all_analyses),
                user_ip,
                user_agent,
                session_id
            ))

            conn.commit()
            conn.close()

            logger.info(f"Feedback recorded for '{verb_form}'")
            return True

        except Exception as e:
            logger.error(f"Error recording feedback: {e}")
            return False

    def get_feedback_stats(self, verb_form: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about user feedback.

        Args:
            verb_form: Optional verb form to filter by

        Returns:
            Dictionary with feedback statistics
        """
        try:
            conn = sqlite3.connect(self.feedback_db_path)
            cursor = conn.cursor()

            if verb_form:
                cursor.execute('SELECT COUNT(*) FROM feedback WHERE verb_form = ?', (verb_form,))
                count = cursor.fetchone()[0]

                cursor.execute('''
                    SELECT selected_analysis, COUNT(*) as frequency
                    FROM feedback
                    WHERE verb_form = ?
                    GROUP BY selected_analysis
                    ORDER BY frequency DESC
                ''', (verb_form,))

                analyses = cursor.fetchall()
            else:
                cursor.execute('SELECT COUNT(*) FROM feedback')
                count = cursor.fetchone()[0]
                analyses = []

            conn.close()

            return {
                "total_feedback": count,
                "analyses": analyses
            }

        except Exception as e:
            logger.error(f"Error getting feedback stats: {e}")
            return {"total_feedback": 0, "analyses": []}

    def close(self):
        """Close database connections (cleanup)."""
        # SQLite connections are closed after each operation
        pass


# Global database instance
_db_instance = None

def get_database() -> Optional[PrakritDatabase]:
    """
    Get or create the global database instance.

    Returns:
        PrakritDatabase instance or None if initialization failed
    """
    global _db_instance

    if _db_instance is None:
        try:
            _db_instance = PrakritDatabase()
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            return None

    return _db_instance
