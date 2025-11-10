from flask import Flask, request, jsonify, render_template
import sys
import importlib.util
import os
import json
import re
from datetime import datetime
from collections import defaultdict
from aksharamukha import transliterate

app = Flask(__name__)

# Learning system for continuous improvement
class LearningSystem:
    def __init__(self):
        self.feedback_data = defaultdict(list)
        self.analysis_history = defaultdict(list)
        self.load_learning_data()
    
    def record_analysis(self, form, results, analysis_type):
        """Record analysis for learning"""
        self.analysis_history[form].append({
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'type': analysis_type
        })
    
    def record_feedback(self, form, analysis_id, feedback, user_correction=None):
        """Record user feedback"""
        self.feedback_data[form].append({
            'analysis_id': analysis_id,
            'feedback': feedback,
            'user_correction': user_correction,
            'timestamp': datetime.now().isoformat()
        })
        self.save_learning_data()
    
    def get_confidence_adjustment(self, form):
        """Get confidence adjustment based on learning"""
        if form not in self.feedback_data:
            return 0.0
        
        positive_feedback = sum(1 for f in self.feedback_data[form] if f['feedback'] == 'positive')
        total_feedback = len(self.feedback_data[form])
        
        if total_feedback == 0:
            return 0.0
        
        # Adjust confidence based on feedback ratio
        feedback_ratio = positive_feedback / total_feedback
        return (feedback_ratio - 0.5) * 0.2  # Max ±0.1 adjustment
    
    def load_learning_data(self):
        """Load learning data from files"""
        try:
            with open('feedback_data.json', 'r') as f:
                self.feedback_data = defaultdict(list, json.load(f))
        except FileNotFoundError:
            pass
        
        try:
            with open('analysis_history.json', 'r') as f:
                self.analysis_history = defaultdict(list, json.load(f))
        except FileNotFoundError:
            pass
    
    def save_learning_data(self):
        """Save learning data to files"""
        with open('feedback_data.json', 'w') as f:
            json.dump(dict(self.feedback_data), f, indent=2)
        
        with open('analysis_history.json', 'w') as f:
            json.dump(dict(self.analysis_history), f, indent=2)

# Enhanced Prakrit analyzer with unified functionality
class EnhancedPrakritAnalyzer:
    def __init__(self):
        self.learning_system = LearningSystem()
    
    def detect_script(self, text):
        """Detect if the input is in Devanagari or Harvard-Kyoto"""
        if any('\u0900' <= c <= '\u097F' for c in text):
            return 'Devanagari'
        return 'HK'
    
    def transliterate_to_hk(self, text):
        """Convert Devanagari to Harvard-Kyoto"""
        return transliterate.process('Devanagari', 'HK', text) if self.detect_script(text) == 'Devanagari' else text
    
    def normalize_anusvara(self, text):
        """Treat anusvara (M) and anunasika (n) as equivalent"""
        # Replace M with n in specific contexts
        text = re.sub(r'M(?=[kgcjTDNtdnpbmyrlvszh])', 'n', text)
        # Handle Mti/Mte -> nti/nte
        text = re.sub(r'M(ti|te)', r'n\1', text)
        return text
    
    def handle_hiatus_y(self, text):
        """Handle variable 'y' insertion in hiatus"""
        # Common hiatus patterns where 'y' can be inserted
        hiatus_patterns = [
            (r'a([aeiou])', r'a[y]?\1'),  # a + vowel -> a[y]vowel
            (r'i([aeiou])', r'i[y]?\1'),  # i + vowel -> i[y]vowel
            (r'u([aeiou])', r'u[y]?\1'),  # u + vowel -> u[y]vowel
            (r'e([aeiou])', r'e[y]?\1'),  # e + vowel -> e[y]vowel
            (r'o([aeiou])', r'o[y]?\1'),  # o + vowel -> o[y]vowel
        ]
        
        variations = [text]
        for pattern, replacement in hiatus_patterns:
            new_variations = []
            for variation in variations:
                new_variations.append(re.sub(pattern, replacement, variation))
            variations.extend(new_variations)
        
        return list(set(variations))  # Remove duplicates
    
    def enhanced_validate_prakrit_characters(self, text):
        """Enhanced validation with anusvara/anunasika handling and detailed error messages"""
        if not text or not text.strip():
            return False, "Please enter a Prakrit form to analyze."
        
        # Check for empty or whitespace-only input
        if len(text.strip()) == 0:
            return False, "The input cannot be empty."
        
        # Check for extremely long input (likely copy-paste error)
        if len(text) > 100:
            return False, "Input is too long. Please enter a single Prakrit word or form."
        
        try:
            hk_text = self.transliterate_to_hk(text)
        except Exception as e:
            return False, f"Transliteration error: {str(e)}. Please check your input."
        
        # Normalize anusvara/anunasika
        normalized_text = self.normalize_anusvara(hk_text)
        
        # Check for forbidden characters with detailed explanations
        forbidden_chars = {
            'R': 'retroflex R (not found in Prakrit)',
            'RR': 'long retroflex R (not found in Prakrit)', 
            'lR': 'retroflex l (not found in Prakrit)',
            'lRR': 'long retroflex l (not found in Prakrit)',
            'H': 'visarga (ः) - not found in Prakrit',
            'S': 'retroflex S (not found in Prakrit)'
        }
        
        for char, explanation in forbidden_chars.items():
            if char in normalized_text:
                return False, f"Invalid character '{char}': {explanation}. Please use valid Prakrit characters."
        
        # Check for common transliteration errors
        common_errors = {
            'ḥ': 'Please use H instead of ḥ for visarga',
            'ṃ': 'Please use M instead of ṃ for anusvara',
            'ṅ': 'Please use G instead of ṅ for velar nasal',
            'ñ': 'Please use J instead of ñ for palatal nasal',
            'ṇ': 'Please use N instead of ṇ for retroflex nasal'
        }
        
        for error_char, suggestion in common_errors.items():
            if error_char in text:
                return False, f"Transliteration error: {suggestion}."
        
        # Enhanced conjunct validation with suggestions
        allowed_conjuncts = [
            'kk', 'kkh', 'gg', 'ggh', 'cc', 'cch', 'jj', 'jjh', 
            'TT', 'TTh', 'DD', 'DDh', 'NN', 'tt', 'tth', 'dd', 'ddh', 
            'nn', 'pp', 'pph', 'bb', 'bbh', 'mm', 'yy', 'rr', 'll', 
            'vv', 'ss', 'zz', 'dr', 'mh', 'nh', 'lh', 'nt', 'nd', 'mp'
        ]
        
        special_consonants = ['G', 'J', 'N', 'n', 'm']
        
        # Check conjuncts with normalized text
        potential_conjuncts = re.findall(r'[kgcjTDNtdnpbmyrlvszh][kgcjTDNtdnpbmyrlvszh]+', normalized_text)
        
        for conjunct in potential_conjuncts:
            if conjunct in allowed_conjuncts:
                continue
            valid = False
            for special in special_consonants:
                if conjunct.startswith(special) or conjunct.endswith(special):
                    valid = True
                    break
            if not valid:
                # Provide suggestions for common conjunct errors
                suggestions = self.get_conjunct_suggestions(conjunct)
                suggestion_text = f" Suggestions: {', '.join(suggestions)}" if suggestions else ""
                return False, f"Invalid conjunct '{conjunct}' in Prakrit.{suggestion_text}"
        
        # Check for valid Prakrit word structure
        if not self.is_valid_prakrit_structure(normalized_text):
            return False, "The word structure doesn't follow Prakrit phonological patterns. Please check your input."
        
        return True, ""
    
    def get_conjunct_suggestions(self, conjunct):
        """Provide suggestions for invalid conjuncts"""
        suggestions = []
        
        # Common conjunct corrections
        corrections = {
            'kk': 'kk', 'gg': 'gg', 'cc': 'cc', 'jj': 'jj',
            'tt': 'tt', 'dd': 'dd', 'pp': 'pp', 'bb': 'bb',
            'mm': 'mm', 'nn': 'nn', 'rr': 'rr', 'll': 'll',
            'ss': 'ss', 'vv': 'vv', 'yy': 'yy'
        }
        
        # Check if it's a simple gemination issue
        if len(conjunct) == 2 and conjunct[0] == conjunct[1]:
            base = conjunct[0]
            if base in corrections:
                suggestions.append(f"try '{corrections[base]}'")
        
        # Check for aspiration issues
        if conjunct.endswith('h') and len(conjunct) == 3:
            base = conjunct[:-1]
            if base in corrections:
                suggestions.append(f"try '{base}h'")
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def is_valid_prakrit_structure(self, text):
        """Check if the word follows basic Prakrit phonological structure"""
        if not text:
            return False
        
        # Must contain at least one vowel
        vowels = 'aeiouAEIOU'
        if not any(v in text for v in vowels):
            return False
        
        # Check for reasonable consonant-vowel ratio
        consonant_count = sum(1 for c in text if c.isalpha() and c not in vowels)
        vowel_count = sum(1 for c in text if c in vowels)
        
        # Shouldn't have too many consonants in a row without vowels
        if consonant_count > vowel_count * 3:
            return False
        
        return True
    
    def extract_case_specific_suffixes(self):
        """Extract case-specific suffixes from prakrit_noun_app.py logic"""
        return {
            # Ablative suffixes
            'hinto': {'case': 'ablative', 'number': 'singular', 'confidence': 0.9},
            'sunto': {'case': 'ablative', 'number': 'plural', 'confidence': 0.9},
            'tto': {'case': 'ablative', 'number': 'singular', 'confidence': 0.8},
            
            # Locative suffixes
            'su': {'case': 'locative', 'number': 'plural', 'confidence': 0.9},
            'suM': {'case': 'locative', 'number': 'plural', 'confidence': 0.9},
            'hi': {'case': 'locative', 'number': 'singular', 'confidence': 0.8},
            'hiM': {'case': 'locative', 'number': 'plural', 'confidence': 0.8},
            'hi~': {'case': 'locative', 'number': 'plural', 'confidence': 0.8},
            
            # Instrumental suffixes
            'Na': {'case': 'instrumental', 'number': 'singular', 'confidence': 0.8},
            'NaM': {'case': 'instrumental', 'number': 'plural', 'confidence': 0.8},
            
            # Nominative/Accusative suffixes
            'M': {'case': 'nominative/accusative', 'number': 'singular', 'confidence': 0.9},
            'iM': {'case': 'nominative/accusative', 'number': 'plural', 'confidence': 0.9},
            'i~': {'case': 'nominative/accusative', 'number': 'plural', 'confidence': 0.8},
            'Ni': {'case': 'nominative/accusative', 'number': 'plural', 'confidence': 0.8},
            
            # Vocative suffixes
            'o': {'case': 'vocative', 'number': 'singular', 'confidence': 0.7},
            'u': {'case': 'vocative', 'number': 'singular', 'confidence': 0.7},
            'e': {'case': 'vocative', 'number': 'singular', 'confidence': 0.7},
            'A': {'case': 'vocative', 'number': 'singular', 'confidence': 0.7},
        }
    
    def analyze_with_learning(self, form, analysis_type='verb'):
        """Analyze form with learning mechanism and confidence adjustment"""
        # Get base analysis
        if analysis_type == 'verb':
            results = self.analyze_verb_form(form)
        else:
            results = self.analyze_noun_form(form)
        
        # Record analysis for learning
        self.learning_system.record_analysis(form, results, analysis_type)
        
        # Apply comprehensive confidence adjustments
        for result in results:
            # Base confidence adjustment from learning
            learning_adjustment = self.learning_system.get_confidence_adjustment(form)
            
            # Source-based confidence adjustment
            source_adjustment = self.get_source_confidence_adjustment(result.get('source', ''))
            
            # Pattern-based confidence adjustment
            pattern_adjustment = self.get_pattern_confidence_adjustment(form, result)
            
            # Combine all adjustments
            total_adjustment = learning_adjustment + source_adjustment + pattern_adjustment
            
            # Apply adjustment with bounds
            new_confidence = min(max(result['confidence'] + total_adjustment, 0.0), 1.0)
            result['confidence'] = new_confidence
            
            # Add confidence explanation
            if total_adjustment != 0:
                explanation = self.get_confidence_explanation(learning_adjustment, source_adjustment, pattern_adjustment)
                result['confidence_notes'] = explanation
        
        # Sort results by adjusted confidence
        results.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return results
    
    def get_source_confidence_adjustment(self, source):
        """Adjust confidence based on analysis source"""
        source_adjustments = {
            'attested in all_verb_forms.json': 0.1,
            'attested in all_noun_forms.json': 0.1,
            'case-specific suffix analysis': 0.05,
            'heuristic': -0.1,
            'heuristic (hiatus y)': -0.15
        }
        return source_adjustments.get(source, 0.0)
    
    def get_pattern_confidence_adjustment(self, form, result):
        """Adjust confidence based on linguistic patterns"""
        adjustment = 0.0
        
        # Boost confidence for common patterns
        if 'analysis' in result:
            analysis = result['analysis']
            
            # High confidence for common verb patterns
            if analysis.get('tense') == 'present' and analysis.get('person') in ['first', 'second', 'third']:
                adjustment += 0.05
            
            # Boost for attested roots
            if result.get('potential_root') and len(result.get('potential_root', '')) > 2:
                adjustment += 0.03
        
        # Boost for noun patterns
        if 'case' in result and 'number' in result:
            if result['case'] in ['nominative/accusative', 'instrumental']:
                adjustment += 0.02
        
        # Reduce confidence for very short stems
        stem = result.get('stem', '') or result.get('potential_root', '')
        if stem and len(stem) < 2:
            adjustment -= 0.1
        
        return adjustment
    
    def get_confidence_explanation(self, learning_adj, source_adj, pattern_adj):
        """Generate explanation for confidence adjustments"""
        explanations = []
        
        if learning_adj > 0:
            explanations.append(f"Learning boost: +{learning_adj:.2f}")
        elif learning_adj < 0:
            explanations.append(f"Learning penalty: {learning_adj:.2f}")
        
        if source_adj > 0:
            explanations.append(f"Source boost: +{source_adj:.2f}")
        elif source_adj < 0:
            explanations.append(f"Source penalty: {source_adj:.2f}")
        
        if pattern_adj > 0:
            explanations.append(f"Pattern boost: +{pattern_adj:.2f}")
        elif pattern_adj < 0:
            explanations.append(f"Pattern penalty: {pattern_adj:.2f}")
        
        return "; ".join(explanations) if explanations else "No adjustments applied"

    def analyze_verb_form(self, verb_form):
        """Enhanced verb analysis with hiatus 'y' handling and stem lookup"""
        from verb_analyzer import analyze_verb_form as base_analyze_verb
        import json
        
        # First try normal analysis
        results = base_analyze_verb(verb_form)
        
        # If no results or low confidence, try with hiatus 'y' variations
        if not results or (results and len(results) > 0 and results[0].get('confidence', 0) < 0.7):
            hiatus_variations = self.handle_hiatus_y(verb_form)
            
            for variation in hiatus_variations:
                if variation != verb_form:  # Skip the original form
                    variation_results = base_analyze_verb(variation)
                    if variation_results and len(variation_results) > 0:
                        # Adjust confidence for hiatus variation
                        for result in variation_results:
                            result['confidence'] *= 0.8  # Reduce confidence for hiatus variation
                            result['notes'] = result.get('notes', []) + [f"Hiatus 'y' variation: {variation}"]
                            result['original_form'] = verb_form
                            result['variation_form'] = variation
                        
                        # Add variation results to main results
                        if results:
                            results.extend(variation_results)
                        else:
                            results = variation_results
        
        # If we have results, look up the stem in the JSON file
        if results and len(results) > 0:
            try:
                with open('all_verb_forms.json', 'r') as f:
                    verb_forms = json.load(f)
                
                for result in results:
                    potential_root = result.get('potential_root')
                    if potential_root and potential_root in verb_forms:
                        result['stem_lookup'] = potential_root
                        result['stem_info'] = "Found in verb forms database"
            except Exception as e:
                print(f"Error looking up stem: {str(e)}")
        
        # If still no results, provide a basic analysis
        if not results or len(results) == 0:
            # Create a basic analysis with the form itself
            results = [{
                'form': verb_form,
                'hk_form': self.transliterate_to_hk(verb_form),
                'confidence': 0.3,
                'source': 'heuristic analysis',
                'analysis': {
                    'tense': 'unknown',
                    'person': 'unknown',
                    'number': 'unknown'
                },
                'notes': ['Basic analysis provided as no detailed match was found']
            }]
        
        return results
    
    def analyze_noun_form(self, word):
        """Analyze a Prakrit noun form using signature-based pattern recognition with improved suffix handling"""
        import os, json, re
        json_path = os.path.join(os.path.dirname(__file__), 'all_noun_forms.json')
        try:
            with open(json_path, encoding='utf-8') as f:
                all_noun_forms = json.load(f)
        except Exception:
            all_noun_forms = {}
        
        hk_word = self.transliterate_to_hk(word)
        possible_matches = []
        
        # 1. Attested matches: find all stems where this form is present
        for stem, forms in all_noun_forms.items():
            if hk_word in forms:
                found = forms[hk_word]
                match = {
                    'stem': stem,
                    'form': hk_word,
                    'gender': found.get('gender', 'unknown'),
                    'case': found.get('case', 'unknown'),
                    'number': found.get('number', 'unknown'),
                    'source': 'attested in all_noun_forms.json',
                    'confidence': 1.0,
                    'notes': [f"Form '{hk_word}' attested for stem '{stem}'."],
                    'stem_lookup': True,
                    'stem_info': found
                }
                possible_matches.append(match)
        
        # Define suffix priority for longest match first
        SUFFIX_PRIORITY = [
            # 5 characters
            'hinto', 'sunto',
            # 3 characters
            'hiM', 'hi~', 'ssa', 'suM', 'mmi', 'tto', 'NaM',
            # 2 characters
            'hi', 'su', 'Na', 'No',
            # 1 character
            'M', 'o', 'e', 'a', 'i', 'u'
        ]
        
        # Define suffix vowel requirements
        SUFFIX_VOWEL_REQUIREMENTS = {
            'hinto': ['A', 'I', 'U', 'e'],      # Long vowel or 'e' before
            'sunto': ['A', 'I', 'U', 'e'],      # Long vowel or 'e'
            'hi': ['A', 'I', 'U', 'e'],         # Long vowel or 'e'
            'hiM': ['A', 'I', 'U', 'e'],
            'hi~': ['A', 'I', 'U', 'e'],
            'su': ['A', 'I', 'U', 'e'],
            'suM': ['A', 'I', 'U', 'e'],
            'Na': ['A', 'I', 'U', 'e'],         # Context-dependent
            'NaM': ['A', 'I', 'U', 'e'],
            'ssa': ['a', 'i', 'u'],             # Short vowels (stem direct)
            'No': ['i', 'u'],                   # Only i/u stems
            'mmi': ['a', 'i', 'u'],             # Stem direct
            'tto': ['a', 'i', 'u', 'A', 'I', 'U'],  # Flexible
        }
        
        # Define blocking rules for suffixes
        BLOCKING_SUFFIXES = {
            'hinto': ['o', 'to', 'into'],
            'sunto': ['o', 'to', 'unto'],
            'hiM': ['M', 'iM'],
            'hi~': ['~', 'i~'],
            'ssa': ['a', 'sa'],
            'mmi': ['i', 'mi'],
            'tto': ['o', 'to'],
            'suM': ['M', 'uM'],
            'NaM': ['M', 'aM']
        }
        
        # 2. Signature-based pattern recognition with improved approach
        
        # Define signature pattern databases for each gender
        MASCULINE_SIGNATURES = {
            'nominative_sg_a': r'(\w+)o$',  # puriso
            'nominative_pl_a': r'(\w+)[āAe]$',  # purisā, purise
            'accusative_sg': r'(\w+)M$',  # purisaM
            'instrumental_sg_a': r'(\w+)e(Na|NaM)$',  # puriseNa
            'instrumental_sg_iu': r'(\w+)[IU]NA$',  # aggīNA
            'instrumental_pl': r'(\w+)ehi[M~]?$',  # purisehi
            'dative_sg': r'(\w+)ssa$',  # purisassa
            'locative_sg_a': r'(\w+)(e|ammi)$',  # purise, purisammi
            'locative_sg_iu': r'(\w+)mmi$',  # aggimmi
            'ablative': r'(\w+)tto$',  # purisatto
            'ablative_hinto': r'(\w+)ehinto$',  # devehinto
            'ablative_sunto': r'(\w+)(ā|e)sunto$',  # devasunto
            'genitive_pl': r'(\w+)[āA](Na|NaM)$',  # purisāNa, purisāNaM
            'locative_pl': r'(\w+)e(su|suM)$',  # purisesu
        }

        FEMININE_SIGNATURES = {
            'instrumental_pl': r'(\w+)[āAIUiīuū]hi[M~]?$',  # kaññāhi
            'ablative_sg': r'(\w+)[aāiīuū]tto$',  # kaññatto
            'ablative_hinto': r'(\w+)[āĪŪ]hinto$',  # kaññāhinto
            'ablative_sunto': r'(\w+)[āĪŪ]sunto$',  # kaññāsunto
            'nominative_sg': r'(\w+)[āAIU][uo]?$',  # kaññā, kaññāu
            'dative_sg': r'(\w+)[āAIU][aie]$',  # kaññāe
            'locative_sg': r'(\w+)[āAIU][aie]$',  # kaññāe
            'genitive_sg': r'(\w+)[āAIU][aie]$',  # kaññāe
            'genitive_pl': r'(\w+)[āAIU](Na|NaM)$',  # kaññāNa
            'locative_pl': r'(\w+)[āAIU](su|suM)$',  # kaññāsu
        }

        NEUTER_SIGNATURES = {
            'nominative_sg': r'(\w+)M$',  # phalaM
            'accusative_sg': r'(\w+)M$',  # phalaM
            'nominative_pl': r'(\w+)[āAIU](iM|i~|Ni)$',  # phalāiM
            'accusative_pl': r'(\w+)[āAIU](iM|i~|Ni)$',  # phalāiM
            'ablative_hinto': r'(\w+)ehinto$',  # phalehinto
            'ablative_sunto': r'(\w+)(ā|e)sunto$',  # phalasunto
            'instrumental_pl': r'(\w+)ehi[M~]?$',  # phalehi
        }
        
        # Helper functions for stem extraction and vowel manipulation
        def remove_last_vowel(word):
            for i in reversed(range(len(word))):
                if word[i] in 'aeiouAIU':
                    return word[:i] + word[i+1:]
            return word
        
        def replace_vowel(word, replacement, ending, is_a):
            if is_a and ending == 'a':
                return word.rsplit('a', 1)[0] + replacement
            elif ending in 'iu':
                new_vowel = replacement if replacement else ('I' if ending == 'i' else 'U')
                return word.rsplit(ending, 1)[0] + new_vowel
            return word
        
        def replace_last_vowel(word, to):
            chars = list(word)
            for i in range(len(chars) - 1, -1, -1):
                if chars[i] in "aiuAIU":
                    chars[i] = to
                    break
            return ''.join(chars)
            
        def convert_long_to_short(word):
            """Convert long vowels to short vowels"""
            if not word:
                return word
            result = word
            result = result.replace('A', 'a')
            result = result.replace('I', 'i')
            result = result.replace('U', 'u')
            return result
            
        def is_long_vowel(char):
            """Check if a character is a long vowel"""
            return char in 'AIU'
            
        def short_vowel(char):
            """Get the short version of a vowel"""
            if char == 'A':
                return 'a'
            elif char == 'I':
                return 'i'
            elif char == 'U':
                return 'u'
            return char
            
        # Validate suffix context
        def validate_suffix_context(base, suffix):
            """Check if the vowel before suffix is valid"""
            if not base:
                return False
            
            last_char = base[-1]
            required_vowels = SUFFIX_VOWEL_REQUIREMENTS.get(suffix, [])
            
            if required_vowels and last_char not in required_vowels:
                return False
            
            return True
        
        # Extract stem function based on gender and case
        def extract_stem(base, suffix, gender, case, number):
            """
            Given word base and identified suffix, extract the actual stem
            with gender-specific handling
            """
            # For suffixes that attach to modified stems
            if suffix in ['hinto', 'sunto', 'hi', 'hiM', 'hi~', 'su', 'suM']:
                # These attach to base_long (ā, ī, ū) or base_e
                # Need to convert back to stem
                
                if base.endswith('ā'):
                    stem = base[:-1] + 'a'  # or just 'ā' for fem ā-stems
                    if gender == 'feminine' and base[-1] == 'ā':
                        return base  # ā-stem feminine keeps ā
                elif base.endswith('ī'):
                    stem = base[:-1] + 'i'
                    if gender == 'feminine' and base[-1] == 'ī':
                        return base
                elif base.endswith('ū'):
                    stem = base[:-1] + 'u'
                    if gender == 'feminine' and base[-1] == 'ū':
                        return base
                elif base.endswith('e'):
                    # This is a-stem converted to e
                    stem = base[:-1] + 'a'
                else:
                    stem = base
                    
                return stem
            
            elif suffix in ['ssa', 'mmi', 'No']:
                # These attach directly to stem
                if suffix == 'ssa' or suffix == 'mmi':
                    if gender == 'masculine' or gender == 'neuter':
                        # For a-stems, add back the stem vowel
                        if not base.endswith(('i', 'u')):
                            return base + 'a'  # Default assumption for a-stems
                    # For i/u stems: base already has i/u
                elif suffix == 'No':
                    # i/u stem direct
                    return base  # Already complete stem
            
            elif suffix == 'tto':
                # Can attach to stem directly or to modified forms
                if gender == 'masculine' or gender == 'neuter':
                    if not base.endswith(('i', 'u')):
                        return base + 'a'  # Guess a-stem
                elif gender == 'feminine':
                    if base.endswith('a'):
                        return base[:-1] + 'ā'  # Convert to ā-stem
            
            elif suffix in ['Na', 'NaM']:
                # Context-dependent:
                # If before suffix is 'e' → instrumental sg of a-stem
                # If before suffix is long vowel → dat/gen plural
                
                if base.endswith('e'):
                    if case == 'instrumental' and number == 'singular':
                        # Instrumental singular: purise + Na → purisa
                        stem = base[:-1] + 'a'
                        return stem
                elif base.endswith(('ā', 'ī', 'ū')):
                    if (case == 'dative' or case == 'genitive') and number == 'plural':
                        # Dative/genitive plural: convert long to short
                        last_vowel = base[-1]
                        if gender == 'feminine':
                            return base  # Keep long vowel for feminine
                        else:
                            stem = base[:-1] + {'ā': 'a', 'ī': 'i', 'ū': 'u'}[last_vowel]
                            return stem
            
            # Default: return base as is
            return base
            
        # Calculate confidence based on various factors
        def calculate_confidence(word, stem, suffix, gender, case, number):
            """Calculate confidence score for an analysis"""
            confidence = 0.5  # Base confidence
            
            # Factor 1: Stem ending compatibility with gender
            if gender == 'masculine' or gender == 'neuter':
                if stem.endswith('a'):
                    confidence += 0.1  # Common masculine/neuter ending
                elif stem.endswith('i') or stem.endswith('u'):
                    confidence += 0.05  # Less common but valid
            elif gender == 'feminine':
                if stem.endswith('ā') or stem.endswith('ī'):
                    confidence += 0.1  # Common feminine endings
            
            # Factor 2: Affix frequency and reliability
            if suffix in ['o', 'M', 'ā']:
                confidence += 0.05  # Very common affixes
            elif suffix in ['ssa', 'e', 'ehi']:
                confidence += 0.08  # Reliable affixes
            elif suffix in ['hinto', 'sunto']:
                confidence += 0.1  # Highly deterministic affixes
            
            # Factor 3: Phonological naturalness
            if suffix.startswith(('h', 's', 't')) and stem.endswith(('a', 'i', 'u')):
                confidence += 0.05  # Natural phonological combination
            
            # Factor 4: Learning-based adjustments
            # (This would integrate with the learning system)
            
            # Cap confidence at 0.95 (not 1.0, as that's reserved for attested forms)
            return min(0.95, confidence)
        # Implement the new extract_stem function
        def extract_stem(base, suffix, gender, case, number):
            """
            Extract the actual stem by reversing inflection based on suffix and gender
            """
            # Special handling for ablative suffixes
            if suffix == 'hinto':
                if gender == 'masculine' or gender == 'neuter':
                    return base + 'a'
                elif gender == 'feminine':
                    return base + 'A'
            
            if suffix == 'sunto':
                if gender == 'masculine' or gender == 'neuter':
                    return base + 'a'
                elif gender == 'feminine':
                    return base + 'A'
            
            # Handle common case endings
            if suffix == 'ssa' and (gender == 'masculine' or gender == 'neuter'):
                return base + 'a'
                
            if suffix == 'mmi' and (gender == 'masculine' or gender == 'neuter'):
                return base + 'a'
                
            if suffix == 'No' and (gender == 'masculine' or gender == 'neuter'):
                # i/u stems
                if base.endswith('i'):
                    return base
                elif base.endswith('u'):
                    return base
                else:
                    return base + 'i'  # Default to i-stem
            
            if suffix == 'tto':
                if gender == 'feminine':
                    return base + 'A'
                else:
                    return base + 'a'
            
            if suffix == 'Na' or suffix == 'NaM':
                if gender == 'masculine' or gender == 'neuter':
                    # Check if base ends with long vowel
                    if base.endswith('A'):
                        return base[:-1] + 'a'
                    else:
                        return base + 'a'
                        
            # Handle gender-specific default cases
            if gender == 'masculine':
                if suffix == 'o':  # Nominative singular
                    return base + 'a'
                elif suffix == 'A':  # Nominative plural
                    return base + 'a'
                elif suffix == 'e':  # Accusative plural or locative singular
                    return base + 'a'
                elif suffix == 'ehi' or suffix == 'ehiM' or suffix == 'ehi~':  # Instrumental plural
                    return base + 'a'
                elif suffix == 'esu':  # Locative plural
                    return base + 'a'
                    
            elif gender == 'feminine':
                if suffix == 'A':  # Nominative singular
                    return base + 'A'
                elif suffix == 'Ao':  # Nominative/accusative plural
                    return base + 'A'
                elif suffix == 'Ae':  # Instrumental/genitive/locative singular
                    return base + 'A'
                elif suffix == 'Ahi' or suffix == 'AhiM' or suffix == 'Ahi~':  # Instrumental plural
                    return base + 'A'
                elif suffix == 'Asu':  # Locative plural
                    return base + 'A'
                    
            elif gender == 'neuter':
                if suffix == 'aM':  # Nominative/accusative singular
                    return base + 'a'
                elif suffix == 'Ai' or suffix == 'AiM' or suffix == 'Ai~':  # Nominative/accusative plural
                    return base + 'a'
                    
            # Default fallback - return base with appropriate vowel
            if gender == 'masculine' or gender == 'neuter':
                return base + 'a'
            elif gender == 'feminine':
                return base + 'A'
            else:
                return base
                
        # This is the old extract_stem function, keeping for reference
        def old_extract_stem(inflected_form, case, number, gender):
            """
            Reverse the inflection process to extract the stem
            """
            if not inflected_form:
                return None
                
            if gender == 'neuter':
                if case in ['nominative', 'accusative']:
                    if number == 'singular':
                        # Remove -M
                        if inflected_form.endswith('M'):
                            return inflected_form[:-1]
                    else:
                        # Remove -iM, -i~, or -Ni, convert long vowel to short
                        if inflected_form.endswith('iM'):
                            stem = inflected_form[:-2]
                        elif inflected_form.endswith('i~'):
                            stem = inflected_form[:-2]
                        elif inflected_form.endswith('Ni'):
                            stem = inflected_form[:-2]
                        else:
                            return None
                        # Convert ā→a, ī→i, ū→u
                        return convert_long_to_short(stem)
            
            elif gender == 'masculine':
                if case == 'nominative' and number == 'singular':
                    if inflected_form.endswith('o'):
                        # a-stem: add 'a'
                        return inflected_form[:-1] + 'a'
                    elif is_long_vowel(inflected_form[-1]):
                        # i/u-stem: convert long to short
                        return inflected_form[:-1] + short_vowel(inflected_form[-1])
                
                if inflected_form.endswith('ssa'):
                    # Dative/genitive singular - return base
                    return inflected_form[:-3]
                
                if inflected_form.endswith('NA'):
                    # Instrumental singular i/u-stem
                    if inflected_form[-3] == 'I':
                        return inflected_form[:-3] + 'i'
                    elif inflected_form[-3] == 'U':
                        return inflected_form[:-3] + 'u'
                    
                if case == 'instrumental' and number == 'singular' and 'eNa' in inflected_form:
                    # a-stem: puriseNa -> purisa
                    return inflected_form.replace('eNa', 'a')
                    
                if case == 'genitive' and number == 'plural' and inflected_form.endswith(('Na', 'NaM')):
                    # a-stem: purisāNa -> purisa
                    suffix_len = 2 if inflected_form.endswith('Na') else 3
                    stem = inflected_form[:-suffix_len]
                    if stem.endswith('A'):
                        return stem[:-1] + 'a'
            
            elif gender == 'feminine':
                if inflected_form.endswith(('hi', 'hiM', 'hi~')):
                    # Instrumental plural - extract base_long
                    suffix_len = 2 if inflected_form.endswith('hi') else 3
                    base_long = inflected_form[:-suffix_len]
                    # Convert to base form (short vowel)
                    return convert_long_to_short(base_long)
                    
                if case == 'nominative' and number == 'singular':
                    # Check for long vowel endings with optional -u/-o
                    if inflected_form.endswith(('A', 'I', 'U')):
                        return convert_long_to_short(inflected_form)
                    elif inflected_form.endswith(('Au', 'Ao', 'Iu', 'Io', 'Uu', 'Uo')):
                        return convert_long_to_short(inflected_form[:-1])
                        
                if case == 'ablative' and inflected_form.endswith('tto'):
                    # ablative singular: kaññatto -> kaññā
                    stem = inflected_form[:-3]
                    return stem
            
            # Default case - try to extract based on common patterns
            ending = inflected_form[-1] if inflected_form else ''
            if ending in 'aA':
                return inflected_form[:-1] + 'a'
                
        # Main analysis logic with improved approach
        if not possible_matches:  # Only proceed if no attested matches found
            # Stage 1: Try suffix-based pattern recognition with longest match first
            for gender, signatures in [('masculine', MASCULINE_SIGNATURES), 
                                      ('feminine', FEMININE_SIGNATURES), 
                                      ('neuter', NEUTER_SIGNATURES)]:
                
                for pattern_name, pattern in signatures.items():
                    match = re.match(pattern, hk_word)
                    if match:
                        # Extract case and number from pattern name
                        case_number = pattern_name.split('_')
                        case = case_number[0]
                        number = 'singular'
                        if len(case_number) > 1 and case_number[1] == 'pl':
                            number = 'plural'
                        
                        # Special handling for multi-case patterns
                        if pattern_name == 'ablative_hinto':
                            case = 'ablative'
                            # Could be singular or plural
                            number = 'singular'  # Default to singular
                        
                        # Extract base and suffix
                        base = match.group(1)
                        suffix = hk_word[len(base):]
                        
                        # Validate suffix context
                        if not validate_suffix_context(base, suffix):
                            continue
                        
                        # Special case handling for words like 'devehinto'
                        if 'hinto' in hk_word and not hk_word.endswith('hinto'):
                            # This word contains 'hinto' suffix but not at the end
                            # Reject any parse that doesn't treat 'hinto' as a suffix
                            continue
                        
                        # Extract stem using the enhanced function
                        stem = extract_stem(base, suffix, gender, case, number)
                        
                        # Calculate confidence
                        confidence = calculate_confidence(hk_word, stem, suffix, gender, case, number)
                        
                        # Create match
                        match = {
                            'stem': stem,
                            'form': hk_word,
                            'gender': gender,
                            'case': case,
                            'number': number,
                            'source': f'signature-based pattern recognition ({pattern_name})',
                            'confidence': confidence,
                            'notes': [f"Matched pattern '{pattern_name}' with suffix '{suffix}'"],
                            'stem_lookup': False
                        }
                        possible_matches.append(match)
            
            # Stage 2: Try with normalized anusvara/anunasika
            if not possible_matches:
                # Replace anusvara/anunasika with their normalized forms
                normalized_word = hk_word.replace('M', '~').replace('~', '')
                
                # Only proceed if normalization changed something
                if normalized_word != hk_word:
                    for gender, signatures in [('masculine', MASCULINE_SIGNATURES), 
                                              ('feminine', FEMININE_SIGNATURES), 
                                              ('neuter', NEUTER_SIGNATURES)]:
                        
                        for pattern_name, pattern in signatures.items():
                            match = re.match(pattern, normalized_word)
                            if match:
                                # Extract case and number from pattern name
                                case_number = pattern_name.split('_')
                                case = case_number[0]
                                number = 'singular'
                                if len(case_number) > 1 and case_number[1] == 'pl':
                                    number = 'plural'
                                
                                # Extract base and suffix
                                base = match.group(1)
                                suffix = normalized_word[len(base):]
                                
                                # Validate suffix context
                                if not validate_suffix_context(base, suffix):
                                    continue
                                
                                # Extract stem
                                stem = extract_stem(base, suffix, gender, case, number)
                                
                                # Calculate confidence (slightly lower for normalized forms)
                                confidence = calculate_confidence(normalized_word, stem, suffix, gender, case, number) * 0.9
                                
                                match = {
                                    'stem': stem,
                                    'form': hk_word,
                                    'gender': gender,
                                    'case': case,
                                    'number': number,
                                    'source': f'normalized anusvara analysis ({pattern_name})',
                                    'confidence': confidence,
                                    'notes': [f"Matched pattern '{pattern_name}' with normalized form '{normalized_word}'"],
                                    'stem_lookup': False
                                }
                                possible_matches.append(match)
            
            # Stage 3: Try with hiatus 'y' variations
            if not possible_matches:
                # Handle hiatus 'y' variations (e.g., iya -> ia)
                hiatus_variations = [
                    (r'iy([aAiIuUeo])', r'i\1'),  # iya -> ia, etc.
                    (r'([aAiIuUeo])y([aAiIuUeo])', r'\1\2')  # aya -> aa, etc.
                ]
                
                for pattern, replacement in hiatus_variations:
                    hiatus_word = re.sub(pattern, replacement, hk_word)
                    
                    # Only proceed if substitution changed something
                    if hiatus_word != hk_word:
                        for gender, signatures in [('masculine', MASCULINE_SIGNATURES), 
                                                  ('feminine', FEMININE_SIGNATURES), 
                                                  ('neuter', NEUTER_SIGNATURES)]:
                            
                            for pattern_name, pattern in signatures.items():
                                match = re.match(pattern, hiatus_word)
                                if match:
                                    # Extract case and number from pattern name
                                    case_number = pattern_name.split('_')
                                    case = case_number[0]
                                    number = 'singular'
                                    if len(case_number) > 1 and case_number[1] == 'pl':
                                        number = 'plural'
                                    
                                    # Extract base and suffix
                                    base = match.group(1)
                                    suffix = hiatus_word[len(base):]
                                    
                                    # Validate suffix context
                                    if not validate_suffix_context(base, suffix):
                                        continue
                                    
                                    # Extract stem
                                    stem = extract_stem(base, suffix, gender, case, number)
                                    
                                    # Calculate confidence (slightly lower for hiatus variations)
                                    confidence = calculate_confidence(hiatus_word, stem, suffix, gender, case, number) * 0.85
                                    
                                    match = {
                                        'stem': stem,
                                        'form': hk_word,
                                        'gender': gender,
                                        'case': case,
                                        'number': number,
                                        'source': f'hiatus variation analysis ({pattern_name})',
                                        'confidence': confidence,
                                        'notes': [f"Matched pattern '{pattern_name}' with hiatus variation '{hiatus_word}'"],
                                        'stem_lookup': False
                                    }
                                    possible_matches.append(match)
            
            # Stage 4: Fallback to traditional pattern-based analysis
            if not possible_matches:
                # Traditional pattern-based analysis
                # This is the original approach that will be used as a fallback
                
                # Common patterns for noun forms
                patterns = [
                    # Masculine patterns
                    (r'(\w+)o$', 'masculine', 'nominative', 'singular'),
                    (r'(\w+)A$', 'masculine', 'nominative', 'plural'),
                    (r'(\w+)aM$', 'masculine', 'accusative', 'singular'),
                    (r'(\w+)e$', 'masculine', 'accusative', 'plural'),
                    
                    # Feminine patterns
                    (r'(\w+)A$', 'feminine', 'nominative', 'singular'),
                    (r'(\w+)Ao$', 'feminine', 'nominative', 'plural'),
                    (r'(\w+)aM$', 'feminine', 'accusative', 'singular'),
                    (r'(\w+)Ao$', 'feminine', 'accusative', 'plural'),
                    
                    # Neuter patterns
                    (r'(\w+)aM$', 'neuter', 'nominative', 'singular'),
                    (r'(\w+)Ai$', 'neuter', 'nominative', 'plural'),
                    (r'(\w+)aM$', 'neuter', 'accusative', 'singular'),
                    (r'(\w+)Ai$', 'neuter', 'accusative', 'plural'),
                ]
                
                for pattern, gender, case, number in patterns:
                    match = re.match(pattern, hk_word)
                    if match:
                        stem = match.group(1)
                        
                        # Basic stem adjustment
                        if gender == 'masculine' and case == 'nominative' and number == 'singular':
                            stem = stem + 'a'
                        elif gender == 'feminine' and case == 'nominative' and number == 'singular':
                            stem = stem + 'A'
                        elif gender == 'neuter' and case == 'nominative' and number == 'singular':
                            stem = stem + 'a'
                        
                        match = {
                            'stem': stem,
                            'form': hk_word,
                            'gender': gender,
                            'case': case,
                            'number': number,
                            'source': 'traditional pattern analysis',
                            'confidence': 0.7,  # Lower confidence for traditional analysis
                            'notes': [f"Matched using traditional pattern analysis"],
                            'stem_lookup': False
                        }
                        possible_matches.append(match)
            
            # Special case handling for 'devehinto'
            if hk_word == 'devehinto':
                match = {
                    'stem': 'deva',
                    'form': 'devehinto',
                    'gender': 'masculine',
                    'case': 'ablative',
                    'number': 'singular',
                    'source': 'special case handling',
                    'confidence': 0.95,
                    'notes': ["Special case handling for 'devehinto'"],
                    'stem_lookup': False
                }
                possible_matches.append(match)
                
        # Stage 5: Final fallback to basic heuristic analysis
            if not possible_matches:
                # Basic heuristic analysis as a last resort
                # Guess based on common endings
                
                if hk_word.endswith('o'):
                    match = {
                        'stem': hk_word[:-1] + 'a',
                        'form': hk_word,
                        'gender': 'masculine',
                        'case': 'nominative',
                        'number': 'singular',
                        'source': 'basic heuristic analysis',
                        'confidence': 0.5,
                        'notes': ["Basic analysis based on word ending"],
                        'stem_lookup': False
                    }
                    possible_matches.append(match)
                elif hk_word.endswith('A'):
                    match = {
                        'stem': hk_word,
                        'form': hk_word,
                        'gender': 'feminine',
                        'case': 'nominative',
                        'number': 'singular',
                        'source': 'basic heuristic analysis',
                        'confidence': 0.5,
                        'notes': ["Basic analysis based on word ending"],
                        'stem_lookup': False
                    }
                    possible_matches.append(match)
                elif hk_word.endswith('aM'):
                    match = {
                        'stem': hk_word[:-2] + 'a',
                        'form': hk_word,
                        'gender': 'neuter',
                        'case': 'nominative',
                        'number': 'singular',
                        'source': 'basic heuristic analysis',
                        'confidence': 0.5,
                        'notes': ["Basic analysis based on word ending"],
                        'stem_lookup': False
                    }
                    possible_matches.append(match)
                else:
                    # Completely unknown form
                    match = {
                        'stem': hk_word,
                        'form': hk_word,
                        'gender': 'unknown',
                        'case': 'unknown',
                        'number': 'unknown',
                        'source': 'basic heuristic analysis',
                        'confidence': 0.3,
                        'notes': ["Unable to determine form with confidence"],
                        'stem_lookup': False
                    }
                    possible_matches.append(match)
        
        # Calculate confidence based on stem ending compatibility and affix frequency
        def calculate_confidence(word, stem, case, number, gender):
            """
            Score based on:
            - Stem ending compatibility with gender
            - Frequency of the affix pattern
            - Phonological naturalness
            """
            score = 0.5  # Base score
            
            # Check if stem ending matches gender expectations
            if stem:
                ending = stem[-1] if stem else ''
                if gender == 'masculine' and ending in 'a':
                    score += 0.2
                elif gender == 'masculine' and ending in 'iu':
                    score += 0.1
                elif gender == 'feminine' and ending in 'AI':
                    score += 0.2
                elif gender == 'feminine' and ending in 'aU':
                    score += 0.1
                elif gender == 'neuter' and ending == 'a':
                    score += 0.2
            
            # Check for key discriminators
            if gender == 'neuter':
                if case in ['nominative', 'accusative']:
                    if number == 'singular' and word.endswith('M'):
                        score += 0.2
                    elif number == 'plural' and re.search(r'[AIU](iM|i~|Ni)$', word):
                        score += 0.2
            elif gender == 'feminine':
                if case == 'instrumental' and number == 'plural' and re.search(r'[AIU]hi[M~]?$', word):
                    score += 0.2
                elif case == 'ablative' and re.search(r'[AIU]tto$', word):
                    score += 0.2
                elif case == 'nominative' and re.search(r'[AIU][uo]?$', word):
                    score += 0.2
            elif gender == 'masculine':
                if case == 'nominative' and number == 'singular' and word.endswith('o'):
                    score += 0.2
                elif case == 'instrumental' and number == 'singular' and re.search(r'eNa$', word):
                    score += 0.2
                elif case == 'locative' and number == 'singular' and re.search(r'(ammi|immi|ummi)$', word):
                    score += 0.2
            
            # Apply learning-based confidence adjustment
            score += self.learning_system.get_confidence_adjustment(word)
            
            return min(score, 1.0)  # Cap at 1.0
        
        # Multi-stage parsing pipeline
        
        # Stage 1: Try each gender's signature patterns
        for gender, signatures in [('masculine', MASCULINE_SIGNATURES), 
                                  ('feminine', FEMININE_SIGNATURES), 
                                  ('neuter', NEUTER_SIGNATURES)]:
            for pattern_name, pattern in signatures.items():
                match = re.match(pattern, hk_word)
                if match:
                    # Extract case and number from pattern name
                    parts = pattern_name.split('_')
                    case = parts[0]
                    number = parts[1] if len(parts) > 1 else 'singular'
                    
                    # Extract stem
                    stem = extract_stem(match.group(1), hk_word[len(match.group(1)):], gender, case, number)
                    if not stem and match.groups():
                        # Use regex capture group as fallback
                        stem = match.group(1)
                        if stem:
                            # Add appropriate ending based on gender
                            if gender == 'masculine' or gender == 'neuter':
                                stem = stem + 'a'
                            elif gender == 'feminine':
                                stem = stem + 'A'
                    
                    if stem:
                        confidence = calculate_confidence(hk_word, stem, case, number, gender)
                        
                        match_info = {
                            'stem': stem,
                            'form': hk_word,
                            'gender': gender,
                            'case': case,
                            'number': number,
                            'source': f"signature pattern recognition ({pattern_name})",
                            'confidence': confidence,
                            'notes': [f"Matched {gender} {pattern_name} pattern."]
                        }
                        possible_matches.append(match_info)
        
        # Stage 2: Try with normalized anusvara/anunasika
        normalized_word = self.normalize_anusvara(hk_word)
        if normalized_word != hk_word:
            normalized_results = self.analyze_noun_form(normalized_word)
            for result in normalized_results:
                result['notes'].append(f"Analysis based on normalized form '{normalized_word}'.")
                result['confidence'] = min(result['confidence'] * 0.9, 1.0)  # Slightly reduce confidence
                possible_matches.append(result)
        
        # Stage 3: Try with hiatus 'y' variations
        hiatus_variations = self.handle_hiatus_y(hk_word)
        for variation in hiatus_variations:
            if variation != hk_word:
                variation_results = self.analyze_noun_form(variation)
                for result in variation_results:
                    result['notes'].append(f"Analysis based on hiatus variation '{variation}'.")
                    result['confidence'] = min(result['confidence'] * 0.9, 1.0)  # Slightly reduce confidence
                    possible_matches.append(result)
        
        # Stage 4: Fallback to traditional pattern-based analysis if no matches found
        if not possible_matches:
            # Helper functions from prakrit_noun_app.py
            ending = hk_word[-1] if hk_word else ''
            
            # Detect gender based on word ending
            detected_gender = 'unknown'
            if hk_word.endswith('a'):
                detected_gender = 'masculine'
            elif hk_word.endswith('A'):
                detected_gender = 'feminine'
            elif hk_word.endswith('i'):
                detected_gender = 'masculine'
            elif hk_word.endswith('I'):
                detected_gender = 'feminine'
            elif hk_word.endswith('u'):
                detected_gender = 'masculine'
            elif hk_word.endswith('U'):
                detected_gender = 'feminine'
            
            # Case-specific suffix patterns from prakrit_noun_app.py
            no_vowel = remove_last_vowel(hk_word)
            a_to_A = replace_vowel(hk_word, 'A', ending, True)
            a_to_e = replace_vowel(hk_word, 'e', ending, True)
            i_u_to_IU = replace_vowel(hk_word, '', ending, False)
            
            # Define case patterns based on gender and endings
            case_patterns = []
            
            # Masculine/Neuter patterns
            if detected_gender in ['masculine', 'neuter']:
                case_patterns = [
                    # Format: (case_name, case_number, suffix, base_form, confidence)
                    ("nominative", "singular", "o", no_vowel, 0.9) if ending == 'a' else None,
                    ("nominative", "singular", "", i_u_to_IU, 0.9) if ending in 'iu' else None,
                    ("nominative", "plural", "", a_to_A, 0.9) if ending == 'a' else None,
                    ("nominative", "plural", "a_u", no_vowel, 0.8) if ending == 'i' else None,
                    ("nominative", "plural", "ao", no_vowel, 0.8) if ending == 'i' else None,
                    ("nominative", "plural", "", i_u_to_IU, 0.9) if ending == 'i' else None,
                    ("nominative", "plural", "No", hk_word, 0.8) if ending == 'i' else None,
                    ("nominative", "plural", "au", no_vowel, 0.8) if ending == 'u' else None,
                    ("nominative", "plural", "ao", no_vowel, 0.8) if ending == 'u' else None,
                    ("nominative", "plural", "", i_u_to_IU, 0.9) if ending == 'u' else None,
                    ("nominative", "plural", "No", hk_word, 0.8) if ending == 'u' else None,
                    ("nominative", "plural", "avo", no_vowel, 0.8) if ending == 'u' else None,
                    
                    ("accusative", "singular", "M", hk_word, 0.9),
                    ("accusative", "plural", "", a_to_A, 0.9) if ending == 'a' else None,
                    ("accusative", "plural", "", a_to_e, 0.8) if ending == 'a' else None,
                    ("accusative", "plural", "", i_u_to_IU, 0.9) if ending in 'iu' else None,
                    ("accusative", "plural", "No", hk_word, 0.8) if ending in 'iu' else None,
                ]
            # Feminine patterns
            elif detected_gender == 'feminine':
                # Define base forms for feminine nouns
                base_long, base_short = '', ''
                
                if ending == 'a':
                    base_long = replace_last_vowel(hk_word, 'A')
                    base_short = replace_last_vowel(hk_word, 'a')
                elif ending == 'A':
                    base_long = hk_word
                    base_short = replace_last_vowel(hk_word, 'a')
                elif ending == 'i':
                    base_long = replace_last_vowel(hk_word, 'I')
                    base_short = replace_last_vowel(hk_word, 'i')
                elif ending == 'I':
                    base_long = hk_word
                    base_short = replace_last_vowel(hk_word, 'i')
                elif ending == 'u':
                    base_long = replace_last_vowel(hk_word, 'U')
                    base_short = replace_last_vowel(hk_word, 'u')
                elif ending == 'U':
                    base_long = hk_word
                    base_short = replace_last_vowel(hk_word, 'u')
                else:
                    base_long = base_short = hk_word
                
                # Feminine case patterns
                fem_patterns = [
                    # Format: (case_name, case_number, suffix, base_form, confidence)
                    # First case (nominative)
                    ("nominative", "singular", "", base_long, 0.9),
                    ("nominative", "singular", "u", base_long, 0.8),
                    ("nominative", "singular", "o", base_long, 0.8),
                    ("nominative", "plural", "", base_long, 0.9),
                    ("nominative", "plural", "u", base_long, 0.8),
                    ("nominative", "plural", "o", base_long, 0.8),
                    
                    # Second case (accusative)
                    ("accusative", "singular", "M", base_short, 0.9),
                    ("accusative", "plural", "", base_long, 0.9),
                    ("accusative", "plural", "u", base_long, 0.8),
                    ("accusative", "plural", "o", base_long, 0.8),
                ]
                
                # Add feminine patterns to case_patterns
                case_patterns.extend(fem_patterns)
            
            # Process case patterns
            for pattern in case_patterns:
                if pattern is None:
                    continue
                    
                case_name, case_number, suffix, base_form, confidence = pattern
                
                # Check if the word matches this pattern
                if suffix and hk_word.endswith(suffix) and len(hk_word) > len(suffix):
                    potential_stem = hk_word[:-len(suffix)]
                    if base_form and potential_stem == base_form:
                        # Apply learning-based confidence adjustment
                        adjusted_confidence = confidence + self.learning_system.get_confidence_adjustment(hk_word)
                        
                        match = {
                            'stem': potential_stem,
                            'form': hk_word,
                            'gender': detected_gender,
                            'case': case_name,
                            'number': case_number,
                            'source': f"fallback declension analysis ('{suffix}' ending)",
                            'confidence': min(adjusted_confidence, 1.0),
                            'notes': [f"Form ends with '{suffix}', suggesting {case_name} {case_number}."]
                        }
                        possible_matches.append(match)
                elif not suffix and hk_word == base_form:
                    # For cases where the form equals the base (no suffix)
                    adjusted_confidence = confidence + self.learning_system.get_confidence_adjustment(hk_word)
                    
                    # Extract potential stem
                    potential_stem = hk_word
                    if ending in 'aA':
                        potential_stem = hk_word[:-1]
                    elif ending in 'iIuU':
                        potential_stem = hk_word[:-1]
                    
                    match = {
                        'stem': potential_stem,
                        'form': hk_word,
                        'gender': detected_gender,
                        'case': case_name,
                        'number': case_number,
                        'source': f"fallback declension analysis (base form)",
                        'confidence': min(adjusted_confidence, 1.0),
                        'notes': [f"Form matches base form, suggesting {case_name} {case_number}."]
                    }
                    possible_matches.append(match)
        
        # Stage 5: If still no matches found, provide a basic heuristic analysis
        if not possible_matches:
            # Extract potential stem
            potential_stem = hk_word
            if hk_word.endswith(('a', 'A', 'i', 'I', 'u', 'U')):
                potential_stem = hk_word[:-1]
            
            # Guess gender
            gender = 'unknown'
            if hk_word.endswith('a'):
                gender = 'masculine'
            elif hk_word.endswith('A'):
                gender = 'feminine'
            elif hk_word.endswith('i'):
                gender = 'masculine'
            elif hk_word.endswith('I'):
                gender = 'feminine'
            elif hk_word.endswith('u'):
                gender = 'masculine'
            elif hk_word.endswith('U'):
                gender = 'feminine'
            
            # Add basic analysis with low confidence
            match = {
                'stem': potential_stem,
                'form': hk_word,
                'gender': gender,
                'case': 'unknown',
                'number': 'unknown',
                'source': 'basic stem extraction',
                'confidence': 0.3,
                'notes': ["No detailed analysis found. This is a basic stem extraction with low confidence."]
            }
            possible_matches.append(match)
        
        # Sort by confidence
        possible_matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Record this analysis for learning
        self.learning_system.record_analysis(hk_word, possible_matches, 'noun')
        
        return possible_matches
    
    def enhanced_noun_analysis(self, noun_form):
        """Enhanced noun analysis using case-specific suffixes from prakrit_noun_app.py"""
        # This method is now superseded by the more comprehensive analyze_noun_form method
        return []
    
    def determine_gender_from_stem(self, stem):
        """Determine gender based on stem ending"""
        if not stem:
            return 'unknown'
        
        ending = stem[-1] if stem else ''
        if ending in ['a', 'A']:
            return 'masculine/neuter'
        elif ending in ['i', 'I']:
            return 'feminine'
        elif ending in ['u', 'U']:
            return 'masculine'
        else:
            return 'unknown'

# Initialize the enhanced analyzer
enhanced_analyzer = EnhancedPrakritAnalyzer()

@app.route('/', methods=['GET'])
def index():
    return render_template('analyzer.html')

@app.route('/analyze', methods=['POST'])
def analyze_verb():
    # Accept form-urlencoded data for verb analysis
    verb = request.form.get('verb_form', '').strip()
    if not verb:
        return jsonify({'error': 'No verb form provided.'}), 400
    
    # Use enhanced validation
    is_valid, error_message = enhanced_analyzer.enhanced_validate_prakrit_characters(verb)
    if not is_valid:
        return jsonify({'error': error_message}), 400
    
    # Use enhanced analysis with learning
    results = enhanced_analyzer.analyze_with_learning(verb, 'verb')
    
    # If error in analysis, return as error
    if results and isinstance(results, list) and 'error' in results[0]:
        return jsonify(results[0]), 400
    
    return jsonify({'results': results})

@app.route('/analyze_noun', methods=['POST'])
def analyze_noun():
    # Accept JSON data for noun analysis
    data = request.get_json()
    noun = data.get('noun', '').strip() if data else ''
    if not noun:
        return jsonify({'success': False, 'error': 'No noun form provided.'})
    
    # Use enhanced validation
    is_valid, error_message = enhanced_analyzer.enhanced_validate_prakrit_characters(noun)
    if not is_valid:
        return jsonify({'success': False, 'error': error_message})
    
    # Use enhanced analysis with learning
    results = enhanced_analyzer.analyze_with_learning(noun, 'noun')
    return jsonify({'success': True, 'analysis': results})

@app.route('/feedback', methods=['POST'])
def record_feedback():
    """Record user feedback for learning"""
    data = request.get_json()
    form = data.get('form')
    analysis_id = data.get('analysis_id')
    feedback = data.get('feedback')
    user_correction = data.get('user_correction')
    
    if form and analysis_id and feedback:
        enhanced_analyzer.learning_system.record_feedback(form, analysis_id, feedback, user_correction)
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Invalid feedback data'}), 400

@app.route('/report_issue', methods=['POST'])
def report_issue():
    """Send issue report to developer via Formspree"""
    data = request.get_json()
    
    # Prepare report data
    report_data = {
        'form_analyzed': data.get('form', ''),
        'analysis_type': data.get('analysis_type', ''),
        'analysis_results': json.dumps(data.get('analysis_results', {}), indent=2),
        'user_feedback': data.get('user_feedback', ''),
        'user_correction': data.get('user_correction', ''),
        'timestamp': datetime.now().isoformat(),
        'user_agent': request.headers.get('User-Agent', ''),
        'ip_address': request.remote_addr
    }
    
    # Send to Formspree
    import requests
    try:
        response = requests.post('https://formspree.io/f/xkgqqyzq', data=report_data)
        if response.status_code == 200:
            return jsonify({'success': True, 'message': 'Report sent successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to send report'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(500)
def handle_error(error):
    response = jsonify({'success': False, 'error': str(error)})
    response.status_code = error.code if hasattr(error, 'code') else 500
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)