#!/usr/bin/env python3
"""
Database handler for Prakrit verb and noun forms - Web version.
Supports both SQLite (local) and PostgreSQL (Supabase).
"""

import os
import random
from typing import List, Dict, Optional

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

import sqlite3
from core.script_converter import ScriptConverter


class PrakritDatabaseWeb:
    """Handles database operations for both SQLite and PostgreSQL."""

    def __init__(self, db_url=None, use_sqlite=False, verbs_db_path=None, nouns_db_path=None):
        """
        Initialize database connections.

        Args:
            db_url: PostgreSQL connection URL (e.g., from Supabase)
            use_sqlite: Force use of SQLite instead of PostgreSQL
            verbs_db_path: Path to SQLite verb_forms.db (if using SQLite)
            nouns_db_path: Path to SQLite noun_forms.db (if using SQLite)
        """
        self.converter = ScriptConverter()
        self.use_postgres = False

        # Try to use PostgreSQL if URL provided
        if db_url and not use_sqlite and HAS_PSYCOPG2:
            try:
                self.pg_conn = psycopg2.connect(db_url)
                self.use_postgres = True
                print("✓ Connected to PostgreSQL database")
            except Exception as e:
                print(f"⚠ PostgreSQL connection failed: {e}")
                print("⚠ Falling back to SQLite")
                self.use_postgres = False

        # Fall back to SQLite
        if not self.use_postgres:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, 'data')

            self.verbs_db_path = verbs_db_path or os.path.join(data_dir, 'verb_forms.db')
            self.nouns_db_path = nouns_db_path or os.path.join(data_dir, 'noun_forms.db')

            if not os.path.exists(self.verbs_db_path):
                raise FileNotFoundError(f"Verb database not found: {self.verbs_db_path}")
            if not os.path.exists(self.nouns_db_path):
                raise FileNotFoundError(f"Noun database not found: {self.nouns_db_path}")

    def _execute_query(self, query: str, params: tuple = None, db_type: str = 'verb') -> List[Dict]:
        """Execute a query and return results as list of dicts."""
        if self.use_postgres:
            cursor = self.pg_conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return [dict(row) for row in results]
        else:
            # SQLite
            db_path = self.verbs_db_path if db_type == 'verb' else self.nouns_db_path
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results

    # ===== VERB METHODS =====

    def get_verb_form(self, root: str, tense: str, person: str, number: str,
                      script: str = 'devanagari') -> Optional[str]:
        """Get a specific verb form."""
        if self.use_postgres:
            query = '''
                SELECT vf.form
                FROM verbs v
                JOIN verb_forms vf ON v.id = vf.verb_id
                WHERE v.root = %s AND vf.tense = %s AND vf.person = %s AND vf.number = %s
            '''
        else:
            query = '''
                SELECT vf.form
                FROM verbs v
                JOIN verb_forms vf ON v.id = vf.verb_id
                WHERE v.root = ? AND vf.tense = ? AND vf.person = ? AND vf.number = ?
            '''

        results = self._execute_query(query, (root, tense, person, number), 'verb')

        if results:
            form_hk = results[0]['form']
            return self.converter.convert(form_hk, 'hk', script)
        return None

    def get_random_verb_form(self, difficulty: str = None, script: str = 'devanagari') -> Optional[Dict]:
        """Get a random verb form with full context."""
        # Get random verb
        if self.use_postgres:
            if difficulty:
                verb_query = "SELECT * FROM verbs WHERE difficulty = %s ORDER BY RANDOM() LIMIT 1"
                params = (difficulty,)
            else:
                verb_query = "SELECT * FROM verbs ORDER BY RANDOM() LIMIT 1"
                params = None
        else:
            if difficulty:
                verb_query = "SELECT * FROM verbs WHERE difficulty = ? ORDER BY RANDOM() LIMIT 1"
                params = (difficulty,)
            else:
                verb_query = "SELECT * FROM verbs ORDER BY RANDOM() LIMIT 1"
                params = None

        verbs = self._execute_query(verb_query, params, 'verb')
        if not verbs:
            return None

        verb = verbs[0]

        # Get random form of this verb
        if self.use_postgres:
            form_query = "SELECT * FROM verb_forms WHERE verb_id = %s ORDER BY RANDOM() LIMIT 1"
        else:
            form_query = "SELECT * FROM verb_forms WHERE verb_id = ? ORDER BY RANDOM() LIMIT 1"

        forms = self._execute_query(form_query, (verb['id'],), 'verb')
        if not forms:
            return None

        form_data = forms[0]

        return {
            'form': self.converter.convert(form_data['form'], 'hk', script),
            'form_hk': form_data['form'],
            'root': self.converter.convert(verb['root'], 'hk', script),
            'root_hk': verb['root'],
            'meaning': verb['meaning'],
            'tense': form_data['tense'],
            'person': form_data['person'],
            'number': form_data['number'],
            'transitivity': verb['transitivity'],
            'difficulty': verb['difficulty']
        }

    def get_all_verbs(self, script: str = 'devanagari') -> List[Dict]:
        """Get list of all verbs."""
        query = "SELECT id, root, meaning, transitivity, difficulty FROM verbs"
        verbs = self._execute_query(query, db_type='verb')

        return [{
            'id': v['id'],
            'root': self.converter.convert(v['root'], 'hk', script),
            'root_hk': v['root'],
            'meaning': v['meaning'],
            'transitivity': v['transitivity'],
            'difficulty': v['difficulty']
        } for v in verbs]

    # ===== NOUN METHODS =====

    def get_noun_form(self, root: str, case_name: str, number: str,
                      script: str = 'devanagari') -> Optional[str]:
        """Get a specific noun form."""
        if self.use_postgres:
            query = '''
                SELECT nf.form
                FROM nouns n
                JOIN noun_forms nf ON n.id = nf.noun_id
                WHERE n.root = %s AND nf.case_name = %s AND nf.number = %s
            '''
        else:
            query = '''
                SELECT nf.form
                FROM nouns n
                JOIN noun_forms nf ON n.id = nf.noun_id
                WHERE n.root = ? AND nf.case_name = ? AND nf.number = ?
            '''

        results = self._execute_query(query, (root, case_name, number), 'noun')

        if results:
            form_hk = results[0]['form']
            return self.converter.convert(form_hk, 'hk', script)
        return None

    def get_random_noun_form(self, difficulty: str = None, script: str = 'devanagari') -> Optional[Dict]:
        """Get a random noun form with full context."""
        # Get random noun
        if self.use_postgres:
            if difficulty:
                noun_query = "SELECT * FROM nouns WHERE difficulty = %s ORDER BY RANDOM() LIMIT 1"
                params = (difficulty,)
            else:
                noun_query = "SELECT * FROM nouns ORDER BY RANDOM() LIMIT 1"
                params = None
        else:
            if difficulty:
                noun_query = "SELECT * FROM nouns WHERE difficulty = ? ORDER BY RANDOM() LIMIT 1"
                params = (difficulty,)
            else:
                noun_query = "SELECT * FROM nouns ORDER BY RANDOM() LIMIT 1"
                params = None

        nouns = self._execute_query(noun_query, params, 'noun')
        if not nouns:
            return None

        noun = nouns[0]

        # Get random form
        if self.use_postgres:
            form_query = "SELECT * FROM noun_forms WHERE noun_id = %s ORDER BY RANDOM() LIMIT 1"
        else:
            form_query = "SELECT * FROM noun_forms WHERE noun_id = ? ORDER BY RANDOM() LIMIT 1"

        forms = self._execute_query(form_query, (noun['id'],), 'noun')
        if not forms:
            return None

        form_data = forms[0]

        return {
            'form': self.converter.convert(form_data['form'], 'hk', script),
            'form_hk': form_data['form'],
            'root': self.converter.convert(noun['root'], 'hk', script),
            'root_hk': noun['root'],
            'meaning': noun['meaning'],
            'case': form_data['case_name'],
            'number': form_data['number'],
            'gender': noun['gender'],
            'difficulty': noun['difficulty']
        }

    def get_all_nouns(self, script: str = 'devanagari') -> List[Dict]:
        """Get list of all nouns."""
        query = "SELECT id, root, meaning, gender, difficulty FROM nouns"
        nouns = self._execute_query(query, db_type='noun')

        return [{
            'id': n['id'],
            'root': self.converter.convert(n['root'], 'hk', script),
            'root_hk': n['root'],
            'meaning': n['meaning'],
            'gender': n['gender'],
            'difficulty': n['difficulty']
        } for n in nouns]

    def get_noun_paradigm(self, root: str, script: str = 'devanagari') -> Dict:
        """Get all forms of a noun (full declension table)."""
        if self.use_postgres:
            query = '''
                SELECT nf.case_name, nf.number, nf.form
                FROM nouns n
                JOIN noun_forms nf ON n.id = nf.noun_id
                WHERE n.root = %s
            '''
        else:
            query = '''
                SELECT nf.case_name, nf.number, nf.form
                FROM nouns n
                JOIN noun_forms nf ON n.id = nf.noun_id
                WHERE n.root = ?
            '''

        results = self._execute_query(query, (root,), 'noun')

        paradigm = {}
        for row in results:
            case_name = row['case_name']
            number = row['number']
            form = self.converter.convert(row['form'], 'hk', script)

            if case_name not in paradigm:
                paradigm[case_name] = {}
            paradigm[case_name][number] = form

        return paradigm

    def get_random_noun(self, difficulty: str = None, script: str = 'devanagari') -> Optional[Dict]:
        """Get a random noun with its metadata."""
        if self.use_postgres:
            if difficulty:
                query = "SELECT * FROM nouns WHERE difficulty = %s ORDER BY RANDOM() LIMIT 1"
                params = (difficulty,)
            else:
                query = "SELECT * FROM nouns ORDER BY RANDOM() LIMIT 1"
                params = None
        else:
            if difficulty:
                query = "SELECT * FROM nouns WHERE difficulty = ? ORDER BY RANDOM() LIMIT 1"
                params = (difficulty,)
            else:
                query = "SELECT * FROM nouns ORDER BY RANDOM() LIMIT 1"
                params = None

        nouns = self._execute_query(query, params, 'noun')
        if not nouns:
            return None

        noun = nouns[0]

        return {
            'id': noun['id'],
            'root': self.converter.convert(noun['root'], 'hk', script),
            'root_hk': noun['root'],
            'meaning': noun['meaning'],
            'gender': noun['gender'],
            'difficulty': noun['difficulty']
        }

    def close(self):
        """Close database connections."""
        if self.use_postgres and hasattr(self, 'pg_conn'):
            self.pg_conn.close()
