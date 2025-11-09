# Database Setup Guide

## Quick Start

### Automatic Download (Recommended)

```bash
# Download all databases from Dropbox
python3 download_databases.py

# Check status
python3 download_databases.py --check

# Download only dictionary
python3 download_databases.py --dict-only
```

The parser will automatically download missing databases on first run!

---

## Available Databases

| Database | Size | Purpose | Auto-Download |
|----------|------|---------|---------------|
| **prakrit-dict.db** | ~40 MB | Word meanings & definitions | ✅ Yes |
| **verb_forms.db** | ~15 MB | Attested verb forms | ✅ Yes |
| **noun_forms.db** | ~20 MB | Attested noun forms | ✅ Yes |

**Total**: ~75 MB

---

## What Each Database Provides

### 1. prakrit-dict.db (Dictionary)

**Contains:**
- 15,000+ Prakrit words with meanings
- Sanskrit equivalents
- Multiple senses per word
- Desya word identification
- Cross-references

**Example entry:**
```json
{
  "headword": "ghāya",
  "meanings": ["मारना, हत्या करना", "घात, हत्या"],
  "sanskrit_equivalent": ["हन्"],
  "is_desya": false
}
```

**Parser output WITH dictionary:**
```json
{
  "root": "ghāya",
  "dictionary": {
    "meanings": ["मारना, हत्या करना"],
    "sanskrit_equivalent": ["हन्"],
    "is_desya": false
  }
}
```

**Parser output WITHOUT dictionary:**
```json
{
  "root": "ghāya"
  // No meanings
}
```

### 2. verb_forms.db

**Contains:**
- 3,000+ verb roots
- All conjugated forms per root
- Person, number, tense information

**Improves accuracy for:**
- Attested verb form identification
- Faster lookups vs JSON
- Reduced false positives

### 3. noun_forms.db

**Contains:**
- 5,000+ noun stems
- All declined forms per stem
- Case, number, gender information

**Improves accuracy for:**
- Attested noun form identification
- Stem extraction
- Case identification

---

## How Auto-Download Works

### On First Run

```python
from unified_parser import PrakritUnifiedParser

# This automatically downloads missing databases
parser = PrakritUnifiedParser()
```

**What happens:**
1. Checks if databases exist
2. Downloads missing databases from Dropbox
3. Shows progress during download
4. Validates SQLite format
5. Continues even if download fails

### Manual Download

```bash
# Download all
python3 download_databases.py

# Force re-download
python3 download_databases.py --force

# Check what's downloaded
python3 download_databases.py --check
```

**Output:**
```
📊 Database Status:
======================================================================
  prakrit-dict.db      ✓ Present (38.45 MB)
    → Prakrit Dictionary (words with meanings)
  verb_forms.db        ✓ Present (14.23 MB)
    → Verb Forms Database
  noun_forms.db        ✓ Present (19.87 MB)
    → Noun Forms Database
======================================================================
✓ All databases present (Total: 72.55 MB)
```

---

## Fallback Behavior

The parser works **without databases** using fallback logic:

| Database Missing | Fallback Behavior |
|------------------|-------------------|
| prakrit-dict.db | No word meanings (morphology still works) |
| verb_forms.db | Uses ending-based verb analysis only |
| noun_forms.db | Uses ending-based noun analysis only |

**Still functional:**
- ✅ Suffix/ending analysis
- ✅ Case identification
- ✅ Sandhi detection
- ✅ User feedback learning

**Not available:**
- ❌ Word meanings
- ❌ Attested form validation
- ❌ Historical accuracy data

---

## Vercel Deployment

### Automatic Build

The `build.sh` script automatically downloads databases during deployment:

```bash
#!/bin/bash
echo "📥 Downloading databases from Dropbox..."
python3 download_databases.py
```

**Vercel configuration** (already set in `vercel.json`):
```json
{
  "builds": [
    {
      "src": "unified_parser.py",
      "use": "@vercel/python"
    }
  ]
}
```

### Build Process

1. Vercel starts build
2. Runs `build.sh`
3. Downloads databases from Dropbox
4. Deploys with databases included
5. Ready for production

**Note**: Vercel has a 250 MB limit for serverless functions, which is enough for our ~75 MB of databases.

---

## Manual Download (If Auto-Download Fails)

### Option 1: Direct Download

Visit these links in your browser:

- **Dictionary**: https://www.dropbox.com/scl/fi/pzftxtvk8p4iji08v6jno/prakrit-dict.db?rlkey=vkuwuhlmo0z0yu33n1pn2smty&st=y1yxu53l&dl=0

- **Verb Forms**: https://www.dropbox.com/scl/fi/9vsgdwryy997lg0x8if8m/verb_forms.db?rlkey=oj8xeabqxwyf69rrnn3uiaeps&st=izd2cdez&dl=0

- **Noun Forms**: https://www.dropbox.com/scl/fi/y55jdapz829kg0p01fkft/noun_forms.db?rlkey=v1s938s20declyifrkllr36o0&st=w2tswabh&dl=0

### Option 2: Using curl

```bash
# Dictionary
curl -L "https://www.dropbox.com/scl/fi/pzftxtvk8p4iji08v6jno/prakrit-dict.db?rlkey=vkuwuhlmo0z0yu33n1pn2smty&st=y1yxu53l&dl=1" -o prakrit-dict.db

# Verb forms
curl -L "https://www.dropbox.com/scl/fi/9vsgdwryy997lg0x8if8m/verb_forms.db?rlkey=oj8xeabqxwyf69rrnn3uiaeps&st=izd2cdez&dl=1" -o verb_forms.db

# Noun forms
curl -L "https://www.dropbox.com/scl/fi/y55jdapz829kg0p01fkft/noun_forms.db?rlkey=v1s938s20declyifrkllr36o0&st=w2tswabh&dl=1" -o noun_forms.db
```

### Option 3: Using wget

```bash
# Dictionary
wget "https://www.dropbox.com/scl/fi/pzftxtvk8p4iji08v6jno/prakrit-dict.db?rlkey=vkuwuhlmo0z0yu33n1pn2smty&st=y1yxu53l&dl=1" -O prakrit-dict.db

# Verb forms
wget "https://www.dropbox.com/scl/fi/9vsgdwryy997lg0x8if8m/verb_forms.db?rlkey=oj8xeabqxwyf69rrnn3uiaeps&st=izd2cdez&dl=1" -O verb_forms.db

# Noun forms
wget "https://www.dropbox.com/scl/fi/y55jdapz829kg0p01fkft/noun_forms.db?rlkey=v1s938s20declyifrkllr36o0&st=w2tswabh&dl=1" -O noun_forms.db
```

---

## Testing

### Test Database Downloads

```bash
# Download databases
python3 download_databases.py

# Verify they work
python3 dictionary_lookup.py prakrit-dict.db ghāya
```

**Expected output:**
```
Dictionary Statistics:
  Total entries: 15000
  Words: 12500
  Roots: 2500

--- Looking up: ghāya ---
Entry 1:
  Devanagari: घाय
  Type: transitive, neuter
  Sanskrit: हन्
  [Root form]
  Meanings:
    1. मारना, हत्या करना
```

### Test Parser with Databases

```bash
python3 unified_parser.py ghāya
```

**Expected output:**
```
✓ Dictionary database loaded
✓ Loaded 3000 verb roots from database
✓ Loaded 5000 noun stems from database

=== Analysis for: ghāya ===
Harvard-Kyoto: ghāya
Script: HK

Found 5 possible analyses:

--- Analysis 1 (confidence: 1.00) ---
Type: verb
Root: ghāya
Dictionary:
  Meanings: मारना, हत्या करना
  Sanskrit: हन्
```

---

## Troubleshooting

### "Download failed"

**Cause**: Network issue or Dropbox rate limiting

**Solution**:
```bash
# Try manual download
python3 download_databases.py --force

# Or use curl/wget (see Manual Download section)
```

### "Database not loaded"

**Cause**: Corrupted download or wrong format

**Solution**:
```bash
# Check file size
ls -lh *.db

# Re-download
rm prakrit-dict.db
python3 download_databases.py
```

### "Parser works but no meanings"

**Cause**: Dictionary database not loaded

**Solution**:
```bash
# Check dictionary specifically
python3 download_databases.py --dict-only

# Verify it loads
python3 dictionary_lookup.py prakrit-dict.db test
```

### Vercel deployment timeout

**Cause**: Database download takes too long

**Solutions**:
1. Pre-download databases and commit to Git (if under 100MB total)
2. Use smaller database subset
3. Upgrade Vercel plan for longer build time

---

## Database Schema

### prakrit-dict.db

```sql
CREATE TABLE dictionary (
    id INTEGER PRIMARY KEY,
    headword_devanagari TEXT,
    headword_translit TEXT,
    type_list TEXT,  -- JSON array
    meanings TEXT,   -- JSON array
    sanskrit_equivalent TEXT,  -- JSON array
    is_desya INTEGER,
    is_root INTEGER
);

CREATE INDEX idx_headword_translit ON dictionary(headword_translit);
CREATE VIRTUAL TABLE dictionary_fts USING fts5(...);
```

### verb_forms.db

```sql
CREATE TABLE verb_forms (
    root TEXT PRIMARY KEY,
    forms TEXT  -- JSON object with all conjugated forms
);
```

### noun_forms.db

```sql
CREATE TABLE noun_forms (
    stem TEXT PRIMARY KEY,
    forms TEXT  -- JSON object with all declined forms
);
```

---

## Performance

| Operation | With Databases | Without Databases |
|-----------|----------------|-------------------|
| Parse word | 50-100ms | 30-50ms |
| Get meanings | Instant | N/A |
| Startup time | +2-3 seconds | Instant |
| Memory usage | +50 MB | Baseline |
| Accuracy | 90-95% | 70-80% |

**Trade-off**: Slightly slower startup, significantly better accuracy and features.

---

## .gitignore

Databases are **excluded from Git** to avoid size limits:

```gitignore
# Database files (auto-downloaded)
*.db
prakrit-dict.db
verb_forms.db
noun_forms.db
```

They are downloaded automatically, so no need to commit them!

---

## Summary

### ✅ What Works

- Auto-download on first run
- Fallback to JSON files
- Manual download options
- Vercel deployment
- Progress reporting
- Error handling

### 📋 Next Steps

1. Run `python3 download_databases.py`
2. Test with `python3 unified_parser.py ghāya`
3. Deploy to Vercel
4. Enjoy enhanced parser with meanings!

---

**All databases are hosted on Dropbox and downloaded automatically. No manual setup required!**
