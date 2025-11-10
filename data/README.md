# Data Directory

This directory contains SQL database files for Prakrit verb form validation.

## Files

- `prakrit_verbs.db` - SQLite database with attested Prakrit verb forms
- `user_feedback.db` - SQLite database for user feedback and corrections

## Schema

### prakrit_verbs.db

#### verbs table:
```sql
CREATE TABLE verbs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verb_form TEXT NOT NULL UNIQUE,
    root TEXT NOT NULL,
    tense TEXT NOT NULL,
    person TEXT,
    number TEXT,
    mood TEXT,
    voice TEXT,
    source TEXT,  -- Source reference (grammar, text)
    dialect TEXT,  -- Maharashtri, Shauraseni, etc.
    confidence REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### roots table:
```sql
CREATE TABLE roots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    root TEXT NOT NULL UNIQUE,
    meaning TEXT,
    class TEXT,  -- Verb class (bhū, div, etc.)
    sanskrit_cognate TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### user_feedback.db

#### feedback table:
```sql
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verb_form TEXT NOT NULL,
    selected_analysis TEXT NOT NULL,  -- JSON of the selected analysis
    all_analyses TEXT NOT NULL,  -- JSON of all presented analyses
    user_ip TEXT,
    user_agent TEXT,
    session_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Usage

Place your SQL export files here. The application will automatically:
1. Load verified forms from `prakrit_verbs.db`
2. Give higher confidence to forms found in the database
3. Collect user feedback to improve accuracy over time

## Adding Data

To add verified verb forms:

```sql
INSERT INTO verbs (verb_form, root, tense, person, number, source, dialect)
VALUES ('karomi', 'kar', 'present', 'first', 'singular', 'Pischel 1900', 'Maharashtri');
```

To add roots:

```sql
INSERT INTO roots (root, meaning, sanskrit_cognate, notes)
VALUES ('kar', 'to do, to make', 'kṛ', 'Common verb root');
```
