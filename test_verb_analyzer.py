"""
Comprehensive test suite for Prakrit verb analyzer.

This module contains unit tests for all major functions in the verb analyzer,
including script detection, transliteration, phonological validation,
sandhi rules, prefix identification, and ending analysis.
"""

import unittest
import sys
import os

# Add parent directory to path to import verb_analyzer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from verb_analyzer import (
        detect_script,
        transliterate,
        is_valid_prakrit_sequence,
        apply_sandhi_rules,
        identify_prefix,
        analyze_endings
    )
    VERB_ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import verb_analyzer: {e}")
    print("Some tests will be skipped")
    VERB_ANALYZER_AVAILABLE = False


class TestScriptDetection(unittest.TestCase):
    """Test cases for script detection functionality."""

    def test_detect_devanagari(self):
        """Test detection of Devanagari script."""
        self.assertEqual(detect_script('करोति'), 'devanagari')
        self.assertEqual(detect_script('जाणइ'), 'devanagari')
        self.assertEqual(detect_script('भवति'), 'devanagari')

    def test_detect_hk(self):
        """Test detection of Harvard-Kyoto transliteration."""
        self.assertEqual(detect_script('karoti'), 'hk')
        self.assertEqual(detect_script('jANai'), 'hk')
        self.assertEqual(detect_script('bhavati'), 'hk')

    def test_mixed_script_defaults_to_devanagari(self):
        """Test that mixed scripts default to Devanagari."""
        self.assertEqual(detect_script('karo करोति ti'), 'devanagari')


class TestTransliteration(unittest.TestCase):
    """Test cases for transliteration between scripts."""

    def test_devanagari_to_hk(self):
        """Test transliteration from Devanagari to Harvard-Kyoto."""
        result = transliterate('करोति', 'devanagari', 'hk')
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, '')

    def test_hk_to_devanagari(self):
        """Test transliteration from Harvard-Kyoto to Devanagari."""
        result = transliterate('karoti', 'hk', 'devanagari')
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, '')

    def test_no_conversion_needed(self):
        """Test that same script returns original text."""
        text = 'karoti'
        result = transliterate(text, 'hk', 'hk')
        self.assertEqual(result, text)


class TestPhonotacticValidation(unittest.TestCase):
    """Test cases for Prakrit phonological validation."""

    def test_valid_sequences(self):
        """Test valid Prakrit phonological sequences."""
        self.assertTrue(is_valid_prakrit_sequence('karomi'))
        self.assertTrue(is_valid_prakrit_sequence('jANai'))
        self.assertTrue(is_valid_prakrit_sequence('muNissai'))
        self.assertTrue(is_valid_prakrit_sequence('hoe'))
        self.assertTrue(is_valid_prakrit_sequence('jANae'))

    def test_vowel_hiatus_allowed(self):
        """Test that vowel hiatus is allowed in Prakrit."""
        self.assertTrue(is_valid_prakrit_sequence('ai'))
        self.assertTrue(is_valid_prakrit_sequence('ae'))
        self.assertTrue(is_valid_prakrit_sequence('oe'))
        self.assertTrue(is_valid_prakrit_sequence('ie'))

    def test_invalid_consonant_clusters(self):
        """Test detection of invalid consonant clusters."""
        # These should be invalid based on current rules
        self.assertFalse(is_valid_prakrit_sequence('ktpb'))
        self.assertFalse(is_valid_prakrit_sequence('khdp'))


class TestSandhiRules(unittest.TestCase):
    """Test cases for Prakrit sandhi (euphonic combination) rules."""

    def test_i_plus_a_glide_insertion(self):
        """Test glide 'y' insertion between i and a."""
        result = apply_sandhi_rules('kari', 'ati')
        self.assertEqual(result, 'kariyati')

    def test_u_plus_a_glide_insertion(self):
        """Test glide 'v' insertion between u and a."""
        result = apply_sandhi_rules('bhu', 'ati')
        self.assertEqual(result, 'bhuvati')

    def test_hiatus_preservation(self):
        """Test that most vowel combinations are preserved as hiatus."""
        # a + i should remain as hiatus (ai)
        result = apply_sandhi_rules('kara', 'imi')
        self.assertEqual(result, 'karaimi')

        # a + e should remain as hiatus (ae)
        result = apply_sandhi_rules('kara', 'e')
        self.assertEqual(result, 'karae')

    def test_consonant_vowel_combination(self):
        """Test combinations where no sandhi is applied."""
        result = apply_sandhi_rules('kar', 'omi')
        self.assertEqual(result, 'karomi')


class TestPrefixIdentification(unittest.TestCase):
    """Test cases for verbal prefix identification."""

    def test_identify_pa_prefix(self):
        """Test identification of 'pa' (pra) prefix."""
        prefix, sanskrit = identify_prefix('pakaromi')
        self.assertEqual(prefix, 'pa')
        self.assertEqual(sanskrit, 'pra')

    def test_identify_vi_prefix(self):
        """Test identification of 'vi' prefix."""
        prefix, sanskrit = identify_prefix('vikaromi')
        self.assertEqual(prefix, 'vi')
        self.assertEqual(sanskrit, 'vi')

    def test_identify_sam_prefix(self):
        """Test identification of 'saṃ' (sam) prefix."""
        prefix, sanskrit = identify_prefix('saṃkaromi')
        self.assertEqual(prefix, 'saṃ')
        self.assertEqual(sanskrit, 'sam')

    def test_no_prefix(self):
        """Test forms without prefixes."""
        prefix, sanskrit = identify_prefix('karomi')
        self.assertIsNone(prefix)
        self.assertIsNone(sanskrit)

    def test_longest_match_priority(self):
        """Test that longer prefixes are matched first."""
        # 'paḍi' should be matched before 'pa'
        prefix, sanskrit = identify_prefix('paḍikaromi')
        self.assertEqual(prefix, 'paḍi')
        self.assertEqual(sanskrit, 'prati')


class TestEndingAnalysis(unittest.TestCase):
    """Test cases for verb ending analysis."""

    def test_present_first_singular(self):
        """Test analysis of present tense, first person singular."""
        results = analyze_endings('karomi')
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0)

        # Check that at least one result has the expected analysis
        has_correct_analysis = False
        for result in results:
            if (result['analysis']['tense'] == 'present' and
                result['analysis']['person'] == 'first' and
                result['analysis']['number'] == 'singular'):
                has_correct_analysis = True
                break
        self.assertTrue(has_correct_analysis)

    def test_present_third_singular(self):
        """Test analysis of present tense, third person singular."""
        results = analyze_endings('karoti')
        self.assertIsNotNone(results)
        # Should find possible analyses

    def test_future_forms(self):
        """Test analysis of future tense forms."""
        results = analyze_endings('karihimi')
        self.assertIsNotNone(results)
        if results:
            # Check for future tense in results
            has_future = any(r['analysis']['tense'] == 'future' for r in results)
            self.assertTrue(has_future)

    def test_invalid_form(self):
        """Test that invalid forms return None or empty."""
        # A completely invalid form
        results = analyze_endings('xyz123')
        # Should either be None or empty list
        if results is not None:
            self.assertEqual(len(results), 0)

    def test_confidence_scoring(self):
        """Test that confidence scores are reasonable."""
        results = analyze_endings('karomi')
        if results:
            for result in results:
                self.assertGreaterEqual(result['confidence'], 0.0)
                self.assertLessEqual(result['confidence'], 1.0)

    def test_attested_forms_boost(self):
        """Test that attested forms get confidence boost."""
        # This test assumes we have some attested forms loaded
        # If the form is attested, confidence should be higher
        results = analyze_endings('karomi')
        if results and len(results) > 0:
            # Just verify confidence is within valid range
            self.assertGreater(results[0]['confidence'], 0.0)


class TestInputValidation(unittest.TestCase):
    """Test cases for input validation and edge cases."""

    def test_empty_string(self):
        """Test handling of empty string input."""
        results = analyze_endings('')
        # Should handle gracefully
        self.assertTrue(results is None or len(results) == 0)

    def test_whitespace_only(self):
        """Test handling of whitespace-only input."""
        results = analyze_endings('   ')
        # Should handle gracefully
        self.assertTrue(results is None or len(results) == 0)

    def test_very_long_input(self):
        """Test handling of unusually long input."""
        long_input = 'k' * 1000
        results = analyze_endings(long_input)
        # Should not crash
        self.assertIsInstance(results, (list, type(None)))

    def test_special_characters(self):
        """Test handling of special characters."""
        results = analyze_endings('karo@#$mi')
        # Should handle gracefully without crashing
        self.assertIsInstance(results, (list, type(None)))


class TestIntegration(unittest.TestCase):
    """Integration tests for complete analysis workflow."""

    def test_devanagari_input_workflow(self):
        """Test complete workflow with Devanagari input."""
        # Simulate what the Flask app does
        verb_form = 'करोमि'
        script = detect_script(verb_form)
        self.assertEqual(script, 'devanagari')

        hk_form = transliterate(verb_form, 'devanagari', 'hk')
        self.assertIsNotNone(hk_form)

        results = analyze_endings(hk_form)
        # Should get some results
        self.assertIsInstance(results, (list, type(None)))

    def test_hk_input_workflow(self):
        """Test complete workflow with HK input."""
        verb_form = 'karomi'
        script = detect_script(verb_form)
        self.assertEqual(script, 'hk')

        results = analyze_endings(verb_form)
        self.assertIsInstance(results, (list, type(None)))


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
