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

    def __init__(self):
        self.load_data()
        self.initialize_suffix_database()

    def load_data(self):
        """Load verb and noun data from JSON files"""
        # Load verb data
        try:
            verbs1_path = os.path.join(os.path.dirname(__file__), 'verbs1.json')
            with open(verbs1_path, encoding='utf-8') as f:
                verbs1_data = json.load(f)
                self.verb_roots = set(verbs1_data.values())
        except Exception as e:
            print(f"Warning: Could not load verbs1.json: {e}")
            self.verb_roots = set()

        # Load all verb forms
        try:
            all_verb_forms_path = os.path.join(os.path.dirname(__file__), 'all_verb_forms.json')
            with open(all_verb_forms_path, encoding='utf-8') as f:
                self.all_verb_forms = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load all_verb_forms.json: {e}")
            self.all_verb_forms = {}

        # Load all noun forms
        try:
            all_noun_forms_path = os.path.join(os.path.dirname(__file__), 'all_noun_forms.json')
            with open(all_noun_forms_path, encoding='utf-8') as f:
                self.all_noun_forms = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load all_noun_forms.json: {e}")
            self.all_noun_forms = {}

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
                'confidence': 0.9
            },
            'sunto': {
                'cases': ['ablative'],
                'numbers': ['plural'],
                'genders': ['masculine', 'feminine', 'neuter'],
                'must_precede': ['ā', 'ī', 'ū', 'e'],
                'blocks': ['o', 'to', 'unto'],
                'priority': 5,
                'confidence': 0.9
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
                'cases': ['instrumental', 'dative', 'genitive'],
                'numbers': ['singular (inst)', 'plural (dat/gen)'],
                'genders': ['masculine', 'feminine', 'neuter'],
                'must_precede': ['ā', 'ī', 'ū', 'e'],
                'blocks': ['M', 'aM'],
                'priority': 3,
                'confidence': 0.8
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
                'cases': ['instrumental', 'dative', 'genitive'],
                'numbers': ['singular (inst)', 'plural (dat/gen)'],
                'genders': ['masculine', 'feminine', 'neuter'],
                'must_precede': ['ā', 'ī', 'ū', 'e'],
                'blocks': ['a'],
                'priority': 2,
                'confidence': 0.8
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

    def reconstruct_noun_stem(self, base: str, suffix: str, gender: str) -> str:
        """Reconstruct noun stem from base and suffix"""
        if not base:
            return ''

        # For suffixes attached to long vowel or 'e' forms
        if suffix in ['hinto', 'sunto', 'hi', 'hiM', 'hi~', 'su', 'suM']:
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

    def analyze_as_verb(self, word_hk: str) -> List[Dict]:
        """Analyze word as a Prakrit verb"""
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

            # Try to find matching root
            potential_root = None
            for i in range(len(base), 0, -1):
                subroot = base[:i]
                if subroot in self.verb_roots:
                    potential_root = subroot
                    break

            confidence = info.get('confidence', 0.5)

            # Adjust confidence based on root match
            if potential_root:
                confidence += 0.15
                note = f"Root '{potential_root}' found in verb list"
            else:
                confidence -= 0.1
                potential_root = base
                note = "Root not attested - guessed from form"

            analysis = {
                'form': word_hk,
                'root': potential_root,
                'ending': ending,
                'tense': info.get('tense'),
                'person': info.get('person'),
                'number': info.get('number'),
                'type': 'verb',
                'source': 'ending_based_guess',
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
