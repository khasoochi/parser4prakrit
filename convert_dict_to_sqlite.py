#!/usr/bin/env python3
"""
Convert Prakrit Dictionary from JSON to SQLite

This script converts a large JSON dictionary to an efficient SQLite database.

Usage:
    python3 convert_dict_to_sqlite.py input.json output.db

Dictionary JSON format expected:
[
    {
        "headword_devanagari": "घाइआ",
        "headword_translit": "ghāiā",
        "type": ["neuter", "adjective"],
        "gender": "",
        "sanskrit_equivalent": ["घातिका"],
        "is_desya": false,
        "is_root": false,
        "is_word": true,
        "meanings": [
            {
                "sense_number": 1,
                "definition": "विनाश करनेवाली स्त्री",
                "references": []
            }
        ],
        "references": [],
        "cross_references": [],
        "compounds": [],
        "parent": null
    }
]
"""

import json
import sqlite3
import sys
import os
from typing import List, Dict, Any


def create_database(db_path: str):
    """Create SQLite database schema"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Main dictionary table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dictionary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            headword_devanagari TEXT NOT NULL,
            headword_translit TEXT NOT NULL,
            type_list TEXT,  -- JSON array
            gender TEXT,
            sanskrit_equivalent TEXT,  -- JSON array
            is_desya INTEGER,
            is_root INTEGER,
            is_word INTEGER,
            meanings TEXT,  -- JSON array of meanings
            references TEXT,  -- JSON array
            cross_references TEXT,  -- JSON array
            compounds TEXT,  -- JSON array
            parent TEXT
        )
    ''')

    # Create indexes for fast lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_headword_translit
        ON dictionary(headword_translit)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_headword_devanagari
        ON dictionary(headword_devanagari)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_is_root
        ON dictionary(is_root)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_is_word
        ON dictionary(is_word)
    ''')

    # Create full-text search table for definitions
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS dictionary_fts
        USING fts5(
            headword_translit,
            headword_devanagari,
            definitions,
            content=dictionary
        )
    ''')

    conn.commit()
    return conn


def extract_definitions(meanings: List[Dict]) -> str:
    """Extract all definitions as searchable text"""
    definitions = []
    for meaning in meanings:
        if 'definition' in meaning:
            definitions.append(meaning['definition'])
    return ' | '.join(definitions)


def insert_entries(conn: sqlite3.Connection, entries: List[Dict]):
    """Insert dictionary entries into database"""
    cursor = conn.cursor()

    for entry in entries:
        # Prepare data
        headword_devanagari = entry.get('headword_devanagari', '')
        headword_translit = entry.get('headword_translit', '')
        type_list = json.dumps(entry.get('type', []), ensure_ascii=False)
        gender = entry.get('gender', '')
        sanskrit_equivalent = json.dumps(entry.get('sanskrit_equivalent', []), ensure_ascii=False)
        is_desya = 1 if entry.get('is_desya', False) else 0
        is_root = 1 if entry.get('is_root', False) else 0
        is_word = 1 if entry.get('is_word', False) else 0
        meanings = json.dumps(entry.get('meanings', []), ensure_ascii=False)
        references = json.dumps(entry.get('references', []), ensure_ascii=False)
        cross_references = json.dumps(entry.get('cross_references', []), ensure_ascii=False)
        compounds = json.dumps(entry.get('compounds', []), ensure_ascii=False)
        parent = entry.get('parent')

        # Insert into main table
        cursor.execute('''
            INSERT INTO dictionary (
                headword_devanagari, headword_translit, type_list, gender,
                sanskrit_equivalent, is_desya, is_root, is_word,
                meanings, references, cross_references, compounds, parent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            headword_devanagari, headword_translit, type_list, gender,
            sanskrit_equivalent, is_desya, is_root, is_word,
            meanings, references, cross_references, compounds, parent
        ))

        # Insert into FTS table for full-text search
        definitions_text = extract_definitions(entry.get('meanings', []))
        cursor.execute('''
            INSERT INTO dictionary_fts (
                rowid, headword_translit, headword_devanagari, definitions
            ) VALUES (last_insert_rowid(), ?, ?, ?)
        ''', (headword_translit, headword_devanagari, definitions_text))

    conn.commit()


def convert_json_to_sqlite(json_path: str, db_path: str):
    """Main conversion function"""
    print(f"Loading JSON dictionary from: {json_path}")

    # Load JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        entries = json.load(f)

    print(f"Loaded {len(entries)} entries")

    # Create database
    print(f"Creating SQLite database: {db_path}")
    conn = create_database(db_path)

    # Insert entries in batches
    batch_size = 1000
    total = len(entries)

    for i in range(0, total, batch_size):
        batch = entries[i:i+batch_size]
        insert_entries(conn, batch)
        print(f"Processed {min(i+batch_size, total)}/{total} entries ({(min(i+batch_size, total)*100//total)}%)")

    # Get database stats
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM dictionary')
    count = cursor.fetchone()[0]

    cursor.execute('SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()')
    size_bytes = cursor.fetchone()[0]
    size_mb = size_bytes / (1024 * 1024)

    conn.close()

    print(f"\n✓ Conversion complete!")
    print(f"  - Total entries: {count}")
    print(f"  - Database size: {size_mb:.2f} MB")
    print(f"  - Output: {db_path}")


def test_database(db_path: str, test_word: str = 'ghāya'):
    """Test the database with a sample query"""
    print(f"\n--- Testing database with word: '{test_word}' ---")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Test exact match
    cursor.execute('''
        SELECT headword_translit, headword_devanagari, meanings
        FROM dictionary
        WHERE headword_translit = ?
    ''', (test_word,))

    results = cursor.fetchall()

    if results:
        print(f"Found {len(results)} exact matches:")
        for headword_translit, headword_devanagari, meanings_json in results:
            meanings = json.loads(meanings_json)
            print(f"  {headword_translit} ({headword_devanagari})")
            for meaning in meanings[:2]:  # Show first 2 meanings
                print(f"    - {meaning.get('definition', 'N/A')}")
    else:
        print("  No exact matches found")

    # Test full-text search
    cursor.execute('''
        SELECT headword_translit, headword_devanagari
        FROM dictionary_fts
        WHERE dictionary_fts MATCH ?
        LIMIT 5
    ''', (test_word,))

    fts_results = cursor.fetchall()

    if fts_results:
        print(f"\nFull-text search results:")
        for headword_translit, headword_devanagari in fts_results:
            print(f"  {headword_translit} ({headword_devanagari})")

    conn.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 convert_dict_to_sqlite.py <input.json> <output.db>")
        print("\nExample:")
        print("  python3 convert_dict_to_sqlite.py prakrit_dict.json prakrit_dict.db")
        sys.exit(1)

    json_path = sys.argv[1]
    db_path = sys.argv[2]

    if not os.path.exists(json_path):
        print(f"Error: Input file not found: {json_path}")
        sys.exit(1)

    if os.path.exists(db_path):
        response = input(f"Database {db_path} already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
        os.remove(db_path)

    try:
        convert_json_to_sqlite(json_path, db_path)

        # Run test if database is not too large
        if os.path.getsize(db_path) < 100 * 1024 * 1024:  # < 100 MB
            test_word = sys.argv[3] if len(sys.argv) > 3 else 'ghāya'
            test_database(db_path, test_word)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
