# Quick Start Guide

## Installation & Running

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Run the Application
```bash
python3 main.py
```

## First Time Setup

1. **Choose Your Script** - Select from the dropdown at the top:
   - Devanagari (Default) - देवनागरी
   - IAST - International transliteration
   - ISO 15919 - ISO standard
   - Harvard-Kyoto - ASCII format

2. **Select Difficulty** - Choose Easy, Medium, or Hard

3. **Pick a Game** - Click any of the 5 game buttons

## Game Summary

| Game | Description | Best For |
|------|-------------|----------|
| **Game 1: Form Quiz** | Type the correct form | Learning specific forms |
| **Game 2: Word ID** | Identify root & grammar | Recognition practice |
| **Game 3: Paradigm** | Fill declension tables | Systematic learning |
| **Game 4: Speed Drill** | Timed rapid questions | Speed & fluency |
| **Game 5: Matching** | Match forms & descriptions | Pattern recognition |

## Quick Tips

- **Start with Game 1** (Form Quiz) on Easy difficulty
- Use the **Hint button** when stuck
- Watch your **combo multiplier** in Speed Drill
- Track your **accuracy** in the status bar
- Settings are **saved automatically**

## Keyboard Shortcuts

- **Enter** - Submit answer / Check answer
- **Tab** - Navigate between fields

## Sample Data Note

⚠️ **Important**: This application currently uses sample Prakrit data for demonstration.

To use real Prakrit databases:
1. Place your `verb_forms.db` and `noun_forms.db` in the `data/` directory
2. Ensure they use Harvard-Kyoto (HK) transliteration
3. Follow the schema shown in README.md
4. Restart the application

## Troubleshooting

### Application won't start
```bash
# Check Python version (need 3.7+)
python3 --version

# Reinstall dependencies
pip3 install --force-reinstall -r requirements.txt
```

### Can't see Devanagari text
- Install a Unicode font like "Noto Sans Devanagari"
- Restart the application

### Games not loading
- Check terminal/console for error messages
- Verify database files exist in `data/` directory

## What's Included

✅ **Core Features**
- 5 fully functional games
- Multi-script support (4 scripts)
- Script conversion engine
- Settings management
- Progress tracking
- Sample databases with 10 verbs, 10 nouns

✅ **Phase 1 & 2 Complete**
- Project structure
- Database handler with script conversion
- All 5 games implemented
- Main window with game switching
- Documentation

## Next Steps

1. **Try all 5 games** to see which you prefer
2. **Experiment with different scripts** to find what works best
3. **Replace sample databases** with real Prakrit data
4. **Track your progress** and watch your accuracy improve!

---

For detailed information, see [README.md](README.md)
