# User Feedback Guide

The Prakrit parser has a built-in learning system that improves accuracy based on user corrections.

## How It Works

When you analyze a word, the parser may return multiple possible analyses ranked by confidence. If the correct analysis is not at the top, you can provide feedback to help the parser learn.

The feedback system:
- Records which analysis was correct for each word
- Tracks suffix/ending accuracy statistics
- Automatically adjusts confidence scores for future analyses
- Saves feedback to `user_feedback.json` (gitignored)

## Providing Feedback via API

### Endpoint: POST `/api/feedback`

**Request Body:**
```json
{
  "word": "muNinti",
  "correct_index": 0,
  "all_analyses": [
    {
      "form": "muNinti",
      "root": "muN",
      "ending": "nti",
      "type": "verb",
      "tense": "present",
      "person": "third",
      "number": "plural",
      "confidence": 1.0
    }
  ]
}
```

**Parameters:**
- `word` (string): The Prakrit word being analyzed
- `correct_index` (integer): Index of the correct analysis (0-based)
- `all_analyses` (array): All analyses returned by the parser

**Response:**
```json
{
  "success": true,
  "message": "Feedback recorded successfully",
  "total_feedback": 42
}
```

### Example with cURL:

```bash
curl -X POST http://localhost:5000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "word": "Nemo",
    "correct_index": 0,
    "all_analyses": [
      {
        "form": "Nemo",
        "root": "NI",
        "ending": "mo",
        "type": "verb",
        "source": "sandhi_analysis",
        "confidence": 1.0
      }
    ]
  }'
```

### Example with Python:

```python
import requests
import json

# Parse a word
response = requests.get('http://localhost:5000/api/parse?word=muNinti')
result = response.json()

# User confirms analysis #2 is correct
feedback = {
    'word': 'muNinti',
    'correct_index': 1,  # 0-based index
    'all_analyses': result['analyses']
}

# Submit feedback
feedback_response = requests.post(
    'http://localhost:5000/api/feedback',
    json=feedback
)
print(feedback_response.json())
```

## Viewing Feedback Statistics

### Endpoint: GET `/api/feedback/stats`

**Response:**
```json
{
  "total_feedback": 42,
  "unique_forms": 28,
  "suffix_stats": {
    "nti": {
      "correct": 15,
      "incorrect": 2
    },
    "mo": {
      "correct": 8,
      "incorrect": 1
    }
  }
}
```

## How Feedback Improves the Parser

1. **Suffix Confidence Adjustment**: If a suffix gets confirmed correct multiple times (>80% accuracy with ≥3 samples), its confidence is boosted by +0.10. If it's frequently wrong (<30% accuracy with ≥3 samples), confidence is reduced by -0.15.

2. **Form Corrections**: The parser remembers corrections for specific words, so repeated analyses of the same word benefit from previous feedback.

3. **Learning Over Time**: As more feedback is collected, the parser automatically becomes better at ranking analyses correctly.

## Feedback Data Storage

Feedback is stored in `user_feedback.json` with this structure:

```json
{
  "form_corrections": {
    "muNinti": [
      {
        "correct_analysis": {
          "root": "muN",
          "ending": "nti",
          ...
        },
        "timestamp": "2025-01-09 12:34:56"
      }
    ]
  },
  "suffix_accuracy": {
    "nti": {
      "correct": 15,
      "incorrect": 2
    }
  },
  "total_feedback": 42
}
```

## Adding a Feedback UI (Optional)

To add user feedback to the web interface, you can modify `templates/unified_analyzer.html` to include feedback buttons:

```html
<div class="feedback-section">
  <p>Is this analysis correct?</p>
  <button onclick="submitFeedback(analysisIndex, true)">✓ Correct</button>
  <button onclick="submitFeedback(analysisIndex, false)">✗ Incorrect</button>
</div>

<script>
function submitFeedback(correctIndex, isCorrect) {
  if (!isCorrect) return; // Only submit if marked correct

  fetch('/api/feedback', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      word: currentWord,
      correct_index: correctIndex,
      all_analyses: allAnalyses
    })
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      alert('Thank you for your feedback!');
    }
  });
}
</script>
```

## Best Practices

1. **Mark only one analysis as correct** - The feedback system expects exactly one correct analysis per word
2. **Provide context** - If a word has multiple valid interpretations, choose the one that fits your specific context
3. **Be consistent** - Try to use the same criteria when marking analyses as correct
4. **Review regularly** - Check `/api/feedback/stats` to see which suffixes need more training data

## Privacy Note

All feedback data is stored locally in `user_feedback.json`. This file is listed in `.gitignore` and will not be committed to version control, ensuring your corrections remain private.
