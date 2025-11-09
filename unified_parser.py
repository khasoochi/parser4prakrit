"""
Unified Prakrit Parser
Combines verb and noun analysis with holistic ending-based guessing
Implements proper suffix priority and blocking rules
"""

import re
import json
import os
from typing import Dict, List, Tuple, Optional

# Optional dependencies
try:
    from flask import Flask, render_template, request, jsonify
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

try:
    from aksharamukha import transliterate as aksh_transliterate
    HAS_AKSHARAMUKHA = True
except ImportError:
    HAS_AKSHARAMUKHA = False
    print("Warning: aksharamukha not installed. Install with: pip install aksharamukha")

# Initialize Flask app only if available
if HAS_FLASK:
    app = Flask(__name__)

class PrakritUnifiedParser:
    """
    Unified parser for both Prakrit verbs and nouns with intelligent ending-based analysis
    """

    def __init__(self, auto_download=True):
        """
        Initialize parser

        Args:
            auto_download: If True, automatically download missing databases
        """
        # Auto-download databases if missing
        if auto_download:
            self.ensure_databases()

        self.load_data()
        self.load_feedback_data()
        self.initialize_suffix_database()
        self.load_dictionary()

    def ensure_databases(self):
        """Ensure databases are available, download if missing"""
        try:
            from download_databases import download_if_missing
            db_paths = download_if_missing()
        except Exception as e:
            # Silently continue if download fails
            pass

    def load_dictionary(self):
        """Load dictionary database if available"""
        self.dictionary = None
        try:
            dict_path = os.path.join(os.path.dirname(__file__), 'prakrit-dict.db')
            if os.path.exists(dict_path):
                from dictionary_lookup import PrakritDictionary
                self.dictionary = PrakritDictionary(dict_path)
                print("✓ Dictionary database loaded")
        except Exception as e:
            # Dictionary is optional
            pass

    def load_data(self):
        """Load verb and noun data from SQLite databases or JSON files"""
        # Try SQLite databases first, fall back to JSON
        self.verb_roots = self.load_verb_roots()
        self.all_verb_forms = self.load_verb_forms_db()
        self.all_noun_forms = self.load_noun_forms_db()

    def load_verb_roots(self):
        """Load verb roots from verbs1.json"""
        try:
            verbs1_path = os.path.join(os.path.dirname(__file__), 'verbs1.json')
            with open(verbs1_path, encoding='utf-8') as f:
                verbs1_data = json.load(f)
                return set(verbs1_data.values())
        except Exception as e:
            print(f"Warning: Could not load verbs1.json: {e}")
            return set()

    def load_verb_forms_db(self):
        """Load verb forms from SQLite database or JSON fallback"""
        # Try SQLite database first
        try:
            import sqlite3
            db_path = os.path.join(os.path.dirname(__file__), 'verb_forms.db')
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Load all verb forms
                cursor.execute('SELECT root, forms FROM verb_forms')
                verb_forms = {}
                for root, forms_json in cursor.fetchall():
                    verb_forms[root] = json.loads(forms_json) if forms_json else {}

                conn.close()
                if verb_forms:
                    print(f"✓ Loaded {len(verb_forms)} verb roots from database")
                    return verb_forms
        except Exception as e:
            pass

        # Fallback to JSON
        try:
            all_verb_forms_path = os.path.join(os.path.dirname(__file__), 'all_verb_forms.json')
            with open(all_verb_forms_path, encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load verb forms: {e}")
            return {}

    def load_noun_forms_db(self):
        """Load noun forms from SQLite database or JSON fallback"""
        # Try SQLite database first
        try:
            import sqlite3
            db_path = os.path.join(os.path.dirname(__file__), 'noun_forms.db')
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Load all noun forms
                cursor.execute('SELECT stem, forms FROM noun_forms')
                noun_forms = {}
                for stem, forms_json in cursor.fetchall():
                    noun_forms[stem] = json.loads(forms_json) if forms_json else {}

                conn.close()
                if noun_forms:
                    print(f"✓ Loaded {len(noun_forms)} noun stems from database")
                    return noun_forms
        except Exception as e:
            pass

        # Fallback to JSON
        try:
            all_noun_forms_path = os.path.join(os.path.dirname(__file__), 'all_noun_forms.json')
            with open(all_noun_forms_path, encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load noun forms: {e}")
            return {}

    def load_feedback_data(self):
        """Load user feedback data for learning"""
        try:
            feedback_path = os.path.join(os.path.dirname(__file__), 'user_feedback.json')
            with open(feedback_path, encoding='utf-8') as f:
                self.feedback_data = json.load(f)
        except Exception as e:
            # Initialize empty feedback data
            self.feedback_data = {
                'form_corrections': {},  # form -> list of correct analyses
                'suffix_accuracy': {},    # suffix -> {correct: count, incorrect: count}
                'total_feedback': 0
            }

    def save_feedback_data(self):
        """Save user feedback data"""
        try:
            feedback_path = os.path.join(os.path.dirname(__file__), 'user_feedback.json')
            with open(feedback_path, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return False

    def record_feedback(self, word: str, correct_analysis: Dict, all_analyses: List[Dict]) -> Dict:
        """
        Record user feedback about which analysis is correct

        Args:
            word: The Prakrit word being analyzed
            correct_analysis: The analysis marked as correct by the user
            all_analyses: All analyses that were returned

        Returns:
            Status dict with success/error message
        """
        try:
            # Record the correction
            if word not in self.feedback_data['form_corrections']:
                self.feedback_data['form_corrections'][word] = []

            self.feedback_data['form_corrections'][word].append({
                'correct_analysis': correct_analysis,
                'timestamp': str(__import__('datetime').datetime.now())
            })

            # Update suffix accuracy tracking
            correct_suffix = correct_analysis.get('suffix') or correct_analysis.get('ending')
            if correct_suffix:
                if correct_suffix not in self.feedback_data['suffix_accuracy']:
                    self.feedback_data['suffix_accuracy'][correct_suffix] = {
                        'correct': 0,
                        'incorrect': 0
                    }

                # Mark this suffix as correct
                self.feedback_data['suffix_accuracy'][correct_suffix]['correct'] += 1

                # Mark other suffixes in the analyses as incorrect
                for analysis in all_analyses:
                    if analysis == correct_analysis:
                        continue
                    other_suffix = analysis.get('suffix') or analysis.get('ending')
                    if other_suffix:
                        if other_suffix not in self.feedback_data['suffix_accuracy']:
                            self.feedback_data['suffix_accuracy'][other_suffix] = {
                                'correct': 0,
                                'incorrect': 0
                            }
                        self.feedback_data['suffix_accuracy'][other_suffix]['incorrect'] += 1

            self.feedback_data['total_feedback'] += 1

            # Save to file
            if self.save_feedback_data():
                return {
                    'success': True,
                    'message': 'Feedback recorded successfully',
                    'total_feedback': self.feedback_data['total_feedback']
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to save feedback'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def apply_learned_adjustments(self, analyses: List[Dict]) -> List[Dict]:
        """
        Apply confidence adjustments based on user feedback

        Args:
            analyses: List of analysis dicts

        Returns:
            Analyses with adjusted confidence scores
        """
        for analysis in analyses:
            suffix = analysis.get('suffix') or analysis.get('ending')
            if not suffix:
                continue

            # Check if we have feedback for this suffix
            if suffix in self.feedback_data['suffix_accuracy']:
                stats = self.feedback_data['suffix_accuracy'][suffix]
                correct = stats['correct']
                incorrect = stats['incorrect']
                total = correct + incorrect

                if total > 0:
                    # Calculate accuracy rate
                    accuracy = correct / total

                    # Adjust confidence based on historical accuracy
                    if accuracy > 0.8 and correct >= 3:
                        # High confidence - boost it
                        analysis['confidence'] = min(1.0, analysis['confidence'] + 0.10)
                        analysis['notes'] = analysis.get('notes', []) + [
                            f"Confidence boosted by user feedback ({correct}/{total} correct)"
                        ]
                    elif accuracy < 0.3 and total >= 3:
                        # Low confidence - reduce it
                        analysis['confidence'] = max(0.1, analysis['confidence'] - 0.15)
                        analysis['notes'] = analysis.get('notes', []) + [
                            f"Confidence reduced by user feedback ({correct}/{total} correct)"
                        ]

        # Re-sort by adjusted confidence
        analyses.sort(key=lambda x: x.get('confidence', 0), reverse=True)

        return analyses

    def initialize_suffix_database(self):
        """Initialize comprehensive suffix database with priority and blocking rules"""

        # NOUN SUFFIXES (sorted by length - longest first)
        self.noun_suffixes = {
            # 5-character suffixes
            'hinto': {
                'cases': ['ablative'],
                'numbers': ['singular', 'plural'],
                'genders': ['masculine', 'feminine', 'neuter'],
                'must_precede': ['ā', 'ī', 'ū', 'e'],
                'blocks': ['o', 'to', 'into'],
                'priority': 5,
                'confidence': 0.95
            },
            'hiMto': {  # With anusvara
                'cases': ['ablative'],
                'numbers': ['singular', 'plural'],
                'genders': ['masculine', 'feminine', 'neuter'],
                'must_precede': ['ā', 'ī', 'ū', 'e'],
                'blocks': ['o', 'to', 'iMto', 'into'],
                'priority': 5,
                'confidence': 0.95
            },
            'sunto': {
                'cases': ['ablative'],
                'numbers': ['plural'],
                'genders': ['masculine', 'feminine', 'neuter'],
                'must_precede': ['ā', 'ī', 'ū', 'e'],
                'blocks': ['o', 'to', 'unto'],
                'priority': 5,
                'confidence': 0.95
            },
            'suMto': {  # With anusvara
                'cases': ['ablative'],
                'numbers': ['plural'],
                'genders': ['masculine', 'feminine', 'neuter'],
                'must_precede': ['ā', 'ī', 'ū', 'e'],
                'blocks': ['o', 'to', 'uMto', 'unto'],
                'priority': 5,
                'confidence': 0.95
            },
            # 3-character suffixes
            'hiM': {
                'cases': ['instrumental'],
                'numbers': ['plural'],
                'genders': ['masculine', 'feminine', 'neuter'],
                'must_precede': ['ā', 'ī', 'ū', 'e'],
                'blocks': ['M', 'iM'],
                'priority': 3,
                'confidence': 0.85
            },
            'hi~': {
                'cases': ['instrumental'],
                'numbers': ['plural'],
                'genders': ['masculine', 'feminine', 'neuter'],
                'must_precede': ['ā', 'ī', 'ū', 'e'],
                'blocks': ['~', 'i~'],
                'priority': 3,
                'confidence': 0.85
            },
            'ssa': {
                'cases': ['dative', 'genitive'],
                'numbers': ['singular'],
                'genders': ['masculine', 'neuter'],
                'must_precede': ['a', 'i', 'u'],
                'blocks': ['a', 'sa'],
                'priority': 3,
                'confidence': 0.9
            },
            'mmi': {
                'cases': ['locative'],
                'numbers': ['singular'],
                'genders': ['masculine', 'neuter'],
                'must_precede': ['a', 'i', 'u'],
                'blocks': ['i', 'mi'],
                'priority': 3,
                'confidence': 0.9
            },
            'tto': {
                'cases': ['ablative'],
                'numbers': ['singular', 'plural'],
                'genders': ['masculine', 'feminine', 'neuter'],
                'must_precede': ['a', 'i', 'u', 'ā', 'ī', 'ū'],
                'blocks': ['o', 'to'],
                'priority': 3,
                'confidence': 0.85
            },
            'suM': {
                'cases': ['locative'],
                'numbers': ['plural'],
                'genders': ['masculine', 'feminine', 'neuter'],
                'must_precede': ['ā', 'ī', 'ū', 'e'],
                'blocks': ['M', 'uM'],
                'priority': 3,
                'confidence': 0.85
            },
            'NaM': {
                'cases': ['dative', 'genitive'],  # Dative and genitive plural
                'numbers': ['plural'],
                'genders': ['masculine', 'feminine', 'neuter'],
                'must_precede': ['ā', 'ī', 'ū', 'e'],
                'blocks': ['M', 'aM'],
                'priority': 3,
                'confidence': 0.90
            },
            'iM': {
                'cases': ['nominative', 'accusative'],
                'numbers': ['plural'],
                'genders': ['neuter'],
                'must_precede': ['ā', 'ī', 'ū'],
                'blocks': ['M'],
                'priority': 2,
                'confidence': 0.85
            },
            'i~': {
                'cases': ['nominative', 'accusative'],
                'numbers': ['plural'],
                'genders': ['neuter'],
                'must_precede': ['ā', 'ī', 'ū'],
                'blocks': ['~'],
                'priority': 2,
                'confidence': 0.8
            },
            # 2-character suffixes
            'hi': {
                'cases': ['instrumental'],
                'numbers': ['plural'],
                'genders': ['masculine', 'feminine', 'neuter'],
                'must_precede': ['ā', 'ī', 'ū', 'e'],
                'blocks': ['i'],
                'priority': 2,
                'confidence': 0.85
            },
            'su': {
                'cases': ['locative'],
                'numbers': ['plural'],
                'genders': ['masculine', 'feminine', 'neuter'],
                'must_precede': ['ā', 'ī', 'ū', 'e'],
                'blocks': ['u'],
                'priority': 2,
                'confidence': 0.85
            },
            'Na': {
                'cases': ['dative', 'genitive'],  # Dative and genitive plural
                'numbers': ['plural'],
                'genders': ['masculine', 'feminine', 'neuter'],
                'must_precede': ['ā', 'ī', 'ū', 'e'],
                'blocks': ['a'],
                'priority': 2,
                'confidence': 0.90
            },
            'No': {
                'cases': ['nominative', 'accusative', 'dative', 'genitive'],
                'numbers': ['plural (nom/acc)', 'singular (dat/gen)'],
                'genders': ['masculine'],
                'must_precede': ['i', 'u'],
                'blocks': ['o'],
                'priority': 2,
                'confidence': 0.75
            },
            'Ni': {
                'cases': ['nominative', 'accusative'],
                'numbers': ['plural'],
                'genders': ['neuter'],
                'must_precede': ['ā', 'ī', 'ū'],
                'blocks': ['i'],
                'priority': 2,
                'confidence': 0.8
            },
            # 1-character suffixes (lowest priority)
            'M': {
                'cases': ['accusative', 'nominative'],
                'numbers': ['singular'],
                'genders': ['masculine', 'feminine', 'neuter'],
                'must_precede': [],
                'blocks': [],
                'priority': 1,
                'confidence': 0.7
            },
            'o': {
                'cases': ['nominative', 'vocative', 'ablative'],
                'numbers': ['singular (nom/voc)', 'plural (abl)'],
                'genders': ['masculine', 'feminine'],
                'must_precede': [],
                'blocks': [],
                'priority': 1,
                'confidence': 0.65
            },
            'e': {
                'cases': ['nominative', 'locative', 'vocative'],
                'numbers': ['singular', 'plural'],
                'genders': ['masculine', 'feminine'],
                'must_precede': [],
                'blocks': [],
                'priority': 1,
                'confidence': 0.6
            },
            'a': {
                'cases': ['nominative', 'vocative', 'instrumental'],
                'numbers': ['singular', 'plural'],
                'genders': ['feminine'],
                'must_precede': [],
                'blocks': [],
                'priority': 1,
                'confidence': 0.5
            }
        }

        # VERB SUFFIXES
        self.verb_endings = {
            # Present tense
            'mi': {'person': 'first', 'number': 'singular', 'tense': 'present', 'confidence': 0.95, 'priority': 2},
            'si': {'person': 'second', 'number': 'singular', 'tense': 'present', 'confidence': 0.95, 'priority': 2},
            'se': {'person': 'second', 'number': 'singular', 'tense': 'present', 'confidence': 0.85, 'priority': 2},
            'di': {'person': 'third', 'number': 'singular', 'tense': 'present', 'confidence': 0.95, 'priority': 2},
            'ti': {'person': 'third', 'number': 'singular', 'tense': 'present', 'confidence': 0.9, 'priority': 2},
            'mo': {'person': 'first', 'number': 'plural', 'tense': 'present', 'confidence': 0.95, 'priority': 2},
            'mu': {'person': 'first', 'number': 'plural', 'tense': 'present', 'confidence': 0.85, 'priority': 2},
            'ma': {'person': 'first', 'number': 'plural', 'tense': 'present', 'confidence': 0.85, 'priority': 2},
            'ha': {'person': 'second', 'number': 'plural', 'tense': 'present', 'confidence': 0.95, 'priority': 2},
            'tha': {'person': 'second', 'number': 'plural', 'tense': 'present', 'confidence': 0.9, 'priority': 3},
            'nti': {'person': 'third', 'number': 'plural', 'tense': 'present', 'confidence': 0.95, 'priority': 3},
            'nte': {'person': 'third', 'number': 'plural', 'tense': 'present', 'confidence': 0.85, 'priority': 3},
            'Mti': {'person': 'third', 'number': 'plural', 'tense': 'present', 'confidence': 0.9, 'priority': 3},
            'Mte': {'person': 'third', 'number': 'plural', 'tense': 'present', 'confidence': 0.85, 'priority': 3},

            # Future tense
            'himi': {'person': 'first', 'number': 'singular', 'tense': 'future', 'confidence': 0.95, 'priority': 4},
            'ssaM': {'person': 'first', 'number': 'singular', 'tense': 'future', 'confidence': 0.95, 'priority': 4},
            'hisi': {'person': 'second', 'number': 'singular', 'tense': 'future', 'confidence': 0.95, 'priority': 4},
            'himo': {'person': 'first', 'number': 'plural', 'tense': 'future', 'confidence': 0.95, 'priority': 4},
            'hinti': {'person': 'third', 'number': 'plural', 'tense': 'future', 'confidence': 0.95, 'priority': 5},
            'issanti': {'person': 'third', 'number': 'plural', 'tense': 'future', 'confidence': 0.9, 'priority': 7},

            # Past tense
            'sI': {'person': 'all', 'number': 'all', 'tense': 'past', 'confidence': 0.95, 'priority': 2},
            'hI': {'person': 'all', 'number': 'all', 'tense': 'past', 'confidence': 0.95, 'priority': 2},
            'hIa': {'person': 'all', 'number': 'all', 'tense': 'past', 'confidence': 0.85, 'priority': 3},
            'Ia': {'person': 'all', 'number': 'all', 'tense': 'past', 'confidence': 0.8, 'priority': 2},

            # Short forms (single character - lowest priority)
            'i': {'person': 'third', 'number': 'singular', 'tense': 'present', 'confidence': 0.7, 'priority': 1},
            'e': {'person': 'third', 'number': 'singular', 'tense': 'present', 'confidence': 0.7, 'priority': 1},
        }

    def detect_script(self, text: str) -> str:
        """Detect if input is Devanagari or Harvard-Kyoto"""
        if any('\u0900' <= c <= '\u097F' for c in text):
            return 'Devanagari'
        return 'HK'

    def transliterate_to_hk(self, text: str) -> str:
        """Convert Devanagari to Harvard-Kyoto"""
        if not HAS_AKSHARAMUKHA:
            return text
        if self.detect_script(text) == 'Devanagari':
            return aksh_transliterate.process('Devanagari', 'HK', text)
        return text

    def transliterate_to_devanagari(self, text: str) -> str:
        """Convert Harvard-Kyoto to Devanagari"""
        if not HAS_AKSHARAMUKHA:
            return text
        return aksh_transliterate.process('HK', 'Devanagari', text)

    def normalize_input(self, text: str) -> str:
        """Normalize input text"""
        text = text.strip()
        # Handle anusvara variations
        text = re.sub(r'M(?=[kgcjṭḍtdnpbmyrlvszh])', 'n', text)
        return text

    def validate_prakrit_characters(self, text: str) -> Tuple[bool, str]:
        """Validate if text contains only valid Prakrit characters"""
        hk_text = self.transliterate_to_hk(text)

        # Forbidden characters in Prakrit
        forbidden = {
            'R': 'retroflex R',
            'RR': 'long retroflex R',
            'lR': 'vocalic L',
            'lRR': 'long vocalic L',
            'H': 'visarga (ः)',
            'S': 'retroflex S (ष)'
        }

        for char, desc in forbidden.items():
            if char in hk_text:
                return False, f"Invalid character '{char}' ({desc}) - not found in Prakrit"

        return True, ""

    def check_attested_form(self, word_hk: str, form_type: str) -> Optional[Dict]:
        """Check if form is attested in JSON databases"""
        if form_type == 'verb':
            # Check in all_verb_forms
            for root, forms in self.all_verb_forms.items():
                if word_hk in forms:
                    return {
                        'root': root,
                        'form': word_hk,
                        'source': 'attested_verb',
                        'confidence': 1.0
                    }
        elif form_type == 'noun':
            # Check in all_noun_forms
            for stem, forms in self.all_noun_forms.items():
                if word_hk in forms:
                    found = forms[word_hk]
                    return {
                        'stem': stem,
                        'form': word_hk,
                        'gender': found.get('gender', 'unknown'),
                        'case': found.get('case', 'unknown'),
                        'number': found.get('number', 'unknown'),
                        'source': 'attested_noun',
                        'confidence': 1.0
                    }
        return None

    def find_suffix_matches(self, word: str, suffix_dict: Dict) -> List[Dict]:
        """Find all possible suffix matches with priority and blocking"""
        matches = []

        # Sort suffixes by priority (longest first)
        sorted_suffixes = sorted(suffix_dict.items(),
                                key=lambda x: (x[1].get('priority', 0), len(x[0])),
                                reverse=True)

        blocked_suffixes = set()

        for suffix, info in sorted_suffixes:
            # Skip if blocked by higher priority match
            if suffix in blocked_suffixes:
                continue

            if word.endswith(suffix):
                base = word[:-len(suffix)] if len(suffix) > 0 else word

                # Validate context (preceding vowel requirements)
                if info.get('must_precede'):
                    if not base or base[-1] not in info['must_precede']:
                        continue

                # Add blocks from this match
                if info.get('blocks'):
                    blocked_suffixes.update(info['blocks'])

                match = {
                    'suffix': suffix,
                    'base': base,
                    'info': info,
                    'priority': info.get('priority', 0)
                }
                matches.append(match)

        return sorted(matches, key=lambda x: x['priority'], reverse=True)

    def is_valid_prakrit_stem(self, stem: str) -> bool:
        """
        Validate if a stem follows Prakrit phonological rules

        Key Prakrit phonological constraints:
        1. NO consonant-ending words - all Prakrit words must end in vowels
        2. Valid ending vowels: a, ā, i, ī, u, ū, e, o
        3. Anusvara (M/ṃ) is allowed as final

        Args:
            stem: The reconstructed stem to validate

        Returns:
            True if valid Prakrit stem, False otherwise
        """
        if not stem or len(stem) < 1:
            return False

        # Get last character
        last_char = stem[-1]

        # Valid Prakrit word endings (all must be vowels or anusvara)
        valid_endings = {'a', 'ā', 'A', 'i', 'ī', 'I', 'u', 'ū', 'U', 'e', 'o', 'M', 'ṃ', '~'}

        # Check if ends with valid character
        if last_char not in valid_endings:
            return False

        return True

    def reconstruct_noun_stem(self, base: str, suffix: str, gender: str) -> str:
        """Reconstruct noun stem from base and suffix"""
        if not base:
            return ''

        # For suffixes attached to long vowel or 'e' forms
        if suffix in ['hinto', 'hiMto', 'sunto', 'suMto', 'hi', 'hiM', 'hi~', 'su', 'suM']:
            if base.endswith('e'):
                return base[:-1] + 'a'  # a-stem
            elif base.endswith('ā'):
                if gender == 'feminine':
                    return base  # ā-stem feminine
                return base[:-1] + 'a'  # masculine
            elif base.endswith('ī'):
                if gender == 'feminine':
                    return base  # ī-stem feminine
                return base[:-1] + 'i'  # masculine
            elif base.endswith('ū'):
                if gender == 'feminine':
                    return base  # ū-stem feminine
                return base[:-1] + 'u'  # masculine

        # For suffixes attached directly to stem
        elif suffix in ['ssa', 'mmi', 'No']:
            if base.endswith(('a', 'i', 'u')):
                return base
            return base + 'a'  # default

        # For Na/NaM (context-dependent)
        elif suffix in ['Na', 'NaM']:
            if base.endswith('e'):
                return base[:-1] + 'a'  # instrumental singular
            elif base.endswith(('ā', 'ī', 'ū')):
                vowel_map = {'ā': 'a', 'ī': 'i', 'ū': 'u'}
                return base[:-1] + vowel_map[base[-1]]

        # For tto
        elif suffix == 'tto':
            if not base.endswith(('a', 'i', 'u', 'ā', 'ī', 'ū')):
                return base + 'a'
            return base

        # Single character suffixes
        elif suffix == 'o':
            return base + 'a'  # nominative masculine
        elif suffix == 'e':
            return base + 'a'  # converted from a
        elif suffix == 'M':
            return base  # accusative

        return base

    def analyze_as_noun(self, word_hk: str) -> List[Dict]:
        """Analyze word as a Prakrit noun"""
        results = []

        # First check if attested
        attested = self.check_attested_form(word_hk, 'noun')
        if attested:
            results.append(attested)
            return results

        # Find suffix matches
        suffix_matches = self.find_suffix_matches(word_hk, self.noun_suffixes)

        for match in suffix_matches[:10]:  # Limit to top 10 matches
            suffix = match['suffix']
            base = match['base']
            info = match['info']

            # Try each gender possibility
            for gender in info.get('genders', []):
                stem = self.reconstruct_noun_stem(base, suffix, gender)

                if not stem or len(stem) < 2:
                    continue

                # Validate Prakrit phonology: no consonant-ending stems
                if not self.is_valid_prakrit_stem(stem):
                    continue

                # Create analysis for each case possibility
                for case in info.get('cases', []):
                    for number in info.get('numbers', []):
                        confidence = info.get('confidence', 0.5)

                        # Boost confidence for good stem matches
                        if stem.endswith(('a', 'i', 'u', 'ā', 'ī', 'ū')):
                            confidence += 0.05

                        analysis = {
                            'form': word_hk,
                            'stem': stem,
                            'suffix': suffix,
                            'case': case,
                            'number': number,
                            'gender': gender,
                            'type': 'noun',
                            'source': 'ending_based_guess',
                            'confidence': min(confidence, 1.0),
                            'notes': [f"Ending-based analysis: suffix '{suffix}' suggests {case} {number}"]
                        }
                        results.append(analysis)

        return results

    def apply_vowel_sandhi_reverse(self, base: str) -> List[Tuple[str, str]]:
        """
        Reverse vowel sandhi transformations to find potential verb roots.
        Returns list of (potential_root, sandhi_rule) tuples.

        Prakrit vowel sandhi rules:
        - ī (I) + consonant suffix → e (NI + mo → Nemo)
        - ū (U) + consonant suffix → o (BhU + ti → Bhoti)
        - ai/e → A/ā in some contexts
        - o → U/ū in some contexts
        """
        candidates = []

        if not base:
            return candidates

        # Rule 1: e → I (ī)
        # Example: "Ne" from "Nemo" → "NI" root
        if base.endswith('e'):
            i_root = base[:-1] + 'I'
            candidates.append((i_root, 'e→ī sandhi'))
            # Also try short i
            i_short_root = base[:-1] + 'i'
            candidates.append((i_short_root, 'e→i sandhi'))

        # Rule 2: o → U (ū)
        # Example: "Bho" from "Bhoti" → "BhU" root
        if base.endswith('o'):
            u_root = base[:-1] + 'U'
            candidates.append((u_root, 'o→ū sandhi'))
            # Also try short u
            u_short_root = base[:-1] + 'u'
            candidates.append((u_short_root, 'o→u sandhi'))

        # Rule 3: a → A (ā)
        if base.endswith('a'):
            a_root = base[:-1] + 'A'
            candidates.append((a_root, 'a→ā extension'))

        # Rule 4: Also check for base + A/I/U directly (no sandhi)
        for vowel in ['A', 'I', 'U', 'a', 'i', 'u']:
            candidates.append((base + vowel, f'vowel-ending +{vowel}'))

        return candidates

    def analyze_as_verb(self, word_hk: str) -> List[Dict]:
        """Analyze word as a Prakrit verb with vowel sandhi support"""
        results = []

        # First check if attested
        attested = self.check_attested_form(word_hk, 'verb')
        if attested:
            # Get grammatical info from the attested root
            root = attested['root']
            results.append({
                'form': word_hk,
                'root': root,
                'type': 'verb',
                'source': 'attested_verb',
                'confidence': 1.0,
                'notes': [f"Form attested for root '{root}'"]
            })
            return results

        # Find ending matches
        ending_matches = self.find_suffix_matches(word_hk, self.verb_endings)

        for match in ending_matches[:10]:  # Limit to top 10
            ending = match['suffix']
            base = match['base']
            info = match['info']

            # Collect ALL potential roots (both direct and sandhi)
            root_candidates = []

            # Strategy 1: Direct substring matches
            for i in range(len(base), 0, -1):
                subroot = base[:i]
                if subroot in self.verb_roots:
                    root_candidates.append({
                        'root': subroot,
                        'method': 'direct_match',
                        'sandhi_note': None,
                        'confidence_boost': 0.15
                    })

            # Strategy 2: Vowel sandhi reversals
            sandhi_candidates = self.apply_vowel_sandhi_reverse(base)
            for candidate_root, sandhi_rule in sandhi_candidates:
                if candidate_root in self.verb_roots:
                    root_candidates.append({
                        'root': candidate_root,
                        'method': 'sandhi_reversal',
                        'sandhi_note': sandhi_rule,
                        'confidence_boost': 0.20  # Slightly higher for sandhi (more sophisticated)
                    })
                # Also try partial matches for compound roots
                for i in range(len(candidate_root), 0, -1):
                    if candidate_root[:i] in self.verb_roots:
                        root_candidates.append({
                            'root': candidate_root[:i],
                            'method': 'sandhi_reversal_partial',
                            'sandhi_note': sandhi_rule,
                            'confidence_boost': 0.12
                        })

            # If no attested root found, use the base as a guess
            if not root_candidates:
                root_candidates.append({
                    'root': base,
                    'method': 'unattested_guess',
                    'sandhi_note': None,
                    'confidence_boost': -0.1
                })

            # Create analysis for each root candidate
            for candidate in root_candidates:
                # Validate Prakrit phonology: no consonant-ending roots
                if not self.is_valid_prakrit_stem(candidate['root']):
                    continue

                confidence = info.get('confidence', 0.5) + candidate['confidence_boost']

                if candidate['sandhi_note']:
                    note = f"Root '{candidate['root']}' found via vowel sandhi ({candidate['sandhi_note']})"
                    source = 'sandhi_analysis'
                elif candidate['method'] == 'direct_match':
                    note = f"Root '{candidate['root']}' found in verb list"
                    source = 'ending_based_guess'
                else:
                    note = "Root not attested - guessed from form"
                    source = 'ending_based_guess'

                analysis = {
                    'form': word_hk,
                    'root': candidate['root'],
                    'ending': ending,
                    'tense': info.get('tense'),
                    'person': info.get('person'),
                    'number': info.get('number'),
                    'type': 'verb',
                    'source': source,
                    'confidence': min(max(confidence, 0.1), 1.0),
                    'notes': [f"Ending-based analysis: {note}"]
                }
                results.append(analysis)

        return results

    def parse(self, text: str) -> Dict:
        """Main parsing function - unified analysis"""
        # Validate input
        is_valid, error_msg = self.validate_prakrit_characters(text)
        if not is_valid:
            return {
                'success': False,
                'error': error_msg,
                'suggestions': ['Check input for forbidden characters', 'Use proper Prakrit transliteration']
            }

        # Normalize and transliterate
        original_script = self.detect_script(text)
        word_hk = self.transliterate_to_hk(self.normalize_input(text))

        # Analyze as both noun and verb
        noun_analyses = self.analyze_as_noun(word_hk)
        verb_analyses = self.analyze_as_verb(word_hk)

        # Combine and sort by confidence
        all_analyses = noun_analyses + verb_analyses
        all_analyses.sort(key=lambda x: x.get('confidence', 0), reverse=True)

        # Apply learned adjustments from user feedback
        all_analyses = self.apply_learned_adjustments(all_analyses)

        # Add dictionary meanings if dictionary is loaded
        if self.dictionary:
            for analysis in all_analyses:
                lookup_word = None

                if analysis.get('type') == 'noun':
                    lookup_word = analysis.get('stem')
                elif analysis.get('type') == 'verb':
                    lookup_word = analysis.get('root')

                if lookup_word:
                    try:
                        entries = self.dictionary.lookup(lookup_word, script='HK')
                        if entries:
                            entry = entries[0]
                            analysis['dictionary'] = {
                                'headword_devanagari': entry.get('headword_devanagari', ''),
                                'sanskrit_equivalent': entry.get('sanskrit_equivalent', []),
                                'meanings': [m.get('definition', '') for m in entry.get('meanings', [])[:3]],
                                'is_desya': entry.get('is_desya', False)
                            }
                    except:
                        pass  # Dictionary lookup is optional

        # Add Devanagari forms if input was HK
        if original_script == 'HK':
            for analysis in all_analyses:
                if 'form' in analysis:
                    analysis['devanagari'] = self.transliterate_to_devanagari(analysis['form'])
                if 'stem' in analysis:
                    analysis['stem_devanagari'] = self.transliterate_to_devanagari(analysis['stem'])
                if 'root' in analysis:
                    analysis['root_devanagari'] = self.transliterate_to_devanagari(analysis['root'])

        return {
            'success': True,
            'original_form': text,
            'hk_form': word_hk,
            'script': original_script,
            'analyses': all_analyses[:15],  # Return top 15 analyses
            'total_found': len(all_analyses)
        }

# Initialize parser
parser = PrakritUnifiedParser()

# Flask routes (only if Flask is available)
if HAS_FLASK:
    @app.route('/', methods=['GET'])
    def index():
        return render_template('unified_analyzer.html')

    @app.route('/api/parse', methods=['POST', 'OPTIONS'])
    def api_parse():
        """API endpoint for parsing"""
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Methods', 'POST')
            return response

        # Try to get data from multiple sources
        try:
            data = request.get_json(force=True, silent=True)
        except:
            data = None

        if not data:
            data = request.form.to_dict()

        if not data:
            try:
                data = {'form': request.data.decode('utf-8')}
            except:
                data = {}

        form = data.get('form', '')

        if not form or not form.strip():
            return jsonify({
                'success': False,
                'error': 'Please provide a Prakrit word or form'
            }), 400

        try:
            result = parser.parse(form)
            response = jsonify(result)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Parser error: {str(e)}'
            }), 500

    @app.route('/api/analyze', methods=['POST', 'OPTIONS'])
    def api_analyze():
        """Backward compatibility with old /analyze endpoint"""
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Methods', 'POST')
            return response

        # Try to get data from multiple sources
        try:
            data = request.get_json(force=True, silent=True)
        except:
            data = None

        if not data:
            data = request.form.to_dict()

        if not data:
            try:
                data = {'verb_form': request.data.decode('utf-8')}
            except:
                data = {}

        verb_form = data.get('verb_form', '')

        if not verb_form:
            return jsonify({
                'success': False,
                'error': 'Please provide a verb form'
            }), 400

        try:
            result = parser.parse(verb_form)

            # Transform to old format
            if result['success']:
                response = jsonify({
                    'results': result['analyses']
                })
            else:
                response = jsonify({
                    'error': result.get('error'),
                    'suggestions': result.get('suggestions', [])
                })

            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        except Exception as e:
            return jsonify({
                'error': str(e)
            }), 500

    @app.route('/api/feedback', methods=['POST', 'OPTIONS'])
    def api_feedback():
        """API endpoint for submitting user feedback"""
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Methods', 'POST')
            return response

        # Try to get data from multiple sources
        try:
            data = request.get_json(force=True, silent=True)
        except:
            data = None

        if not data:
            data = request.form.to_dict()

        word = data.get('word', '')
        correct_analysis_index = data.get('correct_index')
        all_analyses = data.get('all_analyses', [])

        if not word or correct_analysis_index is None or not all_analyses:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: word, correct_index, all_analyses'
            }), 400

        try:
            correct_analysis_index = int(correct_analysis_index)
            if correct_analysis_index < 0 or correct_analysis_index >= len(all_analyses):
                return jsonify({
                    'success': False,
                    'error': 'Invalid correct_index'
                }), 400

            correct_analysis = all_analyses[correct_analysis_index]

            # Record the feedback
            result = parser.record_feedback(word, correct_analysis, all_analyses)

            response = jsonify(result)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/feedback/stats', methods=['GET'])
    def api_feedback_stats():
        """Get feedback statistics"""
        try:
            stats = {
                'total_feedback': parser.feedback_data['total_feedback'],
                'unique_forms': len(parser.feedback_data['form_corrections']),
                'suffix_stats': parser.feedback_data['suffix_accuracy']
            }

            response = jsonify(stats)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

        except Exception as e:
            return jsonify({
                'error': str(e)
            }), 500

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        # CLI mode
        word = sys.argv[1]
        result = parser.parse(word)

        if result['success']:
            print(f"\n=== Analysis for: {result['original_form']} ===")
            print(f"Harvard-Kyoto: {result['hk_form']}")
            print(f"Script: {result['script']}")
            print(f"\nFound {result['total_found']} possible analyses (showing top {len(result['analyses'])}):\n")

            for i, analysis in enumerate(result['analyses'], 1):
                print(f"\n--- Analysis {i} (confidence: {analysis['confidence']:.2f}) ---")
                print(f"Type: {analysis.get('type', 'unknown')}")

                if analysis.get('type') == 'noun':
                    print(f"Stem: {analysis.get('stem', 'unknown')}")
                    print(f"Suffix: {analysis.get('suffix', 'unknown')}")
                    print(f"Gender: {analysis.get('gender', 'unknown')}")
                    print(f"Case: {analysis.get('case', 'unknown')}")
                    print(f"Number: {analysis.get('number', 'unknown')}")
                elif analysis.get('type') == 'verb':
                    print(f"Root: {analysis.get('root', 'unknown')}")
                    print(f"Ending: {analysis.get('ending', 'unknown')}")
                    print(f"Tense: {analysis.get('tense', 'unknown')}")
                    print(f"Person: {analysis.get('person', 'unknown')}")
                    print(f"Number: {analysis.get('number', 'unknown')}")

                print(f"Source: {analysis.get('source', 'unknown')}")
                if analysis.get('notes'):
                    print(f"Notes: {'; '.join(analysis['notes'])}")
        else:
            print(f"\nError: {result.get('error')}")
            if result.get('suggestions'):
                print("\nSuggestions:")
                for suggestion in result['suggestions']:
                    print(f"  - {suggestion}")

        sys.exit(0 if result['success'] else 1)
    else:
        # Server mode
        if not HAS_FLASK:
            print("Error: Flask is not installed. Install with: pip install flask")
            print("For CLI usage, provide a word as argument: python unified_parser.py <word>")
            sys.exit(1)

        port = int(os.environ.get("PORT", 5000))
        app.run(host='0.0.0.0', port=port, debug=True)
