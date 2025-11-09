#!/usr/bin/env python3
"""
Create sample Prakrit database files with realistic data in Harvard-Kyoto format.
This script creates sample verb and noun databases for development.
Replace with actual databases when available.
"""

import sqlite3
import os

def create_verb_database(db_path):
    """Create sample verb forms database in Harvard-Kyoto format."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create verbs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verbs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            root TEXT NOT NULL,
            meaning TEXT,
            transitivity TEXT,
            difficulty TEXT DEFAULT 'medium'
        )
    ''')

    # Create verb_forms table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verb_forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verb_id INTEGER NOT NULL,
            tense TEXT NOT NULL,
            person TEXT NOT NULL,
            number TEXT NOT NULL,
            form TEXT NOT NULL,
            FOREIGN KEY (verb_id) REFERENCES verbs(id)
        )
    ''')

    # Sample verbs in Harvard-Kyoto format
    sample_verbs = [
        ('pac', 'to cook', 'transitive', 'easy'),
        ('gacch', 'to go', 'intransitive', 'easy'),
        ('kar', 'to do/make', 'transitive', 'easy'),
        ('bhAs', 'to speak', 'intransitive', 'medium'),
        ('diz', 'to see', 'transitive', 'medium'),
        ('jAn', 'to know', 'transitive', 'medium'),
        ('As', 'to sit', 'intransitive', 'easy'),
        ('thA', 'to stand', 'intransitive', 'easy'),
        ('pi', 'to drink', 'transitive', 'easy'),
        ('khAd', 'to eat', 'transitive', 'easy'),
    ]

    cursor.executemany('INSERT INTO verbs (root, meaning, transitivity, difficulty) VALUES (?, ?, ?, ?)',
                      sample_verbs)

    # Sample verb forms (Present tense conjugation for 'pac' - to cook)
    verb_forms_pac = [
        (1, 'present', 'first', 'singular', 'pacAmi'),
        (1, 'present', 'second', 'singular', 'pacasi'),
        (1, 'present', 'third', 'singular', 'pacadi'),
        (1, 'present', 'first', 'plural', 'pacAma'),
        (1, 'present', 'second', 'plural', 'pacaha'),
        (1, 'present', 'third', 'plural', 'pacanti'),
        (1, 'past', 'first', 'singular', 'apacaM'),
        (1, 'past', 'second', 'singular', 'apaco'),
        (1, 'past', 'third', 'singular', 'apacA'),
        (1, 'future', 'first', 'singular', 'pacissaM'),
        (1, 'future', 'third', 'singular', 'pacissadi'),
    ]

    # Forms for 'gacch' - to go
    verb_forms_gacch = [
        (2, 'present', 'first', 'singular', 'gacchAmi'),
        (2, 'present', 'second', 'singular', 'gacchasi'),
        (2, 'present', 'third', 'singular', 'gacchadi'),
        (2, 'present', 'first', 'plural', 'gacchAma'),
        (2, 'present', 'second', 'plural', 'gacchaha'),
        (2, 'present', 'third', 'plural', 'gacchanti'),
        (2, 'past', 'first', 'singular', 'agacchaM'),
        (2, 'past', 'third', 'singular', 'agacchA'),
        (2, 'future', 'first', 'singular', 'gacchissaM'),
    ]

    # Forms for 'kar' - to do
    verb_forms_kar = [
        (3, 'present', 'first', 'singular', 'karomi'),
        (3, 'present', 'second', 'singular', 'karosi'),
        (3, 'present', 'third', 'singular', 'karodi'),
        (3, 'present', 'first', 'plural', 'karoma'),
        (3, 'present', 'third', 'plural', 'karonti'),
        (3, 'past', 'first', 'singular', 'akaraM'),
        (3, 'past', 'third', 'singular', 'akarA'),
    ]

    all_verb_forms = verb_forms_pac + verb_forms_gacch + verb_forms_kar

    cursor.executemany('''
        INSERT INTO verb_forms (verb_id, tense, person, number, form)
        VALUES (?, ?, ?, ?, ?)
    ''', all_verb_forms)

    conn.commit()
    conn.close()
    print(f"✓ Created verb database: {db_path}")

def create_noun_database(db_path):
    """Create sample noun forms database in Harvard-Kyoto format."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create nouns table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nouns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            root TEXT NOT NULL,
            meaning TEXT,
            gender TEXT NOT NULL,
            difficulty TEXT DEFAULT 'medium'
        )
    ''')

    # Create noun_forms table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS noun_forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            noun_id INTEGER NOT NULL,
            case_name TEXT NOT NULL,
            number TEXT NOT NULL,
            form TEXT NOT NULL,
            FOREIGN KEY (noun_id) REFERENCES nouns(id)
        )
    ''')

    # Sample nouns in Harvard-Kyoto format
    sample_nouns = [
        ('dhamma', 'dharma/law', 'masculine', 'easy'),
        ('kamma', 'karma/action', 'neuter', 'easy'),
        ('loka', 'world', 'masculine', 'easy'),
        ('suha', 'happiness', 'neuter', 'easy'),
        ('kaTTha', 'wood', 'neuter', 'medium'),
        ('purisa', 'man/person', 'masculine', 'easy'),
        ('itthi', 'woman', 'feminine', 'medium'),
        ('phala', 'fruit', 'neuter', 'easy'),
        ('rAyA', 'king', 'masculine', 'medium'),
        ('nadI', 'river', 'feminine', 'medium'),
    ]

    cursor.executemany('INSERT INTO nouns (root, meaning, gender, difficulty) VALUES (?, ?, ?, ?)',
                      sample_nouns)

    # Sample noun forms for 'dhamma' (masculine a-stem)
    noun_forms_dhamma = [
        (1, 'nominative', 'singular', 'dhammo'),
        (1, 'nominative', 'plural', 'dhammA'),
        (1, 'accusative', 'singular', 'dhammaM'),
        (1, 'accusative', 'plural', 'dhamme'),
        (1, 'instrumental', 'singular', 'dhammeNa'),
        (1, 'instrumental', 'plural', 'dhammehi'),
        (1, 'dative', 'singular', 'dhammAya'),
        (1, 'dative', 'plural', 'dhammANaM'),
        (1, 'ablative', 'singular', 'dhammA'),
        (1, 'ablative', 'plural', 'dhammehi'),
        (1, 'genitive', 'singular', 'dhammassa'),
        (1, 'genitive', 'plural', 'dhammANaM'),
        (1, 'locative', 'singular', 'dhamme'),
        (1, 'locative', 'plural', 'dhammesu'),
        (1, 'vocative', 'singular', 'dhamma'),
        (1, 'vocative', 'plural', 'dhammA'),
    ]

    # Forms for 'loka' (masculine a-stem)
    noun_forms_loka = [
        (3, 'nominative', 'singular', 'loko'),
        (3, 'nominative', 'plural', 'lokA'),
        (3, 'accusative', 'singular', 'lokaM'),
        (3, 'accusative', 'plural', 'loke'),
        (3, 'instrumental', 'singular', 'lokeNa'),
        (3, 'instrumental', 'plural', 'lokehi'),
        (3, 'genitive', 'singular', 'lokassa'),
        (3, 'locative', 'singular', 'loke'),
        (3, 'locative', 'plural', 'lokesu'),
    ]

    # Forms for 'kamma' (neuter a-stem)
    noun_forms_kamma = [
        (2, 'nominative', 'singular', 'kammaM'),
        (2, 'nominative', 'plural', 'kammA'),
        (2, 'accusative', 'singular', 'kammaM'),
        (2, 'accusative', 'plural', 'kammA'),
        (2, 'instrumental', 'singular', 'kammeNa'),
        (2, 'instrumental', 'plural', 'kammehi'),
        (2, 'genitive', 'singular', 'kammassa'),
        (2, 'locative', 'singular', 'kamme'),
    ]

    # Forms for 'itthi' (feminine i-stem)
    noun_forms_itthi = [
        (7, 'nominative', 'singular', 'itthI'),
        (7, 'nominative', 'plural', 'itthiyo'),
        (7, 'accusative', 'singular', 'itthiM'),
        (7, 'accusative', 'plural', 'itthiyo'),
        (7, 'instrumental', 'singular', 'itthiyA'),
        (7, 'genitive', 'singular', 'itthiyA'),
        (7, 'locative', 'singular', 'itthiyaM'),
    ]

    all_noun_forms = noun_forms_dhamma + noun_forms_loka + noun_forms_kamma + noun_forms_itthi

    cursor.executemany('''
        INSERT INTO noun_forms (noun_id, case_name, number, form)
        VALUES (?, ?, ?, ?)
    ''', all_noun_forms)

    conn.commit()
    conn.close()
    print(f"✓ Created noun database: {db_path}")

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)

    # Create databases
    verb_db = os.path.join(data_dir, 'verb_forms.db')
    noun_db = os.path.join(data_dir, 'noun_forms.db')

    create_verb_database(verb_db)
    create_noun_database(noun_db)

    print("\n✓ Sample databases created successfully!")
    print("Replace these with actual Prakrit databases when available.")
