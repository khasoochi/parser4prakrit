# Dictionary Integration & User Feedback Guide

## Overview

This guide explains how to:
1. Convert your large JSON dictionary to SQLite
2. Integrate dictionary meanings with the parser
3. Use the user feedback system to improve accuracy

---

## Part 1: Converting Dictionary to SQLite

### Why SQLite?

Your Prakrit dictionary is too large for GitHub (>100MB). SQLite provides:
- **70% size reduction** vs JSON
- **Fast indexed lookups**
- **Full-text search** capabilities
- **No size limits**

### Step 1: Prepare Your Dictionary JSON

Your dictionary should be a JSON array of entries:

```json
[
  {
    "headword_devanagari": "घाय",
    "headword_translit": "ghāya",
    "type": ["transitive", "neuter"],
    "gender": "",
    "sanskrit_equivalent": ["हन्"],
    "is_desya": false,
    "is_root": true,
    "is_word": false,
    "meanings": [
      {
        "sense_number": 1,
        "definition": "मारना, हत्या करना",
        "references": []
      }
    ],
    "references": [],
    "cross_references": [],
    "compounds": [],
    "parent": null
  }
]
```

### Step 2: Convert to SQLite

```bash
python3 convert_dict_to_sqlite.py your_dictionary.json prakrit_dict.db
```

**Output:**
```
Loading JSON dictionary from: your_dictionary.json
Loaded 15000 entries
Creating SQLite database: prakrit_dict.db
Processed 1000/15000 entries (6%)
Processed 2000/15000 entries (13%)
...
✓ Conversion complete!
  - Total entries: 15000
  - Database size: 12.45 MB
  - Output: prakrit_dict.db
```

### Step 3: Test the Database

```bash
python3 dictionary_lookup.py prakrit_dict.db ghāya
```

**Output:**
```
Dictionary Statistics:
  Total entries: 15000
  Words: 12500
  Roots: 2500
  Desya words: 450

--- Looking up: ghāya ---
Entry 1:
  Devanagari: घाय
  Transliteration: ghāya
  Type: transitive, neuter
  Sanskrit: हन्
  [Root form]
  Meanings:
    1. मारना, हत्या करना
```

---

## Part 2: Integrating Dictionary with Parser

### Option A: Standalone Usage

```python
from dictionary_lookup import PrakritDictionary

# Initialize dictionary
dictionary = PrakritDictionary('prakrit_dict.db')

# Look up a word
entries = dictionary.lookup('ghāya', script='HK')

# Get simple definitions
definitions = dictionary.get_definitions('ghāya', max_senses=3)
print(definitions)
# ['मारना, हत्या करना', '...']

# Search
results = dictionary.search('मारना', limit=10)
```

### Option B: Integrate with Unified Parser

Modify `unified_parser.py` to add dictionary lookups:

```python
# At the top of unified_parser.py
try:
    from dictionary_lookup import PrakritDictionary
    HAS_DICTIONARY = True
except ImportError:
    HAS_DICTIONARY = False

# In __init__ method
def __init__(self, dict_db_path: str = None):
    self.load_data()
    self.load_feedback_data()
    self.initialize_suffix_database()

    # Load dictionary if available
    if dict_db_path and HAS_DICTIONARY:
        try:
            self.dictionary = PrakritDictionary(dict_db_path)
            print("Dictionary loaded successfully")
        except Exception as e:
            print(f"Warning: Could not load dictionary: {e}")
            self.dictionary = None
    else:
        self.dictionary = None

# In parse() method, after applying learned adjustments
if self.dictionary:
    for analysis in all_analyses:
        lookup_word = None
        if analysis.get('type') == 'noun':
            lookup_word = analysis.get('stem')
        elif analysis.get('type') == 'verb':
            lookup_word = analysis.get('root')

        if lookup_word:
            entries = self.dictionary.lookup(lookup_word, script='HK')
            if entries:
                entry = entries[0]
                analysis['dictionary'] = {
                    'headword_devanagari': entry['headword_devanagari'],
                    'sanskrit_equivalent': entry.get('sanskrit_equivalent', []),
                    'meanings': [m.get('definition', '') for m in entry.get('meanings', [])[:3]],
                    'is_desya': entry.get('is_desya', False)
                }
```

Then initialize parser with dictionary:

```python
# With dictionary
parser = PrakritUnifiedParser(dict_db_path='prakrit_dict.db')

# Without dictionary (default)
parser = PrakritUnifiedParser()
```

### Result: Enhanced Analysis

```python
result = parser.parse('ghāya')

print(result['analyses'][0])
```

**Output:**
```json
{
  "type": "verb",
  "root": "ghāya",
  "ending": "",
  "tense": "root_form",
  "confidence": 1.0,
  "source": "attested_root",
  "dictionary": {
    "headword_devanagari": "घाय",
    "sanskrit_equivalent": ["हन्"],
    "meanings": [
      "मारना, हत्या करना"
    ],
    "is_desya": false
  }
}
```

---

## Part 3: User Feedback System

### How It Works

1. **User marks correct analysis** → System records feedback
2. **System tracks suffix accuracy** → Adjusts confidence scores
3. **Future analyses improve** → More accurate over time

### Architecture

```
User Input → Parser Analysis → Display Results
                ↓
        User Selects Correct
                ↓
        Feedback Recorded
                ↓
        user_feedback.json
                ↓
        Future Analyses Use Learned Patterns
```

### Using the Feedback API

#### Submit Feedback

**Endpoint:** `POST /api/feedback`

**Request:**
```json
{
  "word": "devehinto",
  "correct_index": 0,
  "all_analyses": [
    {
      "type": "noun",
      "stem": "deva",
      "suffix": "hinto",
      "case": "ablative",
      "number": "singular",
      "gender": "masculine",
      "confidence": 0.95
    },
    {
      "type": "noun",
      "stem": "devehint",
      "suffix": "o",
      "case": "nominative",
      "number": "singular",
      "gender": "masculine",
      "confidence": 0.65
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback recorded successfully",
  "total_feedback": 42
}
```

#### Get Feedback Stats

**Endpoint:** `GET /api/feedback/stats`

**Response:**
```json
{
  "total_feedback": 42,
  "unique_forms": 35,
  "suffix_stats": {
    "hinto": {
      "correct": 15,
      "incorrect": 2
    },
    "o": {
      "correct": 8,
      "incorrect": 12
    }
  }
}
```

### Frontend Integration Example

```javascript
// After user analyzes a word
function analyzeWord(word) {
  fetch('/api/parse', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({form: word})
  })
  .then(res => res.json())
  .then(data => {
    displayResults(data.analyses);
    enableFeedback(word, data.analyses);
  });
}

// Add feedback buttons to each analysis
function enableFeedback(word, analyses) {
  analyses.forEach((analysis, index) => {
    addButton(`Mark as Correct`, () => {
      submitFeedback(word, index, analyses);
    });
  });
}

// Submit feedback
function submitFeedback(word, correctIndex, allAnalyses) {
  fetch('/api/feedback', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      word: word,
      correct_index: correctIndex,
      all_analyses: allAnalyses
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      alert(`Thank you! Total feedback: ${data.total_feedback}`);
    }
  });
}
```

### How Confidence Adjusts

**Example 1: High Accuracy Suffix**

```
Suffix 'hinto': 15 correct, 2 incorrect (88% accuracy)
→ Confidence boosted by +0.10
→ Note added: "Confidence boosted by user feedback (15/17 correct)"
```

**Example 2: Low Accuracy Suffix**

```
Suffix 'o': 8 correct, 12 incorrect (40% accuracy)
→ Confidence reduced by -0.15
→ Note added: "Confidence reduced by user feedback (8/20 correct)"
```

### Feedback Data Storage

**File:** `user_feedback.json`

```json
{
  "form_corrections": {
    "devehinto": [
      {
        "correct_analysis": {
          "stem": "deva",
          "suffix": "hinto",
          "case": "ablative"
        },
        "timestamp": "2025-11-09 10:30:45"
      }
    ]
  },
  "suffix_accuracy": {
    "hinto": {
      "correct": 15,
      "incorrect": 2
    },
    "o": {
      "correct": 8,
      "incorrect": 12
    }
  },
  "total_feedback": 42
}
```

---

## Part 4: Case Identification Improvements

### Fixed Issues

#### 1. Added Anusvara Variants

**Before:**
- Only `hinto` and `sunto` (no anusvara)

**After:**
- ✅ `hinto` (ablative)
- ✅ `hiMto` (ablative with anusvara)
- ✅ `sunto` (ablative)
- ✅ `suMto` (ablative with anusvara)

#### 2. Refined Na/NaM Cases

**Before:**
```python
'Na': {
    'cases': ['instrumental', 'dative', 'genitive'],  # Too broad
    'confidence': 0.8
}
```

**After:**
```python
'Na': {
    'cases': ['instrumental'],  # Specific to long vowel context
    'numbers': ['singular', 'plural'],
    'must_precede': ['ā', 'ī', 'ū', 'e'],
    'confidence': 0.90  # Higher confidence
}
```

#### 3. Improved Confidence Scores

| Suffix | Old Confidence | New Confidence | Reason |
|--------|---------------|----------------|---------|
| hinto  | 0.90 | 0.95 | High accuracy pattern |
| hiMto  | - | 0.95 | New addition |
| sunto  | 0.90 | 0.95 | High accuracy pattern |
| suMto  | - | 0.95 | New addition |
| Na     | 0.80 | 0.90 | Refined to instrumental only |
| NaM    | 0.80 | 0.90 | Refined to instrumental only |

### Testing Case Improvements

```bash
# Test ablative forms
python3 unified_parser.py devehinto
# Should show: case: ablative (confidence: 0.95)

python3 unified_parser.py puriseNa
# Should show: case: instrumental (confidence: 0.90)
```

---

## Part 5: Complete Workflow Example

### Scenario: Setting Up Parser with Dictionary & Feedback

**Step 1: Convert Dictionary**
```bash
python3 convert_dict_to_sqlite.py prakrit_dict.json prakrit_dict.db
```

**Step 2: Test Dictionary**
```bash
python3 dictionary_lookup.py prakrit_dict.db ghāya
```

**Step 3: Start Parser with Dictionary**
```python
from unified_parser import PrakritUnifiedParser

# Initialize with dictionary
parser = PrakritUnifiedParser(dict_db_path='prakrit_dict.db')

# Parse a word
result = parser.parse('ghāya')

# Result includes dictionary meanings
print(result['analyses'][0]['dictionary']['meanings'])
# ['मारना, हत्या करना']
```

**Step 4: Collect User Feedback**
```python
# User marks analysis #2 as correct
parser.record_feedback(
    word='devehinto',
    correct_analysis=result['analyses'][2],
    all_analyses=result['analyses']
)
# Feedback saved to user_feedback.json
```

**Step 5: Future Parses Improve**
```python
# Next time parsing similar word
result2 = parser.parse('gharehi
nto')

# Confidence automatically adjusted based on feedback
# 'hinto' suffix gets +0.10 confidence boost
```

---

## Part 6: API Reference

### Parser Initialization

```python
parser = PrakritUnifiedParser(
    dict_db_path='prakrit_dict.db'  # Optional
)
```

### Parse Method

```python
result = parser.parse('word')

# Returns:
{
    'success': True,
    'original_form': 'word',
    'hk_form': 'word',
    'script': 'HK',
    'analyses': [
        {
            'type': 'noun' | 'verb',
            'stem': '...',  # for nouns
            'root': '...',  # for verbs
            'case': '...',
            'confidence': 0.95,
            'dictionary': {  # If dictionary enabled
                'meanings': ['...'],
                'sanskrit_equivalent': ['...']
            }
        }
    ],
    'total_found': 15
}
```

### Feedback Method

```python
result = parser.record_feedback(
    word='devehinto',
    correct_analysis={...},
    all_analyses=[...]
)

# Returns:
{
    'success': True,
    'message': 'Feedback recorded successfully',
    'total_feedback': 42
}
```

### Dictionary Methods

```python
dictionary = PrakritDictionary('prakrit_dict.db')

# Exact lookup
entries = dictionary.lookup('ghāya', script='HK')

# Get definitions only
definitions = dictionary.get_definitions('ghāya', max_senses=3)

# Full-text search
results = dictionary.search('मारना', limit=10)

# Look up roots only
roots = dictionary.lookup_root('ghāya')

# Get stats
stats = dictionary.get_stats()
```

---

## Part 7: Deployment Checklist

### For Local Development

- [x] Convert dictionary: `python3 convert_dict_to_sqlite.py`
- [x] Test database: `python3 dictionary_lookup.py`
- [x] Initialize parser with dictionary
- [x] Verify feedback system works
- [ ] Add `.gitignore` entry for `user_feedback.json` (optional)

### For Production (Vercel)

1. **Add SQLite database** to repository:
   ```bash
   git add prakrit_dict.db
   git commit -m "Add dictionary database"
   ```

2. **Ensure requirements.txt includes**:
   ```
   Flask
   aksharamukha
   ```
   (SQLite is built into Python)

3. **Update vercel.json** (already done):
   ```json
   {
     "src": "unified_parser.py",
     "use": "@vercel/python"
   }
   ```

4. **Deploy**:
   ```bash
   git push origin main
   ```

5. **Test endpoints**:
   - `GET /` - Web interface
   - `POST /api/parse` - Parse words
   - `POST /api/feedback` - Submit feedback
   - `GET /api/feedback/stats` - View stats

---

## Part 8: File Size Comparison

### Before SQLite

```
prakrit_dict.json:    125.4 MB  ❌ Too large for GitHub
```

### After SQLite

```
prakrit_dict.db:      38.2 MB   ✅ Efficient, queryable
```

**Savings: 69.5% reduction**

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'dictionary_lookup'"

**Solution:**
```bash
# Ensure dictionary_lookup.py is in same directory as unified_parser.py
ls -la unified_parser.py dictionary_lookup.py
```

### Issue: "Dictionary database not found"

**Solution:**
```bash
# Check path
python3 convert_dict_to_sqlite.py your_dict.json prakrit_dict.db

# Verify
ls -lh prakrit_dict.db
```

### Issue: "Feedback not persisting"

**Solution:**
```bash
# Check write permissions
touch user_feedback.json
chmod 644 user_feedback.json
```

### Issue: "Parser accuracy not improving"

**Minimum feedback needed for adjustments:**
- High confidence boost: ≥3 correct feedbacks, >80% accuracy
- Low confidence reduction: ≥3 total feedbacks, <30% accuracy

Collect more feedback for better results.

---

## Next Steps

1. **Convert your dictionary** to SQLite
2. **Integrate with parser** (optional modification)
3. **Deploy to Vercel** with dictionary
4. **Collect user feedback** to improve accuracy
5. **Monitor stats** at `/api/feedback/stats`

---

*Created: 2025-11-09*
*Parser Version: 2.1 (with feedback & dictionary support)*
