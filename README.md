# प्राकृत शब्द खेल (Prakrit Word Games)

A unified desktop application for learning Prakrit language through 5 integrated educational games.

## Features

### 🎮 Five Game Modes

1. **रूप प्रश्नोत्तरी (Form Quiz)** - Type the correct inflected form based on root word and grammatical specifications
2. **शब्द पहचान (Word Identification)** - Identify the root word and grammatical features from an inflected form
3. **तालिका पूर्ति (Paradigm Completion)** - Fill in missing cells in declension/conjugation tables
4. **द्रुत अभ्यास (Speed Drill)** - Rapid-fire timed questions with combo multipliers
5. **मिलान खेल (Matching Game)** - Match inflected forms with their grammatical descriptions

### 📝 Script Support

The application supports multiple writing systems with seamless conversion:
- **Devanagari** (Default) - देवनागरी
- **IAST** - International Alphabet of Sanskrit Transliteration
- **ISO 15919** - International standard
- **Harvard-Kyoto** - ASCII-compatible transliteration

All database content is stored in Harvard-Kyoto format and dynamically converted to your preferred script.

### ⚙️ Customization

- **Difficulty Levels**: Easy, Medium, Hard
- **Script Preferences**: Change display script on the fly
- **Grammatical Terminology**: Choose between Devanagari, Roman, or English terms
- **Progress Tracking**: Track score, streak, and accuracy across all games
- **Adjustable Font Size**: 12-24pt range for comfortable reading

## Installation

### Requirements

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   This will install:
   - `indic-transliteration` - For script conversion
   - `PyQt5` - For the graphical interface

3. **Verify database files:**

   The application includes sample database files in `data/`:
   - `verb_forms.db` - Prakrit verb conjugations
   - `noun_forms.db` - Prakrit noun declensions

   **Note**: These are sample databases created for demonstration. Replace them with actual Prakrit database files when available.

## Usage

### Running the Application

```bash
python3 main.py
```

Or make it executable:
```bash
chmod +x main.py
./main.py
```

### Quick Start

1. Launch the application
2. Select a script preference from the dropdown (Default: Devanagari)
3. Choose a difficulty level
4. Click on any game button to start playing
5. Track your progress in the status bar at the bottom

### Game Controls

#### Game 1: Form Quiz
- Type your answer in the text box
- Press Enter or click "Check Answer"
- Use the Hint button for assistance
- Click "Next Question" to continue

#### Game 2: Word Identification
- Select the root word from multiple choices
- Choose the correct grammatical features
- Click "Check Answer" to verify
- Click "Next Question" for a new challenge

#### Game 3: Paradigm Completion
- Fill in the empty (yellow) cells in the table
- Leave pre-filled (green) cells as they are
- Click "Check Answers" when complete
- Incorrect cells will turn red with tooltips showing correct answers

#### Game 4: Speed Drill
- Click "Start Sprint" to begin 2-minute timed mode
- Type answers quickly to build combo multipliers
- Skip questions for -5 points penalty
- Race against time to answer 50 questions

#### Game 5: Matching Game
- Click an item on the left, then its match on the right
- Matched pairs turn blue
- Click "Clear Matches" to reset
- Click "Check Matches" to verify all connections

## Database Structure

### Verb Database (`verb_forms.db`)

**Tables:**
- `verbs`: id, root (HK), meaning, transitivity, difficulty
- `verb_forms`: id, verb_id, tense, person, number, form (HK)

**Example:**
```
Root: pac (to cook)
Form: pacAmi (I cook) - present, first person, singular
```

### Noun Database (`noun_forms.db`)

**Tables:**
- `nouns`: id, root (HK), meaning, gender, difficulty
- `noun_forms`: id, noun_id, case_name, number, form (HK)

**Example:**
```
Root: dhamma (dharma/law)
Form: dhammo - nominative, singular
Form: dhammeNa - instrumental, singular
```

## Project Structure

```
prakrit-game/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── core/                  # Core functionality
│   ├── __init__.py
│   ├── db_handler.py      # Database operations with script conversion
│   └── script_converter.py # HK ↔ Devanagari/IAST/ISO conversion
│
├── ui/                    # User interface components
│   ├── __init__.py
│   ├── main_window.py     # Main application window
│   ├── game1_form_quiz.py
│   ├── game2_identification.py
│   ├── game3_paradigm.py
│   ├── game4_speed_drill.py
│   └── game5_matching.py
│
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── settings.py        # Settings management
│   ├── create_sample_dbs.py # Database creation script
│   └── analyze_dbs.py     # Database analysis tool
│
├── data/                  # Data files
│   ├── verb_forms.db      # Verb conjugation database
│   ├── noun_forms.db      # Noun declension database
│   └── settings.json      # User settings (created on first run)
│
└── resources/             # Resources (fonts, sounds, icons)
    ├── fonts/
    ├── sounds/
    └── icons/
```

## Script Conversion Details

All Prakrit words are stored in Harvard-Kyoto (HK) transliteration in the database. The application uses the `indic-transliteration` library to convert between scripts:

**Harvard-Kyoto → Devanagari:**
- `dhamma` → धम्म
- `pacAmi` → पचामि
- `kamma` → कम्म

**Harvard-Kyoto → IAST:**
- `dhamma` → dhamma
- `pacAmi` → pacāmi
- `dhammeNa` → dhammeṇa

**Harvard-Kyoto → ISO 15919:**
- `loka` → lōka
- `gacchati` → gacchati

## Replacing Sample Data

To use your own Prakrit databases:

1. Place your `verb_forms.db` and `noun_forms.db` files in the `data/` directory
2. Ensure they follow the same schema as the sample databases
3. All word forms must be in Harvard-Kyoto (HK) transliteration
4. Restart the application

To analyze your database structure:
```bash
python3 -m utils.analyze_dbs
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'indic_transliteration'"
Install dependencies: `pip install -r requirements.txt`

### "Database not found" error
Ensure `verb_forms.db` and `noun_forms.db` exist in the `data/` directory

### Devanagari text not displaying correctly
Install a Unicode-compatible font like "Noto Sans Devanagari" on your system

### Games not loading
Check console for error messages. Ensure all game files are in the `ui/` directory

## Development

### Creating New Databases

Use the provided script to create sample databases:
```bash
python3 utils/create_sample_dbs.py
```

### Analyzing Databases

View database structure and sample data:
```bash
python3 utils/analyze_dbs.py
```

### Testing Components

Test individual components:
```bash
# Test script converter
python3 -m core.script_converter

# Test database handler
python3 -m core.db_handler

# Test settings
python3 -m utils.settings
```

## Technical Details

- **Framework**: PyQt5 for cross-platform GUI
- **Database**: SQLite for efficient data storage
- **Script Conversion**: indic-transliteration library
- **Language**: Python 3.7+

## Future Enhancements

Potential features for future versions:
- Audio pronunciation support
- User profile management
- Statistics dashboard with charts
- Achievement system
- Export progress data
- Dark theme
- More game variations
- Verb class filtering
- Noun stem type filtering

## Credits

- Script conversion powered by `indic-transliteration` library
- GUI built with PyQt5
- Sample Prakrit data based on Pali grammar patterns

## License

This educational application is provided as-is for learning purposes.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Verify all dependencies are installed
3. Ensure database files are in the correct format
4. Check that you're using Python 3.7 or higher

---

Happy learning! शुभं भवतु (śubhaṃ bhavatu) ✨
