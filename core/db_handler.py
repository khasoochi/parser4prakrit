#!/usr/bin/env python3
"""
Database handler for Prakrit verb and noun forms.
Integrates with script converter to provide forms in multiple scripts.
"""

import sqlite3
import os
import random
from typing import List, Dict, Tuple, Optional
from core.script_converter import ScriptConverter


class PrakritDatabase:
    """Handles database operations for Prakrit verb and noun forms."""

    def __init__(self, verbs_db_path=None, nouns_db_path=None):
        """
        Initialize database connections.

        Args:
            verbs_db_path: Path to verb_forms.db (optional, uses default if not provided)
            nouns_db_path: Path to noun_forms.db (optional, uses default if not provided)
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')

        self.verbs_db_path = verbs_db_path or os.path.join(data_dir, 'verb_forms.db')
        self.nouns_db_path = nouns_db_path or os.path.join(data_dir, 'noun_forms.db')

        # Initialize script converter
        self.converter = ScriptConverter()

        # Verify databases exist
        if not os.path.exists(self.verbs_db_path):
            raise FileNotFoundError(f"Verb database not found: {self.verbs_db_path}")
        if not os.path.exists(self.nouns_db_path):
            raise FileNotFoundError(f"Noun database not found: {self.nouns_db_path}")

    def _get_connection(self, db_type='verb'):
        """Get a database connection."""
        db_path = self.verbs_db_path if db_type == 'verb' else self.nouns_db_path
        return sqlite3.connect(db_path)

    # ===== VERB METHODS =====

    def get_verb_form(self, root: str, tense: str, person: str, number: str,
                      script: str = 'devanagari') -> Optional[str]:
        """
        Get a specific verb form.

        Args:
            root: Verb root in HK (e.g., 'pac')
            tense: Tense (e.g., 'present', 'past', 'future')
            person: Person (e.g., 'first', 'second', 'third')
            number: Number (e.g., 'singular', 'plural')
            script: Target script ('devanagari', 'iast', 'iso15919', 'hk')

        Returns:
            The verb form in the requested script, or None if not found
        """
        conn = self._get_connection('verb')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT vf.form
            FROM verbs v
            JOIN verb_forms vf ON v.id = vf.verb_id
            WHERE v.root = ? AND vf.tense = ? AND vf.person = ? AND vf.number = ?
        ''', (root, tense, person, number))

        result = cursor.fetchone()
        conn.close()

        if result:
            form_hk = result[0]
            return self.converter.convert(form_hk, 'hk', script)
        return None

    def get_verb_paradigm(self, root: str, script: str = 'devanagari') -> Dict:
        """
        Get all forms of a verb (full paradigm).

        Args:
            root: Verb root in HK
            script: Target script

        Returns:
            Dictionary with all verb forms organized by tense, person, and number
        """
        conn = self._get_connection('verb')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT vf.tense, vf.person, vf.number, vf.form
            FROM verbs v
            JOIN verb_forms vf ON v.id = vf.verb_id
            WHERE v.root = ?
        ''', (root,))

        paradigm = {}
        for row in cursor.fetchall():
            tense, person, number, form_hk = row
            form = self.converter.convert(form_hk, 'hk', script)

            if tense not in paradigm:
                paradigm[tense] = {}
            if person not in paradigm[tense]:
                paradigm[tense][person] = {}
            paradigm[tense][person][number] = form

        conn.close()
        return paradigm

    def get_random_verb(self, difficulty: str = None, script: str = 'devanagari') -> Optional[Dict]:
        """
        Get a random verb with its metadata.

        Args:
            difficulty: Filter by difficulty ('easy', 'medium', 'hard') or None for any
            script: Target script for root word

        Returns:
            Dictionary with verb information
        """
        conn = self._get_connection('verb')
        cursor = conn.cursor()

        if difficulty:
            cursor.execute('SELECT * FROM verbs WHERE difficulty = ?', (difficulty,))
        else:
            cursor.execute('SELECT * FROM verbs')

        verbs = cursor.fetchall()
        conn.close()

        if not verbs:
            return None

        verb = random.choice(verbs)
        verb_id, root, meaning, transitivity, diff = verb

        return {
            'id': verb_id,
            'root': self.converter.convert(root, 'hk', script),
            'root_hk': root,
            'meaning': meaning,
            'transitivity': transitivity,
            'difficulty': diff
        }

    def get_random_verb_form(self, difficulty: str = None, script: str = 'devanagari') -> Optional[Dict]:
        """
        Get a random verb form with full context.

        Args:
            difficulty: Filter by difficulty
            script: Target script

        Returns:
            Dictionary with verb form, root, and grammatical features
        """
        verb = self.get_random_verb(difficulty)
        if not verb:
            return None

        # Get a random form of this verb
        conn = self._get_connection('verb')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM verb_forms WHERE verb_id = ?', (verb['id'],))
        forms = cursor.fetchall()
        conn.close()

        if not forms:
            return None

        form_data = random.choice(forms)
        form_id, verb_id, tense, person, number, form_hk = form_data

        return {
            'form': self.converter.convert(form_hk, 'hk', script),
            'form_hk': form_hk,
            'root': verb['root'],
            'root_hk': verb['root_hk'],
            'meaning': verb['meaning'],
            'tense': tense,
            'person': person,
            'number': number,
            'transitivity': verb['transitivity'],
            'difficulty': verb['difficulty']
        }

    # ===== NOUN METHODS =====

    def get_noun_form(self, root: str, case_name: str, number: str,
                      script: str = 'devanagari') -> Optional[str]:
        """
        Get a specific noun form.

        Args:
            root: Noun root in HK (e.g., 'dhamma')
            case_name: Case (e.g., 'nominative', 'accusative', 'instrumental')
            number: Number (e.g., 'singular', 'plural')
            script: Target script

        Returns:
            The noun form in the requested script, or None if not found
        """
        conn = self._get_connection('noun')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT nf.form
            FROM nouns n
            JOIN noun_forms nf ON n.id = nf.noun_id
            WHERE n.root = ? AND nf.case_name = ? AND nf.number = ?
        ''', (root, case_name, number))

        result = cursor.fetchone()
        conn.close()

        if result:
            form_hk = result[0]
            return self.converter.convert(form_hk, 'hk', script)
        return None

    def get_noun_paradigm(self, root: str, script: str = 'devanagari') -> Dict:
        """
        Get all forms of a noun (full declension table).

        Args:
            root: Noun root in HK
            script: Target script

        Returns:
            Dictionary with all noun forms organized by case and number
        """
        conn = self._get_connection('noun')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT nf.case_name, nf.number, nf.form
            FROM nouns n
            JOIN noun_forms nf ON n.id = nf.noun_id
            WHERE n.root = ?
        ''', (root,))

        paradigm = {}
        for row in cursor.fetchall():
            case_name, number, form_hk = row
            form = self.converter.convert(form_hk, 'hk', script)

            if case_name not in paradigm:
                paradigm[case_name] = {}
            paradigm[case_name][number] = form

        conn.close()
        return paradigm

    def get_random_noun(self, difficulty: str = None, script: str = 'devanagari') -> Optional[Dict]:
        """
        Get a random noun with its metadata.

        Args:
            difficulty: Filter by difficulty ('easy', 'medium', 'hard') or None for any
            script: Target script for root word

        Returns:
            Dictionary with noun information
        """
        conn = self._get_connection('noun')
        cursor = conn.cursor()

        if difficulty:
            cursor.execute('SELECT * FROM nouns WHERE difficulty = ?', (difficulty,))
        else:
            cursor.execute('SELECT * FROM nouns')

        nouns = cursor.fetchall()
        conn.close()

        if not nouns:
            return None

        noun = random.choice(nouns)
        noun_id, root, meaning, gender, diff = noun

        return {
            'id': noun_id,
            'root': self.converter.convert(root, 'hk', script),
            'root_hk': root,
            'meaning': meaning,
            'gender': gender,
            'difficulty': diff
        }

    def get_random_noun_form(self, difficulty: str = None, script: str = 'devanagari') -> Optional[Dict]:
        """
        Get a random noun form with full context.

        Args:
            difficulty: Filter by difficulty
            script: Target script

        Returns:
            Dictionary with noun form, root, and grammatical features
        """
        noun = self.get_random_noun(difficulty)
        if not noun:
            return None

        # Get a random form of this noun
        conn = self._get_connection('noun')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM noun_forms WHERE noun_id = ?', (noun['id'],))
        forms = cursor.fetchall()
        conn.close()

        if not forms:
            return None

        form_data = random.choice(forms)
        form_id, noun_id, case_name, number, form_hk = form_data

        return {
            'form': self.converter.convert(form_hk, 'hk', script),
            'form_hk': form_hk,
            'root': noun['root'],
            'root_hk': noun['root_hk'],
            'meaning': noun['meaning'],
            'case': case_name,
            'number': number,
            'gender': noun['gender'],
            'difficulty': noun['difficulty']
        }

    # ===== SEARCH METHODS =====

    def search_by_form(self, inflected_form: str, word_type: str = 'both') -> List[Dict]:
        """
        Reverse lookup: find root and grammatical features from an inflected form.

        Args:
            inflected_form: The inflected form to search for (in HK)
            word_type: 'verb', 'noun', or 'both'

        Returns:
            List of dictionaries with matching results
        """
        results = []

        # Search verbs
        if word_type in ('verb', 'both'):
            conn = self._get_connection('verb')
            cursor = conn.cursor()

            cursor.execute('''
                SELECT v.root, v.meaning, v.transitivity, vf.tense, vf.person, vf.number
                FROM verbs v
                JOIN verb_forms vf ON v.id = vf.verb_id
                WHERE vf.form = ?
            ''', (inflected_form,))

            for row in cursor.fetchall():
                root, meaning, transitivity, tense, person, number = row
                results.append({
                    'type': 'verb',
                    'root': root,
                    'meaning': meaning,
                    'transitivity': transitivity,
                    'tense': tense,
                    'person': person,
                    'number': number
                })

            conn.close()

        # Search nouns
        if word_type in ('noun', 'both'):
            conn = self._get_connection('noun')
            cursor = conn.cursor()

            cursor.execute('''
                SELECT n.root, n.meaning, n.gender, nf.case_name, nf.number
                FROM nouns n
                JOIN noun_forms nf ON n.id = nf.noun_id
                WHERE nf.form = ?
            ''', (inflected_form,))

            for row in cursor.fetchall():
                root, meaning, gender, case_name, number = row
                results.append({
                    'type': 'noun',
                    'root': root,
                    'meaning': meaning,
                    'gender': gender,
                    'case': case_name,
                    'number': number
                })

            conn.close()

        return results

    # ===== UTILITY METHODS =====

    def get_all_verbs(self, script: str = 'devanagari') -> List[Dict]:
        """Get list of all verbs."""
        conn = self._get_connection('verb')
        cursor = conn.cursor()
        cursor.execute('SELECT id, root, meaning, transitivity, difficulty FROM verbs')

        verbs = []
        for row in cursor.fetchall():
            verb_id, root, meaning, transitivity, diff = row
            verbs.append({
                'id': verb_id,
                'root': self.converter.convert(root, 'hk', script),
                'root_hk': root,
                'meaning': meaning,
                'transitivity': transitivity,
                'difficulty': diff
            })

        conn.close()
        return verbs

    def get_all_nouns(self, script: str = 'devanagari') -> List[Dict]:
        """Get list of all nouns."""
        conn = self._get_connection('noun')
        cursor = conn.cursor()
        cursor.execute('SELECT id, root, meaning, gender, difficulty FROM nouns')

        nouns = []
        for row in cursor.fetchall():
            noun_id, root, meaning, gender, diff = row
            nouns.append({
                'id': noun_id,
                'root': self.converter.convert(root, 'hk', script),
                'root_hk': root,
                'meaning': meaning,
                'gender': gender,
                'difficulty': diff
            })

        conn.close()
        return nouns


# Test if run directly
if __name__ == '__main__':
    print("Testing Database Handler:")
    print("="*60)

    try:
        db = PrakritDatabase()

        # Test verb retrieval
        print("\n1. Testing verb form retrieval:")
        form = db.get_verb_form('pac', 'present', 'first', 'singular', script='devanagari')
        print(f"  pac (present, 1st, singular) in Devanagari: {form}")

        form_iast = db.get_verb_form('pac', 'present', 'first', 'singular', script='iast')
        print(f"  pac (present, 1st, singular) in IAST: {form_iast}")

        # Test random verb form
        print("\n2. Testing random verb form:")
        random_verb = db.get_random_verb_form(script='devanagari')
        if random_verb:
            print(f"  Root: {random_verb['root']} ({random_verb['meaning']})")
            print(f"  Form: {random_verb['form']}")
            print(f"  Grammar: {random_verb['tense']}, {random_verb['person']}, {random_verb['number']}")

        # Test noun retrieval
        print("\n3. Testing noun form retrieval:")
        noun_form = db.get_noun_form('dhamma', 'nominative', 'singular', script='devanagari')
        print(f"  dhamma (nominative, singular) in Devanagari: {noun_form}")

        noun_form_iast = db.get_noun_form('dhamma', 'instrumental', 'singular', script='iast')
        print(f"  dhamma (instrumental, singular) in IAST: {noun_form_iast}")

        # Test random noun form
        print("\n4. Testing random noun form:")
        random_noun = db.get_random_noun_form(script='devanagari')
        if random_noun:
            print(f"  Root: {random_noun['root']} ({random_noun['meaning']})")
            print(f"  Form: {random_noun['form']}")
            print(f"  Grammar: {random_noun['case']}, {random_noun['number']}, {random_noun['gender']}")

        # Test paradigm retrieval
        print("\n5. Testing paradigm retrieval:")
        paradigm = db.get_noun_paradigm('dhamma', script='devanagari')
        print(f"  dhamma paradigm (first 3 cases):")
        for i, (case, forms) in enumerate(list(paradigm.items())[:3]):
            print(f"    {case}: {forms}")

        print("\n" + "="*60)
        print("Database handler tests completed successfully!")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
