import re
from aksharamukha import transliterate
import sys

def detect_script(text):
    if any('\u0900' <= c <= '\u097F' for c in text):
        return 'Devanagari'
    return 'HK'

def transliterate_to_hk(text):
    return transliterate.process('Devanagari', 'HK', text) if detect_script(text) == 'Devanagari' else text

def validate_prakrit_characters(text):
    hk_text = transliterate_to_hk(text)
    forbidden_singles = ['R', 'RR', 'lR', 'lRR', 'H', 'S']
    for char in forbidden_singles:
        if char in hk_text:
            return False, f"The character '{char}' is not found in Prakrit."
    if 'H' in hk_text:
        return False, f"The visarga (ः/H) is not found in Prakrit."
    allowed_conjuncts = [
        'kk', 'kkh', 'gg', 'ggh', 'cc', 'cch', 'jj', 'jjh', 
        'TT', 'TTh', 'DD', 'DDh', 'NN', 'tt', 'tth', 'dd', 'ddh', 
        'nn', 'pp', 'pph', 'bb', 'bbh', 'mm', 'yy', 'rr', 'll', 
        'vv', 'ss', 'zz', 'dr', 'mh', 'nh', 'lh'
    ]
    special_consonants = ['G', 'J', 'N', 'n', 'm']
    potential_conjuncts = re.findall(r'[kgcjTDNtdnpbmyrlvszh][kgcjTDNtdnpbmyrlvszh]+', hk_text)
    for conjunct in potential_conjuncts:
        if conjunct in allowed_conjuncts:
            continue
        valid = False
        for special in special_consonants:
            if conjunct.startswith(special) or conjunct.endswith(special):
                valid = True
                break
        if not valid:
            return False, f"The conjunct '{conjunct}' is not allowed in Prakrit."
    return True, ""

def analyze_noun_form(word):
    import os, json
    json_path = os.path.join(os.path.dirname(__file__), 'all_noun_forms.json')
    try:
        with open(json_path, encoding='utf-8') as f:
            all_noun_forms = json.load(f)
    except Exception:
        all_noun_forms = {}
    hk_word = transliterate_to_hk(word)
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
                'notes': [f"Form '{hk_word}' attested for stem '{stem}'."]
            }
            possible_matches.append(match)
    # 2. Heuristic matches: try all plausible endings and positions
    endings = [
        'M', 'm', 'iM', 'im', 'i~', 'Ni', 'ni', 'Na', 'na', 'NaM', 'nam', 'hi', 'him', 'hi~', 'su', 'sum', 'suM', 'tto', 'o', 'u', 'e', 'A'
    ]
    case_map = {
        'M': 'nominative/accusative singular',
        'iM': 'nominative/accusative plural',
        'i~': 'nominative/accusative plural',
        'Ni': 'nominative/accusative plural',
        'Na': 'instrumental singular',
        'NaM': 'instrumental plural',
        'hi': 'locative singular',
        'hiM': 'locative plural',
        'hi~': 'locative plural',
        'su': 'locative plural',
        'suM': 'locative plural',
        'tto': 'ablative singular',
        'o': 'vocative',
        'u': 'vocative',
        'e': 'vocative',
        'A': 'vocative',
    }
    for ending in endings:
        # Direct match
        if hk_word.endswith(ending):
            potential_stem = hk_word[:-len(ending)]
            # Guess gender
            if ending in ['a', 'A', 'i', 'I', 'u', 'U']:
                if ending == 'a' or ending == 'A':
                    gender = 'masculine/neuter'
                elif ending in ['i', 'I']:
                    gender = 'feminine'
                elif ending in ['u', 'U']:
                    gender = 'masculine'
                else:
                    gender = 'unknown'
            else:
                gender = 'unknown'
            match = {
                'stem': potential_stem if potential_stem else 'unknown',
                'form': hk_word,
                'gender': gender,
                'case': case_map.get(ending.replace('m','M'), 'unknown'),
                'number': 'unknown',
                'source': 'heuristic',
                'confidence': 0.5,
                'notes': [f"Heuristic match for ending '{ending}'."]
            }
            possible_matches.append(match)
        # Hiatus handling: allow for an extra 'y' between two vowels before ending
        if hk_word.endswith('y' + ending):
            idx = -len(ending)-1
            if len(hk_word) > abs(idx):
                prev_char = hk_word[idx]
                first_char = ending[0] if ending else ''
                vowels = set('aeiouAEIOU')
                if prev_char in vowels and first_char in vowels:
                    potential_stem = hk_word[:idx]
                    # Check if form without 'y' is attested
                    attested_boost = False
                    attested_stem = None
                    attested_info = None
                    form_without_y = hk_word[:idx] + ending
                    for stem, forms in all_noun_forms.items():
                        if form_without_y in forms:
                            attested_boost = True
                            attested_stem = stem
                            attested_info = forms[form_without_y]
                            break
                    match = {
                        'stem': potential_stem if potential_stem else 'unknown',
                        'form': hk_word,
                        'gender': 'unknown',
                        'case': case_map.get(ending.replace('m','M'), 'unknown'),
                        'number': 'unknown',
                        'source': 'heuristic (hiatus y)',
                        'confidence': 0.4,
                        'notes': [f"Heuristic match for ending 'y{ending}' (hiatus y inserted between vowels before ending)."]
                    }
                    if attested_boost:
                        match['confidence'] = 0.8
                        match['stem'] = attested_stem
                        match['gender'] = attested_info.get('gender', 'unknown')
                        match['case'] = attested_info.get('case', 'unknown')
                        match['number'] = attested_info.get('number', 'unknown')
                        match['notes'].append(f"Form without 'y' ('{form_without_y}') attested for stem '{attested_stem}'. Confidence boosted.")
                    possible_matches.append(match)
    # If no matches, fallback to basic analysis
    if not possible_matches:
        ending = hk_word[-1] if hk_word else ''
        if ending in ['a', 'A', 'i', 'I', 'u', 'U']:
            if ending == 'a' or ending == 'A':
                gender = 'masculine/neuter'
            elif ending in ['i', 'I']:
                gender = 'feminine'
            elif ending in ['u', 'U']:
                gender = 'masculine'
            else:
                gender = 'unknown'
        else:
            gender = 'unknown'
        match = {
            'stem': 'unknown',
            'form': hk_word,
            'gender': gender,
            'case': 'unknown',
            'number': 'unknown',
            'source': 'heuristic',
            'confidence': 0.2,
            'notes': ["No attested or heuristic match found."]
        }
        possible_matches.append(match)
    # Sort by confidence
    possible_matches.sort(key=lambda x: x['confidence'], reverse=True)
    return possible_matches

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python noun_analyzer.py <noun_form>")
        sys.exit(1)
    word = sys.argv[1]
    is_valid, error_message = validate_prakrit_characters(word)
    if not is_valid:
        print(f"Error: {error_message}")
        sys.exit(1)
    possibilities = analyze_noun_form(word)
    print(f"Analysis for: {word}")
    for i, analysis in enumerate(possibilities, 1):
        print(f"\nPossibility {i}:")
        for k, v in analysis.items():
            if k == 'notes' and isinstance(v, list):
                print(f"  Notes: {'; '.join(v)}")
            else:
                print(f"  {k.capitalize()}: {v}")
    sys.exit(0)