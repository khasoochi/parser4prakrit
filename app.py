"""
Flask application entry point for Vercel deployment.

This module creates a serverless-compatible Flask app for Vercel.
"""

# Import Flask and other dependencies first
from flask import Flask, render_template, request, jsonify
import re
import json
import os
import sys
from typing import Optional, Dict, List, Set, Tuple, Any

# Disable file logging in serverless environment
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]  # Only log to stdout
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Load data - import functions from verb_analyzer
try:
    from verb_analyzer import (
        detect_script,
        transliterate,
        is_valid_prakrit_sequence,
        apply_sandhi_rules,
        identify_prefix,
        analyze_endings,
        VERB_ROOTS,
        ALL_VERB_FORMS,
        INPUT_VALIDATION_AVAILABLE
    )

    if INPUT_VALIDATION_AVAILABLE:
        from input_validation import validate_and_sanitize
    else:
        validate_and_sanitize = None

    logger.info("Successfully imported verb_analyzer functions")
except Exception as e:
    logger.error(f"Error importing verb_analyzer: {e}")
    # Create minimal stubs if import fails
    def detect_script(text: str) -> str:
        return 'hk'
    def analyze_endings(text: str) -> None:
        return None
    VERB_ROOTS = set()
    ALL_VERB_FORMS = {}
    INPUT_VALIDATION_AVAILABLE = False
    validate_and_sanitize = None

@app.route('/')
def index():
    """Main page route."""
    return render_template('analyzer.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze verb form endpoint."""
    verb_form = request.form.get('verb_form', '')

    if not verb_form:
        logger.warning("Empty verb form received")
        return jsonify({"error": "Please provide a verb form"}), 400

    # Validate and sanitize input
    if INPUT_VALIDATION_AVAILABLE and validate_and_sanitize:
        try:
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
        except Exception as e:
            logger.warning(f"Validation error: {e}")

    logger.info(f"Analyzing verb form: {verb_form}")

    try:
        # Detect script
        detected_script = detect_script(verb_form)
        logger.debug(f"Detected script: {detected_script}")

        working_form = verb_form

        # Handle transliteration if needed
        if detected_script == 'devanagari':
            try:
                working_form = transliterate(verb_form, 'devanagari', 'hk')
                logger.debug(f"Transliterated to HK: {working_form}")
            except Exception as e:
                logger.warning(f"Transliteration failed: {e}")
                return jsonify({
                    "error": "Devanagari input requires transliteration support. Please use Harvard-Kyoto (HK) transliteration.",
                    "suggestions": [
                        "Use Harvard-Kyoto transliteration (e.g., 'karomi' instead of 'करोमि')",
                        "Refer to HK transliteration guide"
                    ]
                }), 400

        # Preprocess HK input
        if detected_script == 'hk' or (detected_script == 'devanagari' and working_form):
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

        # Build results
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

            # Add explanatory notes
            notes = []
            if analysis.get('prefix'):
                notes.append(f"Found verbal prefix '{analysis['prefix']}' (Sanskrit: '{analysis['sanskrit_prefix']}')")
            if analysis.get('sandhi_applied'):
                notes.append("Sandhi rules were applied in this analysis")
            if analysis['analysis']['tense'] == 'past' and analysis['analysis']['person'] == 'all':
                notes.append("Note: Past tense forms in Prakrit are the same for all persons and numbers")
            result['notes'] = notes

            if detected_script == 'devanagari':
                result["hk_form"] = working_form

            results.append(result)

        logger.info(f"Successfully analyzed {verb_form}: {len(results)} result(s)")
        return jsonify({"results": results})

    except Exception as e:
        logger.error(f"Error analyzing {verb_form}: {e}", exc_info=True)
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Health check endpoint
@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "verb_roots_loaded": len(VERB_ROOTS),
        "attested_forms_loaded": len(ALL_VERB_FORMS)
    })

if __name__ == "__main__":
    # This won't run on Vercel, but useful for local testing
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
