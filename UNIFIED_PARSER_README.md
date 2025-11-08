# Unified Prakrit Parser - Version 2.0

## Overview

The Unified Prakrit Parser is a comprehensive, holistic parsing system that combines both **verb** and **noun** analysis into a single, intelligent engine. This parser implements advanced linguistic rules, suffix priority algorithms, and ending-based guessing to provide accurate morphological analysis of Prakrit words.

## Key Features

### 1. **Unified Analysis**
- Single parser handles both verbs and nouns
- Automatic detection of form type (verb vs. noun)
- Returns ranked analyses sorted by confidence score

### 2. **Intelligent Suffix Matching**
- **Longest-match-first algorithm**: Prioritizes longer suffixes (e.g., "hinto" over "o")
- **Blocking rules**: Prevents incorrect short-suffix matches when longer suffixes are present
- **Context validation**: Ensures preceding vowels match suffix requirements

### 3. **Ending-Based Guessing**
- Analyzes forms not found in JSON databases
- Uses comprehensive suffix patterns to guess grammatical properties
- Provides confidence scores for each analysis

### 4. **Comprehensive Suffix Database**

#### Noun Suffixes (Examples)
| Suffix | Case | Number | Genders | Priority | Example |
|--------|------|--------|---------|----------|---------|
| hinto | Ablative | Sg/Pl | M/F/N | 5 | devehinto |
| sunto | Ablative | Plural | M/F/N | 5 | devasunto |
| ssa | Dative/Genitive | Singular | M/N | 3 | purisassa |
| mmi | Locative | Singular | M/N | 3 | purisammi |
| hi/hiM | Instrumental | Plural | M/F/N | 2-3 | purisehi |

#### Verb Endings (Examples)
| Ending | Person | Number | Tense | Priority | Example |
|--------|--------|--------|-------|----------|---------|
| mi | First | Singular | Present | 2 | karomi |
| nti | Third | Plural | Present | 3 | karonti |
| himi | First | Singular | Future | 4 | karihimi |
| sI | All | All | Past | 2 | karasI |

### 5. **Error Handling**
- Validates Prakrit characters (rejects visarga, retroflex R, etc.)
- Provides clear error messages
- Suggests corrections for common mistakes

## Fixes from Previous Version

### Critical Issues Resolved

1. **Suffix Priority Bug (devehinto issue)**
   - **Problem**: "devehinto" was incorrectly parsed as "devehint" + "o"
   - **Solution**: Implemented longest-match-first with blocking rules
   - **Result**: Now correctly identifies "deve" + "hinto" (ablative)

2. **Missing Ending-Based Guessing**
   - **Problem**: Forms not in JSON returned no results
   - **Solution**: Comprehensive suffix pattern matching for all forms
   - **Result**: Parser can now analyze unknown forms with confidence scores

3. **Separated Verb/Noun Logic**
   - **Problem**: Two separate analyzers with duplicated code
   - **Solution**: Unified parser with shared infrastructure
   - **Result**: Consistent analysis, easier maintenance

4. **No Stem Reconstruction**
   - **Problem**: Parser couldn't reconstruct stems from inflected forms
   - **Solution**: Implemented smart stem reconstruction based on suffix type
   - **Result**: Accurate stem extraction for all genders

## Architecture

### Class: `PrakritUnifiedParser`

#### Key Methods

```python
load_data()
```
Loads verb and noun dictionaries from JSON files

```python
initialize_suffix_database()
```
Sets up comprehensive suffix patterns with priorities and blocking rules

```python
parse(text: str) -> Dict
```
Main entry point - analyzes input and returns all possible interpretations

```python
find_suffix_matches(word: str, suffix_dict: Dict) -> List[Dict]
```
Finds all matching suffixes with priority ordering and blocking

```python
reconstruct_noun_stem(base: str, suffix: str, gender: str) -> str
```
Reconstructs original noun stem from inflected form

```python
analyze_as_noun(word_hk: str) -> List[Dict]
```
Performs noun analysis with ending-based guessing

```python
analyze_as_verb(word_hk: str) -> List[Dict]
```
Performs verb analysis with ending-based guessing

## Usage

### Command Line

```bash
python unified_parser.py devehinto
```

Output:
```
=== Analysis for: devehinto ===
Harvard-Kyoto: devehinto
Script: HK

Found 3 possible analyses (showing top 3):

--- Analysis 1 (confidence: 0.95) ---
Type: noun
Stem: deva
Suffix: hinto
Gender: masculine
Case: ablative
Number: singular
Source: ending_based_guess
Notes: Ending-based analysis: suffix 'hinto' suggests ablative singular
```

### Web API

```python
from unified_parser import parser

result = parser.parse("karoti")
print(result)
```

Output:
```json
{
  "success": true,
  "original_form": "karoti",
  "hk_form": "karoti",
  "script": "HK",
  "analyses": [
    {
      "form": "karoti",
      "root": "kar",
      "ending": "ti",
      "tense": "present",
      "person": "third",
      "number": "singular",
      "type": "verb",
      "source": "ending_based_guess",
      "confidence": 0.95
    }
  ]
}
```

### Flask Server

```bash
python unified_parser.py
```

Then visit: `http://localhost:5000`

## API Endpoints

### POST /api/parse
Analyzes a Prakrit word or form

**Request:**
```json
{
  "form": "devehinto"
}
```

**Response:**
```json
{
  "success": true,
  "original_form": "devehinto",
  "hk_form": "devehinto",
  "script": "HK",
  "analyses": [...],
  "total_found": 3
}
```

### POST /api/analyze
Backward-compatible endpoint for verb analysis only

## Web Interface

The unified parser includes a modern, responsive web interface with:

- **Tab-based filtering**: View all analyses, verbs only, or nouns only
- **Confidence badges**: Visual indicators for analysis quality
- **Copy/Export**: Easy data export in JSON format
- **Devanagari support**: Input and display in both scripts
- **Mobile-friendly**: Responsive design for all devices

## Improvement Summary

| Aspect | Old Version | New Version |
|--------|-------------|-------------|
| Suffix Matching | Simple string matching | Priority-based with blocking |
| Unknown Forms | No analysis | Ending-based guessing |
| Verb & Noun | Separate analyzers | Unified parser |
| Stem Reconstruction | Limited | Full reconstruction |
| UI | Basic | Modern, tabbed interface |
| Confidence Scoring | Binary (yes/no) | Graduated (0.0-1.0) |

## Testing

### Example Test Cases

```python
# Test 1: Multi-character suffix priority
assert parser.parse("devehinto")['analyses'][0]['suffix'] == 'hinto'

# Test 2: Verb with attested root
result = parser.parse("karoti")
assert result['analyses'][0]['root'] == 'kar'

# Test 3: Noun with proper gender detection
result = parser.parse("puriso")
assert result['analyses'][0]['gender'] == 'masculine'

# Test 4: Devanagari input
result = parser.parse("करोति")
assert result['success'] == True
```

## Dependencies

```
Flask==2.3.0
aksharamukha==1.0.0  # Optional, for transliteration
```

Install with:
```bash
pip install flask aksharamukha
```

## File Structure

```
/home/user/parser4prakrit/
├── unified_parser.py                # Main unified parser
├── templates/
│   └── unified_analyzer.html        # Web interface
├── verbs1.json                      # Verb root dictionary
├── all_verb_forms.json              # Attested verb forms
├── all_noun_forms.json              # Attested noun forms
└── UNIFIED_PARSER_README.md         # This file
```

## Future Enhancements

- [ ] Sandhi rule application for compound analysis
- [ ] Support for verbal prefixes (pra-, pari-, sam-, etc.)
- [ ] Imperative and optative mood analysis
- [ ] Multi-dialect support (Maharashtri, Shauraseni, Magadhi)
- [ ] Machine learning-based confidence adjustment
- [ ] Corpus frequency data integration

## Credits

**Author**: Vyom A. Shah (svyoma)
**Version**: 2.0
**Date**: November 2025
**License**: MIT

## References

- Pischel, R. (1900). *Grammar of the Prakrit Languages*
- Documentation in `instructions.mkdown` and `finetune.mkdown`
- Phase 1 improvements: `PHASE1_IMPROVEMENTS.md`

---

For bug reports and feature requests, please visit:
https://github.com/khasoochi/parser4prakrit/issues
