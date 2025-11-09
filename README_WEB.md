# 🎮 Prakrit Word Games - Web Application

**A browser-based language learning application for Prakrit with 5 interactive games.**

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/prakrit-game)

---

## 🌐 Live Demo

**Not deployed yet?** Follow the deployment guide: [DEPLOY_WEB_APP.md](DEPLOY_WEB_APP.md)

---

## ✨ Features

### 🎯 Five Educational Games

1. **📝 Form Quiz** - Type correct inflected forms from grammatical specifications
2. **🔍 Word Identification** - Identify roots and features from inflected forms
3. **📊 Paradigm Completion** - Fill in declension/conjugation tables
4. **⚡ Speed Drill** - Timed rapid-fire practice with combo multipliers
5. **🎯 Matching Game** - Match forms with grammatical descriptions

### 📚 Multi-Script Support

Switch seamlessly between 4 writing systems:
- **Devanagari** (देवनागरी) - Default
- **IAST** - International Alphabet of Sanskrit Transliteration
- **ISO 15919** - International standard
- **Harvard-Kyoto** - ASCII-compatible

### 📈 Progress Tracking

- Real-time score and streak tracking
- Accuracy statistics
- Difficulty levels (Easy/Medium/Hard)
- Persistent progress across sessions

---

## 🚀 Quick Start

### Run Locally

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/prakrit-game.git
cd prakrit-game

# 2. Install dependencies
pip install -r requirements_web.txt

# 3. Run the app
streamlit run streamlit_app.py

# 4. Open browser to http://localhost:8501
```

### Deploy to Cloud

See [DEPLOY_WEB_APP.md](DEPLOY_WEB_APP.md) for step-by-step instructions to deploy to:
- ✅ Vercel (recommended)
- ✅ Streamlit Cloud
- ✅ Any platform supporting Python/Streamlit

---

## 🗄️ Database Setup

The app supports two database backends:

### Option 1: SQLite (Local Development)

```bash
# Uses local .db files in data/ directory
# Good for: Testing, development, small deployments
```

### Option 2: PostgreSQL/Supabase (Production)

```bash
# 1. Create .env file
cp .env.example .env

# 2. Add your Supabase connection string
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres

# 3. Migrate data (see DEPLOY_WEB_APP.md)
python3 utils/migrate_to_postgres.py data/verb_forms.db verb_forms.sql
```

---

## 📦 Dependencies

```
streamlit >= 1.28.0          # Web framework
indic-transliteration >= 2.3.0  # Script conversion
psycopg2-binary >= 2.9.0     # PostgreSQL support (optional)
python-dotenv >= 1.0.0       # Environment variables
```

---

## 🏗️ Project Structure

```
prakrit-game/
├── streamlit_app.py         # Main web application
├── requirements_web.txt     # Web app dependencies
├── vercel.json             # Vercel deployment config
├── .streamlit/
│   └── config.toml         # Streamlit configuration
├── core/
│   ├── db_handler_web.py   # Database handler (SQLite + PostgreSQL)
│   └── script_converter.py # HK ↔ Devanagari/IAST/ISO conversion
├── web_games/              # Streamlit game modules
│   ├── game1_form_quiz.py
│   ├── game2_identification.py
│   ├── game3_paradigm.py
│   ├── game4_speed_drill.py
│   └── game5_matching.py
├── utils/
│   └── migrate_to_postgres.py  # Database migration tool
└── data/
    ├── verb_forms.db       # SQLite verb database
    └── noun_forms.db       # SQLite noun database
```

---

## 🎨 Customization

### Change Theme Colors

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#667eea"      # Purple
backgroundColor = "#ffffff"    # White
secondaryBackgroundColor = "#f8f9fa"
textColor = "#262730"
```

### Modify Games

Each game is in its own module in `web_games/`:
- Edit UI, scoring, or game logic
- Add new game modes
- Customize difficulty levels

---

## 🔒 Environment Variables

Required for production deployment:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |

---

## 🧪 Testing

```bash
# Run locally with SQLite (no DATABASE_URL needed)
streamlit run streamlit_app.py

# Test with PostgreSQL
export DATABASE_URL="postgresql://..."
streamlit run streamlit_app.py

# Test all games:
# - Switch between scripts
# - Try all difficulty levels
# - Verify score tracking
```

---

## 📊 Database Schema

### Tables

**verbs**
- `id` - Primary key
- `root` - Verb root (HK format)
- `meaning` - English translation
- `transitivity` - transitive/intransitive
- `difficulty` - easy/medium/hard

**verb_forms**
- `id` - Primary key
- `verb_id` - Foreign key to verbs
- `tense` - present/past/future
- `person` - first/second/third
- `number` - singular/plural
- `form` - Inflected form (HK format)

**nouns** & **noun_forms** - Similar structure

All Prakrit text stored in **Harvard-Kyoto (HK)** format, converted on-the-fly to user's preferred script.

---

## 🛠️ Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"

```bash
pip install -r requirements_web.txt
```

### "Database connection failed"

Check your `DATABASE_URL` in `.env` or environment variables.

### "No data showing in games"

1. Verify database files exist in `data/` directory
2. Or ensure PostgreSQL migration completed successfully
3. Check table names match schema

### "Script conversion not working"

```bash
# Verify indic-transliteration is installed
pip install indic-transliteration
```

---

## 💰 Hosting Costs

### Free Tiers (Sufficient for Educational Use)

- **Vercel:** Free for personal projects
- **Supabase:** 500MB database free
- **Streamlit Cloud:** 1GB resources free

**Total: $0/month** for moderate traffic!

### When to Upgrade

- **1000+ daily users:** Consider paid tiers
- **Large databases (> 500MB):** Upgrade Supabase
- **Custom domain:** Vercel Pro

---

## 📝 License

This educational application is provided as-is for learning purposes.

---

## 🤝 Contributing

Contributions welcome! Ideas:

- Add more games
- Improve UI/UX
- Add audio pronunciations
- Create mobile app version
- Add more languages

---

## 📚 Learn More

- **Deployment Guide:** [DEPLOY_WEB_APP.md](DEPLOY_WEB_APP.md)
- **Desktop Version:** [README.md](README.md)
- **Quick Start:** [QUICKSTART.md](QUICKSTART.md)

---

## 🎓 Educational Use

Perfect for:
- Sanskrit/Prakrit language courses
- Self-study learners
- Educational institutions
- Language preservation projects

---

## ⭐ Show Your Support

If you find this helpful:
- Star the repository
- Share with learners
- Report bugs
- Suggest improvements

---

**Built with:** Python, Streamlit, Supabase, Vercel

**Made for:** Prakrit language learners worldwide 🌍

शुभं भवतु! ✨
