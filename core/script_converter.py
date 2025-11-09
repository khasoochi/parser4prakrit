#!/usr/bin/env python3
"""
Script conversion module for Prakrit text.
Converts between Harvard-Kyoto, Devanagari, IAST, and ISO 15919.
Uses the indic-transliteration library for accurate conversion.
"""

try:
    from indic_transliteration import sanscript
    from indic_transliteration.sanscript import transliterate
    HAS_INDIC_TRANSLITERATION = True
except ImportError:
    HAS_INDIC_TRANSLITERATION = False
    print("Warning: indic-transliteration not installed. Install with: pip install indic-transliteration")


class ScriptConverter:
    """Handles script conversion for Prakrit text."""

    SCRIPTS = ['devanagari', 'iast', 'iso15919', 'hk']

    # Fallback Harvard-Kyoto to Devanagari mapping (if library not available)
    HK_TO_DEVANAGARI = {
        # Vowels
        'a': 'अ', 'A': 'आ', 'i': 'इ', 'I': 'ई', 'u': 'उ', 'U': 'ऊ',
        'R': 'ऋ', 'RR': 'ॠ', 'lR': 'ऌ', 'lRR': 'ॡ',
        'e': 'ए', 'ai': 'ऐ', 'o': 'ओ', 'au': 'औ',

        # Consonants
        'k': 'क्', 'kh': 'ख्', 'g': 'ग्', 'gh': 'घ्', 'G': 'ङ्',
        'c': 'च्', 'ch': 'छ्', 'j': 'ज्', 'jh': 'झ्', 'J': 'ञ्',
        'T': 'ट्', 'Th': 'ठ्', 'D': 'ड्', 'Dh': 'ढ्', 'N': 'ण्',
        't': 'त्', 'th': 'थ्', 'd': 'द्', 'dh': 'ध्', 'n': 'न्',
        'p': 'प्', 'ph': 'फ्', 'b': 'ब्', 'bh': 'भ्', 'm': 'म्',
        'y': 'य्', 'r': 'र्', 'l': 'ल्', 'v': 'व्',
        'z': 'श्', 's': 'स्', 'S': 'ष्', 'h': 'ह्',

        # Special characters
        'M': 'ं', 'H': 'ः', 'Z': '़',

        # Vowel marks (when following consonants)
        'AA': 'ा', 'II': 'ी', 'UU': 'ू',
    }

    # Harvard-Kyoto to IAST mapping
    HK_TO_IAST = {
        # Vowels
        'a': 'a', 'A': 'ā', 'i': 'i', 'I': 'ī', 'u': 'u', 'U': 'ū',
        'R': 'ṛ', 'RR': 'ṝ', 'lR': 'ḷ', 'lRR': 'ḹ',
        'e': 'e', 'ai': 'ai', 'o': 'o', 'au': 'au',

        # Consonants
        'k': 'k', 'kh': 'kh', 'g': 'g', 'gh': 'gh', 'G': 'ṅ',
        'c': 'c', 'ch': 'ch', 'j': 'j', 'jh': 'jh', 'J': 'ñ',
        'T': 'ṭ', 'Th': 'ṭh', 'D': 'ḍ', 'Dh': 'ḍh', 'N': 'ṇ',
        't': 't', 'th': 'th', 'd': 'd', 'dh': 'dh', 'n': 'n',
        'p': 'p', 'ph': 'ph', 'b': 'b', 'bh': 'bh', 'm': 'm',
        'y': 'y', 'r': 'r', 'l': 'l', 'v': 'v',
        'z': 'ś', 's': 's', 'S': 'ṣ', 'h': 'h',

        # Special
        'M': 'ṃ', 'H': 'ḥ',
    }

    # Harvard-Kyoto to ISO 15919 mapping
    HK_TO_ISO = {
        # Vowels
        'a': 'a', 'A': 'ā', 'i': 'i', 'I': 'ī', 'u': 'u', 'U': 'ū',
        'R': 'r̥', 'RR': 'r̥̄', 'lR': 'l̥', 'lRR': 'l̥̄',
        'e': 'ē', 'ai': 'ai', 'o': 'ō', 'au': 'au',

        # Consonants
        'k': 'k', 'kh': 'kh', 'g': 'g', 'gh': 'gh', 'G': 'ṅ',
        'c': 'c', 'ch': 'ch', 'j': 'j', 'jh': 'jh', 'J': 'ñ',
        'T': 'ṭ', 'Th': 'ṭh', 'D': 'ḍ', 'Dh': 'ḍh', 'N': 'ṇ',
        't': 't', 'th': 'th', 'd': 'd', 'dh': 'dh', 'n': 'n',
        'p': 'p', 'ph': 'ph', 'b': 'b', 'bh': 'bh', 'm': 'm',
        'y': 'y', 'r': 'r', 'l': 'l', 'v': 'v',
        'z': 'ś', 's': 's', 'S': 'ṣ', 'h': 'h',

        # Special
        'M': 'ṁ', 'H': 'ḥ',
    }

    # Grammatical terminology in different scripts/languages
    GRAMMAR_TERMS = {
        # Gender
        'masculine': {
            'devanagari': 'पुंल्लिंग',
            'iast': 'puṃlliṅga',
            'iso15919': 'puṁlliṅga',
            'english': 'masculine',
            'hk': 'puMlliGga'
        },
        'feminine': {
            'devanagari': 'स्त्रीलिंग',
            'iast': 'strīliṅga',
            'iso15919': 'strīliṅga',
            'english': 'feminine',
            'hk': 'strIliGga'
        },
        'neuter': {
            'devanagari': 'नपुंसकलिंग',
            'iast': 'napuṃsakaliṅga',
            'iso15919': 'napuṁsakaliṅga',
            'english': 'neuter',
            'hk': 'napuMsakaliGga'
        },

        # Transitivity
        'transitive': {
            'devanagari': 'सकर्मक',
            'iast': 'sakarmaka',
            'iso15919': 'sakarmaka',
            'english': 'transitive',
            'hk': 'sakarmaka'
        },
        'intransitive': {
            'devanagari': 'अकर्मक',
            'iast': 'akarmaka',
            'iso15919': 'akarmaka',
            'english': 'intransitive',
            'hk': 'akarmaka'
        },

        # Cases
        'nominative': {
            'devanagari': 'प्रथमा',
            'iast': 'prathamā',
            'iso15919': 'prathamā',
            'english': 'nominative',
            'hk': 'prathamA'
        },
        'accusative': {
            'devanagari': 'द्वितीया',
            'iast': 'dvitīyā',
            'iso15919': 'dvitīyā',
            'english': 'accusative',
            'hk': 'dvitIyA'
        },
        'instrumental': {
            'devanagari': 'तृतीया',
            'iast': 'tṛtīyā',
            'iso15919': 'tr̥tīyā',
            'english': 'instrumental',
            'hk': 'tRtIyA'
        },
        'dative': {
            'devanagari': 'चतुर्थी',
            'iast': 'caturthī',
            'iso15919': 'caturthī',
            'english': 'dative',
            'hk': 'caturthI'
        },
        'ablative': {
            'devanagari': 'पञ्चमी',
            'iast': 'pañcamī',
            'iso15919': 'pañcamī',
            'english': 'ablative',
            'hk': 'paJcamI'
        },
        'genitive': {
            'devanagari': 'षष्ठी',
            'iast': 'ṣaṣṭhī',
            'iso15919': 'ṣaṣṭhī',
            'english': 'genitive',
            'hk': 'SaSThI'
        },
        'locative': {
            'devanagari': 'सप्तमी',
            'iast': 'saptamī',
            'iso15919': 'saptamī',
            'english': 'locative',
            'hk': 'saptamI'
        },
        'vocative': {
            'devanagari': 'संबोधन',
            'iast': 'saṃbodhana',
            'iso15919': 'saṁbōdhana',
            'english': 'vocative',
            'hk': 'saMbodhana'
        },

        # Numbers
        'singular': {
            'devanagari': 'एकवचन',
            'iast': 'ekavacana',
            'iso15919': 'ēkavacana',
            'english': 'singular',
            'hk': 'ekavacana'
        },
        'plural': {
            'devanagari': 'बहुवचन',
            'iast': 'bahuvacana',
            'iso15919': 'bahuvacana',
            'english': 'plural',
            'hk': 'bahuvacana'
        },
        'dual': {
            'devanagari': 'द्विवचन',
            'iast': 'dvivacana',
            'iso15919': 'dvivacana',
            'english': 'dual',
            'hk': 'dvivacana'
        },

        # Persons
        'first': {
            'devanagari': 'प्रथम पुरुष',
            'iast': 'prathama puruṣa',
            'iso15919': 'prathama puruṣa',
            'english': 'first person',
            'hk': 'prathama puruSa'
        },
        'second': {
            'devanagari': 'मध्यम पुरुष',
            'iast': 'madhyama puruṣa',
            'iso15919': 'madhyama puruṣa',
            'english': 'second person',
            'hk': 'madhyama puruSa'
        },
        'third': {
            'devanagari': 'उत्तम पुरुष',
            'iast': 'uttama puruṣa',
            'iso15919': 'uttama puruṣa',
            'english': 'third person',
            'hk': 'uttama puruSa'
        },

        # Tenses
        'present': {
            'devanagari': 'वर्तमान',
            'iast': 'vartamāna',
            'iso15919': 'vartamāna',
            'english': 'present',
            'hk': 'vartamAna'
        },
        'past': {
            'devanagari': 'भूत',
            'iast': 'bhūta',
            'iso15919': 'bhūta',
            'english': 'past',
            'hk': 'bhUta'
        },
        'future': {
            'devanagari': 'भविष्यत्',
            'iast': 'bhaviṣyat',
            'iso15919': 'bhaviṣyat',
            'english': 'future',
            'hk': 'bhaviSyat'
        },

        # UI Labels
        'root': {
            'devanagari': 'मूल शब्द',
            'iast': 'mūla śabda',
            'iso15919': 'mūla śabda',
            'english': 'root word',
            'hk': 'mUla zabda'
        },
        'form': {
            'devanagari': 'रूप',
            'iast': 'rūpa',
            'iso15919': 'rūpa',
            'english': 'form',
            'hk': 'rUpa'
        },
        'case': {
            'devanagari': 'विभक्ति',
            'iast': 'vibhakti',
            'iso15919': 'vibhakti',
            'english': 'case',
            'hk': 'vibhakti'
        },
        'number': {
            'devanagari': 'वचन',
            'iast': 'vacana',
            'iso15919': 'vacana',
            'english': 'number',
            'hk': 'vacana'
        },
        'gender': {
            'devanagari': 'लिंग',
            'iast': 'liṅga',
            'iso15919': 'liṅga',
            'english': 'gender',
            'hk': 'liGga'
        },
        'tense': {
            'devanagari': 'काल',
            'iast': 'kāla',
            'iso15919': 'kāla',
            'english': 'tense',
            'hk': 'kAla'
        },
        'person': {
            'devanagari': 'पुरुष',
            'iast': 'puruṣa',
            'iso15919': 'puruṣa',
            'english': 'person',
            'hk': 'puruSa'
        },
    }

    def __init__(self):
        """Initialize the converter with caching."""
        self._cache = {}
        self.has_library = HAS_INDIC_TRANSLITERATION

    def hk_to_devanagari(self, text):
        """Convert Harvard-Kyoto text to Devanagari using indic-transliteration library."""
        if not text:
            return text

        if HAS_INDIC_TRANSLITERATION:
            try:
                return transliterate(text, sanscript.HK, sanscript.DEVANAGARI)
            except Exception as e:
                print(f"Error in transliteration: {e}")
                return text
        else:
            # Fallback: return original text with warning
            return text

    def hk_to_iast(self, text):
        """Convert Harvard-Kyoto text to IAST using indic-transliteration library."""
        if not text:
            return text

        if HAS_INDIC_TRANSLITERATION:
            try:
                return transliterate(text, sanscript.HK, sanscript.IAST)
            except Exception as e:
                print(f"Error in transliteration: {e}")
                return text
        else:
            # Fallback to manual conversion
            result = []
            i = 0
            while i < len(text):
                matched = False
                for length in [3, 2, 1]:
                    if i + length <= len(text):
                        substr = text[i:i+length]
                        if substr in self.HK_TO_IAST:
                            result.append(self.HK_TO_IAST[substr])
                            i += length
                            matched = True
                            break
                if not matched:
                    result.append(text[i])
                    i += 1
            return ''.join(result)

    def hk_to_iso(self, text):
        """Convert Harvard-Kyoto text to ISO 15919 using indic-transliteration library."""
        if not text:
            return text

        if HAS_INDIC_TRANSLITERATION:
            try:
                return transliterate(text, sanscript.HK, sanscript.ISO)
            except Exception as e:
                print(f"Error in transliteration: {e}")
                return text
        else:
            # Fallback to manual conversion
            result = []
            i = 0
            while i < len(text):
                matched = False
                for length in [3, 2, 1]:
                    if i + length <= len(text):
                        substr = text[i:i+length]
                        if substr in self.HK_TO_ISO:
                            result.append(self.HK_TO_ISO[substr])
                            i += length
                            matched = True
                            break
                if not matched:
                    result.append(text[i])
                    i += 1
            return ''.join(result)

    def convert(self, text, from_script='hk', to_script='devanagari'):
        """
        Convert text between scripts.

        Args:
            text: The text to convert
            from_script: Source script ('hk', 'devanagari', 'iast', 'iso15919')
            to_script: Target script ('hk', 'devanagari', 'iast', 'iso15919')

        Returns:
            Converted text
        """
        if not text or from_script == to_script:
            return text

        # Check cache
        cache_key = (text, from_script, to_script)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Currently only support conversion from HK
        if from_script != 'hk':
            # For now, return original text if not from HK
            return text

        # Convert from HK to target script
        if to_script == 'devanagari':
            result = self.hk_to_devanagari(text)
        elif to_script == 'iast':
            result = self.hk_to_iast(text)
        elif to_script == 'iso15919':
            result = self.hk_to_iso(text)
        elif to_script == 'hk':
            result = text
        else:
            result = text

        # Cache result
        self._cache[cache_key] = result
        return result

    def convert_grammar_term(self, term_key, to_script='devanagari'):
        """
        Convert grammatical terminology to specified script.

        Args:
            term_key: The grammatical term key (e.g., 'masculine', 'nominative')
            to_script: Target script/language ('devanagari', 'iast', 'iso15919', 'english', 'hk')

        Returns:
            Converted grammatical term
        """
        term_key = term_key.lower()

        if term_key in self.GRAMMAR_TERMS:
            return self.GRAMMAR_TERMS[term_key].get(to_script, term_key)

        return term_key

    def get_available_scripts(self):
        """Return list of available script options."""
        return self.SCRIPTS.copy()


# Convenience functions for direct use
_converter = ScriptConverter()

def convert(text, from_script='hk', to_script='devanagari'):
    """Convert text between scripts."""
    return _converter.convert(text, from_script, to_script)

def convert_term(term_key, to_script='devanagari'):
    """Convert grammatical term to specified script."""
    return _converter.convert_grammar_term(term_key, to_script)


# Test if run directly
if __name__ == '__main__':
    converter = ScriptConverter()

    print("Testing Script Conversion:")
    print("="*60)

    test_words = ['dhamma', 'kamma', 'loka', 'pacAmi', 'gacchati']

    for word in test_words:
        print(f"\nHK: {word}")
        print(f"  Devanagari: {converter.convert(word, 'hk', 'devanagari')}")
        print(f"  IAST: {converter.convert(word, 'hk', 'iast')}")
        print(f"  ISO 15919: {converter.convert(word, 'hk', 'iso15919')}")

    print("\n" + "="*60)
    print("Testing Grammatical Terms:")
    print("="*60)

    test_terms = ['masculine', 'nominative', 'singular', 'present']

    for term in test_terms:
        print(f"\n{term}:")
        print(f"  Devanagari: {converter.convert_grammar_term(term, 'devanagari')}")
        print(f"  IAST: {converter.convert_grammar_term(term, 'iast')}")
        print(f"  English: {converter.convert_grammar_term(term, 'english')}")
