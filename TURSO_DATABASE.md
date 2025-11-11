# Turso Database Integration

The Prakrit parser now uses **Turso** (libSQL) as its primary database for storing verb forms, noun forms, and participle forms.

## Database Information

**URL:** `libsql://prakrit-khasoochi.aws-ap-south-1.turso.io`
**Region:** AWS Asia Pacific (Mumbai - ap-south-1)
**Authentication:** JWT token-based

## Schema

### Verb Roots Table
```sql
CREATE TABLE verb_roots (
    root_id INTEGER PRIMARY KEY AUTOINCREMENT,
    root TEXT UNIQUE NOT NULL,
    original_root TEXT NOT NULL,
    root_type TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK(root_type IN ('consonant', 'vowel'))
);
```

**Purpose:** Stores all Prakrit verb roots with their type classification.

**Example:**
| root_id | root  | original_root | root_type  |
|---------|-------|---------------|------------|
| 1       | muN   | मुण          | consonant  |
| 2       | jAN   | जाण          | consonant  |
| 3       | NI    | णी           | vowel      |

### Verb Forms Table
```sql
CREATE TABLE verb_forms (
    form_id INTEGER PRIMARY KEY AUTOINCREMENT,
    root_id INTEGER NOT NULL,
    form TEXT NOT NULL,
    tense TEXT NOT NULL,
    voice TEXT NOT NULL,
    mood TEXT NOT NULL,
    dialect TEXT NOT NULL,
    person TEXT NOT NULL,
    number TEXT NOT NULL,
    FOREIGN KEY (root_id) REFERENCES verb_roots(root_id),
    UNIQUE(root_id, form, tense, voice, mood, dialect, person, number)
);
```

**Purpose:** Stores all inflected verb forms with complete grammatical information.

**Example:**
| form_id | root_id | form     | tense   | voice  | mood       | dialect | person | number |
|---------|---------|----------|---------|--------|------------|---------|--------|--------|
| 1       | 1       | muNinti  | present | active | indicative | standard| third  | plural |
| 2       | 1       | muNati   | present | active | indicative | standard| third  | singular |

### Noun Stems Table
```sql
CREATE TABLE noun_stems (
    stem_id INTEGER PRIMARY KEY AUTOINCREMENT,
    stem TEXT NOT NULL,
    gender TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stem, gender)
);
```

**Purpose:** Stores noun stems with their gender.

**Example:**
| stem_id | stem  | gender    |
|---------|-------|-----------|
| 1       | muNi  | masculine |
| 2       | rAjA  | masculine |

### Noun Forms Table
```sql
CREATE TABLE noun_forms (
    form_id INTEGER PRIMARY KEY AUTOINCREMENT,
    stem_id INTEGER NOT NULL,
    form TEXT NOT NULL,
    case_name TEXT NOT NULL,
    number TEXT NOT NULL,
    FOREIGN KEY (stem_id) REFERENCES noun_stems(stem_id),
    UNIQUE(stem_id, form, case_name, number)
);
```

**Purpose:** Stores all inflected noun forms with grammatical case information.

**Example:**
| form_id | stem_id | form       | case_name  | number   |
|---------|---------|------------|------------|----------|
| 1       | 1       | muNIhiMto  | ablative   | singular |
| 2       | 1       | muNI       | nominative | singular |

### Metadata Table
```sql
CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

**Purpose:** Stores database metadata like version, last_updated, etc.

## How It Works

### 1. Connection Priority

The parser uses a **fallback strategy**:

```
1. Try Turso database (remote, always up-to-date)
   ↓ If fails
2. Try local SQLite files (cached)
   ↓ If fails
3. Try JSON files (legacy)
```

### 2. Attested Form Checking

When you parse a word like "muNinti":

```python
# 1. Generate anusvara variants
variants = ['muNinti', 'muṇinti', 'muninti', 'muñinti', ...]

# 2. Query Turso for each variant
for variant in variants:
    result = turso_db.check_verb_form(variant)
    if found:
        return root, grammatical_info

# 3. If found in Turso:
#    - Confidence: 1.0 (highest)
#    - Source: 'attested_form'
#    - Complete grammatical information from database
```

### 3. Anusvara Variant Support

The database integration includes automatic anusvara variant generation:

- `muNinti` → tries `muṇinti`, `muninti`, `muñinti`, `muṅinti`, `muMinti`, `muṃinti`
- Handles all nasal consonant variations: `N`, `ṇ`, `n`, `ñ`, `ṅ`, `m`, `M`, `ṃ`

### 4. Performance Optimization

**In-memory caching:**
- On initialization, loads all verb/noun forms into memory
- Subsequent lookups are instant (no network calls)
- Total memory: ~10-50MB depending on data size

**Direct queries (alternative):**
- For real-time updates or low-memory environments
- Each lookup queries Turso directly
- Supports anusvara variants in SQL WHERE clause

## Setup and Configuration

### Installation

```bash
pip install libsql-client
```

### Authentication Token

The auth token is embedded in `turso_db.py`. To rotate:

1. Generate new token:
```bash
turso db tokens create prakrit
```

2. Update `turso_db.py`:
```python
TURSO_AUTH_TOKEN = "your-new-token-here"
```

### Environment Variables (Optional)

Instead of hardcoding, you can use environment variables:

```python
import os
TURSO_DATABASE_URL = os.getenv('TURSO_DB_URL', 'libsql://prakrit-khasoochi.aws-ap-south-1.turso.io')
TURSO_AUTH_TOKEN = os.getenv('TURSO_AUTH_TOKEN', 'default-token')
```

Then set in your deployment:
```bash
# Vercel
vercel env add TURSO_DB_URL
vercel env add TURSO_AUTH_TOKEN

# Local
export TURSO_DB_URL="libsql://prakrit-khasoochi.aws-ap-south-1.turso.io"
export TURSO_AUTH_TOKEN="your-token"
```

## Usage Examples

### Basic Parsing

```python
from unified_parser import PrakritUnifiedParser

parser = PrakritUnifiedParser()

# Parse a word - automatically uses Turso
result = parser.parse("muNinti")

# Check if attested
for analysis in result['analyses']:
    if analysis['source'] == 'attested_form':
        print(f"✓ Found in Turso: {analysis['root']}")
```

### Direct Database Queries

```python
from turso_db import TursoDatabase

db = TursoDatabase()
db.connect()

# Check specific form
found, root, info = db.check_verb_form("muNinti")
if found:
    print(f"Root: {root}")
    print(f"Tense: {info['tense']}")
    print(f"Person: {info['person']}")

# Load all data
verb_forms = db.load_verb_forms()
print(f"Total roots: {len(verb_forms)}")
```

### Get Database Statistics

```python
from turso_db import TursoDatabase

db = TursoDatabase()
db.connect()

# Get metadata
version = db.get_metadata('version')
last_updated = db.get_metadata('last_updated')

print(f"Database version: {version}")
print(f"Last updated: {last_updated}")
```

## Adding Data to Turso

### Using Turso CLI

```bash
# Connect to database
turso db shell prakrit

# Insert verb root
INSERT INTO verb_roots (root, original_root, root_type)
VALUES ('BhU', 'भू', 'vowel');

# Insert verb form
INSERT INTO verb_forms (root_id, form, tense, voice, mood, dialect, person, number)
VALUES (
    (SELECT root_id FROM verb_roots WHERE root = 'BhU'),
    'Bhavati',
    'present',
    'active',
    'indicative',
    'standard',
    'third',
    'singular'
);
```

### Using Python Script

```python
from libsql_client import create_client_sync

client = create_client_sync(
    url="libsql://prakrit-khasoochi.aws-ap-south-1.turso.io",
    auth_token="your-token"
)

# Insert verb root
client.execute("""
    INSERT INTO verb_roots (root, original_root, root_type)
    VALUES (?, ?, ?)
""", ['kar', 'कर', 'consonant'])

# Get the root_id
result = client.execute("SELECT root_id FROM verb_roots WHERE root = ?", ['kar'])
root_id = result.rows[0][0]

# Insert verb forms
forms = [
    ('karoti', 'present', 'active', 'indicative', 'standard', 'third', 'singular'),
    ('karanti', 'present', 'active', 'indicative', 'standard', 'third', 'plural'),
]

for form_data in forms:
    client.execute("""
        INSERT INTO verb_forms (root_id, form, tense, voice, mood, dialect, person, number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [root_id] + list(form_data))
```

## Benefits of Turso Integration

### ✓ Always Up-to-Date
- No need to download/update local files
- Database updated centrally
- All users get latest data instantly

### ✓ Normalized Schema
- Eliminates data redundancy
- Easier to maintain
- Foreign keys ensure integrity

### ✓ Efficient Storage
- Forms share root references
- ~10x smaller than denormalized JSON
- Faster queries with proper indexing

### ✓ Real-time Updates
- Add new forms without redeployment
- A/B testing different analyses
- Community contributions possible

### ✓ Multi-dialect Support
- Store regional variants
- Track dialect-specific forms
- Historical Prakrit stages

### ✓ Advanced Querying
- Find all forms of a root
- Search by grammatical features
- Statistical analysis

## Troubleshooting

### Connection Fails

**Error:** `Cannot connect to host prakrit-khasoochi.aws-ap-south-1.turso.io`

**Solutions:**
1. Check internet connectivity
2. Verify Turso database is running: `turso db show prakrit`
3. Test auth token: `turso db tokens validate <token>`
4. Check firewall/proxy settings

### No Data Loaded

**Error:** `Verb roots loaded: 0`

**Solutions:**
1. Check if tables have data: `turso db shell prakrit` → `SELECT COUNT(*) FROM verb_roots;`
2. Verify table schema matches expected structure
3. Check for SQL syntax errors in queries

### Slow Queries

**Solutions:**
1. Add indexes:
```sql
CREATE INDEX idx_verb_forms_form ON verb_forms(form);
CREATE INDEX idx_noun_forms_form ON noun_forms(form);
```

2. Use in-memory caching (default behavior)

3. Consider Turso's edge caching with read replicas

## Migration from Local SQLite

If you have existing local SQLite files, migrate them to Turso:

```python
import sqlite3
from turso_db import TursoDatabase

# Connect to local DB
local = sqlite3.connect('verb_forms.db')
cursor = local.cursor()

# Connect to Turso
turso = TursoDatabase()
turso.connect()

# Read from local
cursor.execute("SELECT root, forms FROM verb_forms")
for root, forms_json in cursor.fetchall():
    # Parse and insert into Turso
    # (implementation depends on your local schema)
    pass
```

## Security

- **Token Rotation:** Rotate auth tokens every 90 days
- **Read-only Tokens:** Use read-only tokens for production parsing
- **Admin Tokens:** Keep admin tokens secure, never commit to Git
- **Environment Variables:** Use env vars instead of hardcoding

## Future Enhancements

1. **Participle Forms Table** - Track participles separately
2. **Compound Words** - Store sandhi patterns
3. **Etymology Links** - Connect to Sanskrit roots
4. **Usage Frequency** - Track form popularity
5. **Text Corpus** - Link forms to example sentences
6. **User Corrections** - Store feedback in database
7. **Confidence Scores** - ML-based accuracy tracking

## Support

For Turso-related issues:
- Turso Docs: https://docs.turso.tech/
- Turso Discord: https://discord.gg/turso
- Database admin: See project maintainer

For parser issues:
- GitHub Issues: https://github.com/khasoochi/parser4prakrit/issues
