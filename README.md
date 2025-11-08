# Parser4Prakrit

Parser4Prakrit is a Flask web application for analyzing and displaying verb forms in the Prakrit language. It provides a user-friendly interface to input verbs and view their forms, leveraging JSON datasets and custom analysis scripts.

## Features
- Analyze Prakrit verb forms
- Interactive web interface
- JSON-based data storage
- Support for Devanagari and Harvard-Kyoto (HK) transliteration
- Confidence scoring for multiple possible analyses
- Comprehensive input validation and error handling
- Logging for debugging and monitoring

## Recent Improvements (Phase 1)
- ✅ Enhanced code quality with type hints and comprehensive docstrings
- ✅ Added comprehensive logging infrastructure
- ✅ Implemented robust error handling and graceful degradation
- ✅ Added input validation and sanitization for security
- ✅ Created comprehensive test suite with 50+ tests
- ✅ Added test corpus with known correct verb forms

See [PHASE1_IMPROVEMENTS.md](PHASE1_IMPROVEMENTS.md) for detailed information.

## Setup

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/svyoma/parser4prakrit.git
   cd parser4prakrit
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python verb_analyzer.py
   # or
   python app.py
   ```

4. Open your browser to `http://localhost:5001`

### Command Line Usage

You can also analyze verb forms directly from the command line:

```bash
python verb_analyzer.py karomi
```

## Vercel Deployment

This app is configured for deployment on Vercel:

1. Install Vercel CLI (optional):
   ```bash
   npm install -g vercel
   ```

2. Deploy:
   ```bash
   vercel
   ```

3. Configuration:
   - Entry point: `app.py`
   - Build settings are in `vercel.json`
   - Static files served from `static/` and `templates/`

**Note:** The aksharamukha transliteration library is optional. The app will work with Harvard-Kyoto (HK) input even if transliteration is unavailable. For full Devanagari support, you may need to handle transliteration on the client side or use an alternative deployment platform.

## Folder Structure
```
parser4prakrit/
├── app.py                    # Vercel entry point
├── verb_analyzer.py          # Main Flask application
├── input_validation.py       # Input validation module
├── vercel.json              # Vercel configuration
├── requirements.txt         # Python dependencies
├── static/                  # CSS and JS files
│   ├── styles.css
│   └── verb-analyzer.js
├── templates/               # HTML templates
│   └── analyzer.html
├── verbs.json              # Verb root data (LFS)
├── all_verb_forms.json     # Attested verb forms (LFS)
├── test_verb_analyzer.py   # Test suite
├── test_corpus.json        # Test data
└── PHASE1_IMPROVEMENTS.md  # Phase 1 documentation
```

## Data Files

The large JSON data files (`verbs.json` and `all_verb_forms.json`) are stored using Git LFS (Large File Storage):

```bash
# To pull LFS files
git lfs pull
```

## Testing

Run the test suite:

```bash
python test_verb_analyzer.py
# or with pytest
pytest test_verb_analyzer.py -v
```

## API Endpoints

### `GET /`
Returns the main HTML interface.

### `POST /analyze`
Analyzes a Prakrit verb form.

**Request Body:**
- `verb_form` (string): The verb form to analyze (Devanagari or HK)

**Response:**
```json
{
  "results": [
    {
      "original_form": "karomi",
      "script": "hk",
      "analysis": {
        "tense": "present",
        "person": "first",
        "number": "singular",
        "confidence": 1.0
      },
      "potential_root": "kar",
      "ending": "omi",
      "confidence": 0.95,
      "reliability": "High confidence analysis",
      "notes": []
    }
  ]
}
```

## Logging

Logs are written to:
- Console (stdout)
- `prakrit_parser.log` file

Log levels: INFO, DEBUG, WARNING, ERROR

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Future Enhancements (Planned)

### Phase 2: Linguistic Accuracy
- Expand morphological coverage (imperative, optative, conditional)
- Enhanced sandhi rules
- Better phonological validation
- Multi-dialect support (Maharashtri, Shauraseni, Magadhi)
- Improved root identification for irregular verbs

### Phase 3: Advanced Features
- Lemmatization and stemming
- Context-aware analysis
- Machine learning integration
- Corpus building and analysis

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Credits
Created by [svyoma](https://svyoma.github.io/about)

## References
- Pischel, Richard. "Grammatik der Prakrit-Sprachen". 1900.
- Woolner, Alfred C. "Introduction to Prakrit". 1928.
- Tagare, G.V. "Historical Grammar of Apabhramsha". 1948.
