from flask import Flask, render_template, request, jsonify
import re
import json
import logging
import sys
import os
from typing import Optional, Dict, List, Set, Tuple, Any

# Configure logging first
# Check if running in serverless environment (Vercel/AWS Lambda)
is_serverless = os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME')

if is_serverless:
    # Serverless: only log to stdout (no file logging)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
else:
    # Local: log to both stdout and file
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('prakrit_parser.log')
        ]
    )
logger = logging.getLogger(__name__)

# Try to import aksharamukha, provide fallback if not available
try:
    import aksharamukha.transliterate as aksh
    TRANSLITERATION_AVAILABLE = True
except ImportError:
    logger.warning("aksharamukha module not available - transliteration will be limited")
    TRANSLITERATION_AVAILABLE = False
    aksh = None

try:
    from input_validation import InputValidator, validate_and_sanitize
    INPUT_VALIDATION_AVAILABLE = True
except ImportError:
    logger.warning("input_validation module not available - validation will be basic")
    INPUT_VALIDATION_AVAILABLE = False
    InputValidator = None
    validate_and_sanitize = None

app = Flask(__name__)

# Load Prakrit verb roots from verbs.json
VERB_ROOTS = set()
ALL_VERB_FORMS = {}

try:
    VERBS_PATH = os.path.join(os.path.dirname(__file__), 'verbs.json')
    with open(VERBS_PATH, encoding='utf-8') as f:
        VERB_ROOTS = set(json.load(f).values())
    logger.info(f"Loaded {len(VERB_ROOTS)} verb roots from {VERBS_PATH}")
except FileNotFoundError:
    logger.error(f"Verb roots file not found: {VERBS_PATH}")
    logger.warning("Running with empty verb roots set")
except json.JSONDecodeError as e:
    logger.error(f"Error decoding verb roots JSON: {e}")
    logger.warning("Running with empty verb roots set")
except Exception as e:
    logger.error(f"Unexpected error loading verb roots: {e}")
    logger.warning("Running with empty verb roots set")

# Load all attested verb forms
try:
    ALL_FORMS_PATH = os.path.join(os.path.dirname(__file__), 'all_verb_forms.json')
    with open(ALL_FORMS_PATH, encoding='utf-8') as f:
        ALL_VERB_FORMS = json.load(f)
    total_forms = sum(len(forms) for forms in ALL_VERB_FORMS.values())
    logger.info(f"Loaded {len(ALL_VERB_FORMS)} roots with {total_forms} attested forms from {ALL_FORMS_PATH}")
except FileNotFoundError:
    logger.error(f"All verb forms file not found: {ALL_FORMS_PATH}")
    logger.warning("Running with empty attested forms dictionary")
except json.JSONDecodeError as e:
    logger.error(f"Error decoding all verb forms JSON: {e}")
    logger.warning("Running with empty attested forms dictionary")
except Exception as e:
    logger.error(f"Unexpected error loading all verb forms: {e}")
    logger.warning("Running with empty attested forms dictionary")

def detect_script(text: str) -> str:
    """
    Detect if the input is in Devanagari or Harvard-Kyoto script.

    Args:
        text: Input text to analyze

    Returns:
        'devanagari' if text contains Devanagari characters, 'hk' otherwise
    """
    devanagari_pattern = re.compile(r'[\u0900-\u097F]')
    if devanagari_pattern.search(text):
        return 'devanagari'
    return 'hk'

def transliterate(text: str, from_script: str, to_script: str) -> str:
    """
    Transliterate text between Devanagari and Harvard-Kyoto scripts.

    Args:
        text: Text to transliterate
        from_script: Source script ('devanagari' or 'hk')
        to_script: Target script ('devanagari' or 'hk')

    Returns:
        Transliterated text, or original text if no conversion needed

    Raises:
        RuntimeError: If transliteration is requested but aksharamukha is not available
    """
    if not TRANSLITERATION_AVAILABLE:
        if from_script != to_script:
            logger.error("Transliteration requested but aksharamukha not available")
            raise RuntimeError("Transliteration module not available. Please install aksharamukha.")
        return text

    if from_script == 'devanagari' and to_script == 'hk':
        return aksh.process('Devanagari', 'HK', text)
    elif from_script == 'hk' and to_script == 'devanagari':
        return aksh.process('HK', 'Devanagari', text)
    return text

def is_valid_prakrit_sequence(text: str) -> bool:
    """
    Validate if a text sequence follows Prakrit phonological rules.

    Args:
        text: Text to validate

    Returns:
        True if sequence is valid according to Prakrit phonology, False otherwise

    Note:
        In Prakrit, vowel hiatus is allowed, especially in verbal forms:
        - ai (read as a_i) as in muṇissai
        - ae (read as a_e) as in jāṇae
        - oe (read as o_e) as in hoe
        - ie (read as i_e) as in jāṇie
    """
    # Basic Prakrit phonological rules - only for consonants
    invalid_patterns = [
        r'[kgcjṭḍtdpb][kgcjṭḍtdpb]',  # No double consonants without gemination
        r'[kgcjṭḍtdpb]h[kgcjṭḍtdpb]',  # Aspirated consonants followed by stops
    ]

    # Check only consonant-related patterns
    for pattern in invalid_patterns:
        if re.search(pattern, text):
            return False
    return True

def apply_sandhi_rules(stem: str, ending: str) -> str:
    """
    Apply Prakrit sandhi (euphonic combination) rules between stem and ending.

    Args:
        stem: Verb stem
        ending: Verb ending

    Returns:
        Combined form with appropriate sandhi rules applied

    Note:
        In Prakrit, many vowel combinations are preserved as hiatus.
        Only specific cases have glide insertion:
        - i + a → iya (glide 'y' inserted)
        - u + a → uva (glide 'v' inserted)

        Most other vowel combinations remain as hiatus:
        - a + i → ai (not e)
        - a + e → ae (not e)
        - i + e → ie
        - o + e → oe
    """
    # Cases where glides are inserted
    if stem.endswith('i') and ending.startswith('a'):
        return stem + 'y' + ending  # i + a → iya
    if stem.endswith('u') and ending.startswith('a'):
        return stem + 'v' + ending  # u + a → uva

    # Most other vowel combinations remain as hiatus in Prakrit
    return stem + ending

def identify_prefix(verb_form: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Identify possible Prakrit verbal prefixes in a verb form.

    Args:
        verb_form: The verb form to analyze

    Returns:
        Tuple of (prakrit_prefix, sanskrit_equivalent) if found, (None, None) otherwise

    Example:
        >>> identify_prefix('paṇivāe')
        ('pa', 'pra')
    """
    prefixes = {
        'pa': 'pra',
        'paḍi': 'prati',
        'pari': 'pari',
        'saṃ': 'sam',
        'vi': 'vi',
        'ā': 'ā',
        'ni': 'ni',
        'u': 'ud',
        'aṇu': 'anu'
    }

    for prefix, sanskrit in prefixes.items():
        if verb_form.startswith(prefix):
            return prefix, sanskrit
    return None, None

def analyze_endings(verb_form: str) -> Optional[List[Dict[str, Any]]]:
    """
    Analyze verb endings to determine person, number, and tense.

    Args:
        verb_form: The Prakrit verb form to analyze (in HK transliteration)

    Returns:
        List of possible analyses sorted by confidence (highest first),
        or None if no valid analysis found.

        Each analysis is a dictionary containing:
        - analysis: Dict with tense, person, number, confidence
        - potential_root: Identified root
        - ending: Matched ending
        - prefix: Prakrit prefix if found
        - sanskrit_prefix: Sanskrit equivalent of prefix
        - confidence: Float between 0 and 1
        - notes: List of explanatory notes
        - sandhi_applied: Boolean indicating if sandhi was applied
    """
    # Present tense endings with variants
    present_endings = {
        'mi': {'person': 'first', 'number': 'singular', 'tense': 'present', 'confidence': 1.0},
        'si': {'person': 'second', 'number': 'singular', 'tense': 'present', 'confidence': 1.0},
        'se': {'person': 'second', 'number': 'singular', 'tense': 'present', 'confidence': 0.9},
        'di': {'person': 'third', 'number': 'singular', 'tense': 'present', 'confidence': 1.0},
        'i': {'person': 'third', 'number': 'singular', 'tense': 'present', 'confidence': 0.9},
        'e': {'person': 'third', 'number': 'singular', 'tense': 'present', 'confidence': 0.9},
        'ae': {'person': 'third', 'number': 'singular', 'tense': 'present', 'confidence': 0.85},
        'mo': {'person': 'first', 'number': 'plural', 'tense': 'present', 'confidence': 1.0},
        'mu': {'person': 'first', 'number': 'plural', 'tense': 'present', 'confidence': 0.9},
        'ma': {'person': 'first', 'number': 'plural', 'tense': 'present', 'confidence': 0.9},
        'ha': {'person': 'second', 'number': 'plural', 'tense': 'present', 'confidence': 1.0},
        'tha': {'person': 'second', 'number': 'plural', 'tense': 'present', 'confidence': 0.9},
        'nti': {'person': 'third', 'number': 'plural', 'tense': 'present', 'confidence': 1.0},
        'nte': {'person': 'third', 'number': 'plural', 'tense': 'present', 'confidence': 0.9},
        'mhi': {'person': 'first', 'number': 'singular', 'tense': 'present', 'confidence': 0.8},
    }

    # Future tense endings with variants
    future_endings = {
        'himi': {'person': 'first', 'number': 'singular', 'tense': 'future', 'confidence': 1.0},
        'ssaM': {'person': 'first', 'number': 'singular', 'tense': 'future', 'confidence': 1.0},
        'ssAmi': {'person': 'first', 'number': 'singular', 'tense': 'future', 'confidence': 0.9},
        'issaM': {'person': 'first', 'number': 'singular', 'tense': 'future', 'confidence': 0.9},
        'issAmi': {'person': 'first', 'number': 'singular', 'tense': 'future', 'confidence': 0.9},
        'hisi': {'person': 'second', 'number': 'singular', 'tense': 'future', 'confidence': 1.0},
        'hise': {'person': 'second', 'number': 'singular', 'tense': 'future', 'confidence': 0.9},
        'issasi': {'person': 'second', 'number': 'singular', 'tense': 'future', 'confidence': 0.9},
        'hi': {'person': 'third', 'number': 'singular', 'tense': 'future', 'confidence': 1.0},
        'hii': {'person': 'third', 'number': 'singular', 'tense': 'future', 'confidence': 0.9},
        'issa_e': {'person': 'third', 'number': 'singular', 'tense': 'future', 'confidence': 0.9},
        'hie': {'person': 'third', 'number': 'singular', 'tense': 'future', 'confidence': 0.9},
        'issa_i': {'person': 'third', 'number': 'singular', 'tense': 'future', 'confidence': 0.9},
        'himo': {'person': 'first', 'number': 'plural', 'tense': 'future', 'confidence': 1.0},
        'himu': {'person': 'first', 'number': 'plural', 'tense': 'future', 'confidence': 0.9},
        'hima': {'person': 'first', 'number': 'plural', 'tense': 'future', 'confidence': 0.9},
        'issAmo': {'person': 'first', 'number': 'plural', 'tense': 'future', 'confidence': 0.9},
        'hitthA': {'person': 'second', 'number': 'plural', 'tense': 'future', 'confidence': 1.0},
        'hiha': {'person': 'second', 'number': 'plural', 'tense': 'future', 'confidence': 0.9},
        'issatha': {'person': 'second', 'number': 'plural', 'tense': 'future', 'confidence': 0.9},
        'hinti': {'person': 'third', 'number': 'plural', 'tense': 'future', 'confidence': 1.0},
        'hinte': {'person': 'third', 'number': 'plural', 'tense': 'future', 'confidence': 0.9},
        'issanti': {'person': 'third', 'number': 'plural', 'tense': 'future', 'confidence': 0.9},
        'issante': {'person': 'third', 'number': 'plural', 'tense': 'future', 'confidence': 0.9},
    }

    # Past tense endings with variants
    past_endings = {
        'sI': {'person': 'all', 'number': 'all', 'tense': 'past', 'confidence': 1.0},
        'hI': {'person': 'all', 'number': 'all', 'tense': 'past', 'confidence': 1.0},
        'hIa': {'person': 'all', 'number': 'all', 'tense': 'past', 'confidence': 0.9},
        'Ia': {'person': 'all', 'number': 'all', 'tense': 'past', 'confidence': 0.9},
        'itta': {'person': 'all', 'number': 'all', 'tense': 'past', 'confidence': 0.8},
        'iya': {'person': 'all', 'number': 'all', 'tense': 'past', 'confidence': 0.8},
    }

    # Identify prefix if any
    prefix, sanskrit_prefix = identify_prefix(verb_form)
    if prefix:
        verb_form = verb_form[len(prefix):]

    # Combine all endings
    all_endings = {**present_endings, **future_endings, **past_endings}
    
    possible_matches = []
    vowels = set('aeiouAEIOU')
    # First, check if verb_form is attested in ALL_VERB_FORMS
    attested_root = None
    for root, forms in ALL_VERB_FORMS.items():
        if verb_form in forms:
            attested_root = root
            break
    if attested_root:
        # Find ending and position for attested form
        for ending, info in all_endings.items():
            if verb_form.endswith(ending):
                info = info.copy()
                info['root'] = attested_root
                match = {
                    'analysis': info,
                    'potential_root': attested_root,  # Show attested root
                    'ending': ending,
                    'prefix': prefix,
                    'sanskrit_prefix': sanskrit_prefix,
                    'confidence': min(info['confidence'] + 0.25, 1.0),
                    'notes': [f"Form '{verb_form}' attested for root '{attested_root}'."]
                }
                possible_matches.append(match)
        # If found, return only attested match as highest confidence
        if possible_matches:
            possible_matches.sort(key=lambda x: x['confidence'], reverse=True)
            return possible_matches
    # If not attested, proceed with guessing/hunting as before
    # Direct matches
    for ending, info in all_endings.items():
        # Support Mti/Mte as variants for nti/nte
        endings_to_check = [ending]
        if ending == 'nti':
            endings_to_check.append('Mti')
        if ending == 'nte':
            endings_to_check.append('Mte')
        for test_ending in endings_to_check:
            if verb_form.endswith(test_ending):
                potential_root = verb_form[:-len(test_ending)]
                # Filter: root should not end with 'a'
                if potential_root.endswith('a'):
                    continue
                # Filter: 'i' ending must be preceded by a vowel
                if ending == 'i' and (len(potential_root) == 0 or potential_root[-1] not in vowels):
                    continue
                # Handle Mti/Mte forms (anusvāra)
                info_copy = info.copy()
                if test_ending in ['Mti', 'Mte']:
                    info_copy['note'] = 'Anusvāra (M) used before nti/nte (written as Mti/Mte) in Prakrit.'
                elif ending in ['nti', 'nte'] and len(potential_root) > 0 and potential_root[-1] == 'M':
                    info_copy['note'] = 'Anusvāra (M) used before nti/nte in Prakrit.'
                if is_valid_prakrit_sequence(potential_root):
                    # Fallback to longest substring in VERB_ROOTS
                    matched_root = None
                    for i in range(len(potential_root), 0, -1):
                        subroot = potential_root[:i]
                        if subroot in VERB_ROOTS:
                            matched_root = subroot
                            break
                    # If not found, try removing trailing 'e' or 'i' and check again
                    if not matched_root and potential_root and potential_root[-1] in ['e', 'i']:
                        alt_root = potential_root[:-1]
                        for i in range(len(alt_root), 0, -1):
                            subroot = alt_root[:i]
                            if subroot in VERB_ROOTS:
                                matched_root = subroot
                                break
                    if matched_root:
                        info_copy['root'] = matched_root
                    match = {
                        'analysis': info_copy,
                        'potential_root': potential_root,
                        'ending': test_ending,
                        'prefix': prefix,
                        'sanskrit_prefix': sanskrit_prefix,
                        'confidence': info_copy['confidence']
                    }
                    # Confidence logic
                    if matched_root:
                        boost = 0.15 + 0.05 * (len(matched_root) / max(1, len(potential_root)))
                        match['confidence'] = min(match['confidence'] + boost, 1.0)
                        match.setdefault('notes', []).append(f"Root '{matched_root}' attested in Prakrit verb list.")
                    else:
                        match['confidence'] = max(match['confidence'] - 0.2, 0.1)
                        match.setdefault('notes', []).append("Root not attested in Prakrit verb list.")
                    possible_matches.append(match)
    # Sandhi matches
    for ending, info in all_endings.items():
        # Support Mti/Mte as variants for nti/nte
        endings_to_check = [ending]
        if ending == 'nti':
            endings_to_check.append('Mti')
        if ending == 'nte':
            endings_to_check.append('Mte')
        for test_ending in endings_to_check:
            for i in range(1, min(4, len(verb_form))):
                potential_root = verb_form[:-i]
                # Filter: root should not end with 'a'
                if potential_root.endswith('a'):
                    continue
                # Filter: 'i' ending must be preceded by a vowel
                if ending == 'i' and (len(potential_root) == 0 or potential_root[-1] not in vowels):
                    continue
                # Handle Mti/Mte forms (anusvāra)
                info_copy = info.copy()
                if test_ending in ['Mti', 'Mte']:
                    info_copy['note'] = 'Anusvāra (M) used before nti/nte (written as Mti/Mte) in Prakrit.'
                elif ending in ['nti', 'nte'] and len(potential_root) > 0 and potential_root[-1] == 'M':
                    info_copy['note'] = 'Anusvāra (M) used before nti/nte in Prakrit.'
                if is_valid_prakrit_sequence(potential_root):
                    sandhi_form = apply_sandhi_rules(potential_root, ending)
                    # Also check sandhi for Mti/Mte
                    sandhi_form_M = apply_sandhi_rules(potential_root, test_ending) if test_ending in ['Mti', 'Mte'] else None
                    if sandhi_form == verb_form or (sandhi_form_M and sandhi_form_M == verb_form):
                        # Fallback to longest substring in VERB_ROOTS
                        matched_root = None
                        for j in range(len(potential_root), 0, -1):
                            subroot = potential_root[:j]
                            if subroot in VERB_ROOTS:
                                matched_root = subroot
                                break
                        # If not found, try removing trailing 'e' or 'i' and check again
                        if not matched_root and potential_root and potential_root[-1] in ['e', 'i']:
                            alt_root = potential_root[:-1]
                            for k in range(len(alt_root), 0, -1):
                                subroot = alt_root[:k]
                                if subroot in VERB_ROOTS:
                                    matched_root = subroot
                                    break
                        if matched_root:
                            info_copy['root'] = matched_root
                        match = {
                            'analysis': info_copy,
                            'potential_root': potential_root,
                            'ending': test_ending,
                            'prefix': prefix,
                            'sanskrit_prefix': sanskrit_prefix,
                            'confidence': info_copy['confidence'] * 0.9,
                            'sandhi_applied': True
                        }
                        # Confidence logic
                        if matched_root:
                            boost = 0.15 + 0.05 * (len(matched_root) / max(1, len(potential_root)))
                            match['confidence'] = min(match['confidence'] + boost, 1.0)
                            match.setdefault('notes', []).append(f"Root '{matched_root}' attested in Prakrit verb list.")
                        else:
                            match['confidence'] = max(match['confidence'] - 0.2, 0.1)
                            match.setdefault('notes', []).append("Root not attested in Prakrit verb list.")
                        possible_matches.append(match)
    if not possible_matches:
        return None
    possible_matches.sort(key=lambda x: x['confidence'], reverse=True)
    return possible_matches

@app.route('/', methods=['GET'])
def index():
    return render_template('analyzer.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    verb_form = request.form.get('verb_form', '')

    if not verb_form:
        logger.warning("Empty verb form received")
        return jsonify({"error": "Please provide a verb form"}), 400

    # Validate and sanitize input
    if INPUT_VALIDATION_AVAILABLE:
        is_valid, error_msg, sanitized_form = validate_and_sanitize(verb_form)
        if not is_valid:
            logger.warning(f"Invalid input rejected: {error_msg}")
            return jsonify({
                "error": f"Invalid input: {error_msg}",
                "suggestions": [
                    "Ensure input contains only valid Prakrit characters",
                    "Check that the input is a valid verb form",
                    "Input should be between 1 and 200 characters"
                ]
            }), 400
        verb_form = sanitized_form
        logger.debug(f"Input validated and sanitized: {verb_form}")

    logger.info(f"Analyzing verb form: {verb_form}")

    try:
        # Detect script and convert to HK if needed
        detected_script = detect_script(verb_form)
        logger.debug(f"Detected script: {detected_script}")

        working_form = verb_form
        if detected_script == 'devanagari':
            working_form = transliterate(verb_form, 'devanagari', 'hk')
            logger.debug(f"Transliterated to HK: {working_form}")

        # Preprocess HK input: replace 'ai' with 'a_i' for hiatus handling
        if detected_script == 'hk' or (detected_script == 'devanagari' and working_form):
            # Only replace if not already a_i
            working_form = re.sub(r'(?<!_)ai', 'a_i', working_form)

        # Analyze the form
        possibilities = analyze_endings(working_form)
        logger.debug(f"Found {len(possibilities) if possibilities else 0} possible analyses")
        if not possibilities:
            logger.info(f"No valid analysis found for: {verb_form}")
            return jsonify({
                "error": "Could not analyze this form. It may not be a valid Prakrit verb form.",
                "suggestions": [
                    "Check if the input follows Prakrit phonological rules",
                    "Ensure the ending is a valid Prakrit verb ending",
                    "Verify the transliteration if using Harvard-Kyoto"
                ]
            }), 400
        # Build results for all possibilities
        results = []
        for analysis in possibilities:
            result = {
                "original_form": verb_form,
                "script": detected_script,
                **analysis
            }
            # Add confidence level interpretation
            if analysis['confidence'] >= 0.9:
                result['reliability'] = "High confidence analysis"
            elif analysis['confidence'] >= 0.7:
                result['reliability'] = "Medium confidence analysis"
            else:
                result['reliability'] = "Low confidence analysis - please verify"
            # Add explanatory notes based on the analysis
            notes = []
            if analysis.get('prefix'):
                notes.append(f"Found verbal prefix '{analysis['prefix']}' (Sanskrit: '{analysis['sanskrit_prefix']}')")
            if analysis.get('sandhi_applied'):
                notes.append("Sandhi rules were applied in this analysis")
            if analysis['analysis']['tense'] == 'past' and analysis['analysis']['person'] == 'all':
                notes.append("Note: Past tense forms in Prakrit are the same for all persons and numbers")
            result['notes'] = notes
            # If the original was in Devanagari, add HK transliteration
            if detected_script == 'devanagari':
                result["hk_form"] = working_form
            results.append(result)
        logger.info(f"Successfully analyzed {verb_form}: {len(results)} result(s)")
        return jsonify({"results": results})
    except Exception as e:
        logger.error(f"Error analyzing {verb_form}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        # CLI mode: python verb_analyzer.py <verb_form>
        verb_form = sys.argv[1]
        detected_script = detect_script(verb_form)
        working_form = verb_form
        if detected_script == 'devanagari':
            working_form = transliterate(verb_form, 'devanagari', 'hk')
        possibilities = analyze_endings(working_form)
        if not possibilities:
            print("No valid analysis found.")
            sys.exit(1)
        print(f"Analysis for: {verb_form} (script: {detected_script})")
        for i, analysis in enumerate(possibilities, 1):
            print(f"\nPossibility {i}:")
            print(f"  Tense: {analysis['analysis']['tense']}")
            print(f"  Person: {analysis['analysis']['person']}")
            print(f"  Number: {analysis['analysis']['number']}")
            print(f"  Root: {analysis['potential_root']}")
            print(f"  Ending: {analysis['ending']}")
            print(f"  Confidence: {analysis['confidence']}")
            if analysis.get('prefix'):
                print(f"  Prefix: {analysis['prefix']} (Sanskrit: {analysis['sanskrit_prefix']})")
            if analysis.get('sandhi_applied'):
                print("  Sandhi rules applied")
        sys.exit(0)
    else:
        import os
        port = int(os.environ.get("PORT", 5001))
        app.run(host='0.0.0.0', port=port)
