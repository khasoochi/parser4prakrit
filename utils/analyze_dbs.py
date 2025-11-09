#!/usr/bin/env python3
"""Analyze Prakrit database structure and display sample data."""

import sqlite3
import os

def analyze_database(db_path, db_type):
    """Analyze and display database structure and sample data."""
    print(f"\n{'='*60}")
    print(f"DATABASE: {db_type.upper()}")
    print(f"Path: {db_path}")
    print(f"{'='*60}\n")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for (table_name,) in tables:
        print(f"\n--- TABLE: {table_name} ---")

        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        print("\nSchema:")
        for col in columns:
            col_id, col_name, col_type, not_null, default, pk = col
            pk_str = " PRIMARY KEY" if pk else ""
            null_str = " NOT NULL" if not_null else ""
            default_str = f" DEFAULT {default}" if default else ""
            print(f"  {col_name}: {col_type}{pk_str}{null_str}{default_str}")

        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        row_count = cursor.fetchone()[0]
        print(f"\nTotal rows: {row_count}")

        # Get sample data (first 10 rows)
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 10;")
        rows = cursor.fetchall()

        if rows:
            print("\nSample data (first 10 rows):")
            col_names = [desc[0] for desc in cursor.description]

            # Print header
            print("  " + " | ".join(col_names))
            print("  " + "-" * (len(" | ".join(col_names)) + 10))

            # Print rows
            for row in rows:
                print("  " + " | ".join(str(val) if val is not None else "NULL" for val in row))

    conn.close()

def main():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    verb_db = os.path.join(base_dir, 'data', 'verb_forms.db')
    noun_db = os.path.join(base_dir, 'data', 'noun_forms.db')

    if os.path.exists(verb_db):
        analyze_database(verb_db, 'Verb Forms')
    else:
        print(f"Verb database not found: {verb_db}")

    if os.path.exists(noun_db):
        analyze_database(noun_db, 'Noun Forms')
    else:
        print(f"Noun database not found: {noun_db}")

    print("\n" + "="*60)
    print("DATABASE ANALYSIS COMPLETE")
    print("="*60)

if __name__ == '__main__':
    main()
