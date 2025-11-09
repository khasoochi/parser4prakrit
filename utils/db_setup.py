#!/usr/bin/env python3
"""
Setup databases - decompress if needed, download if missing.
"""

import os
import gzip
import shutil
from pathlib import Path

def decompress_database(gz_path, db_path):
    """Decompress a gzipped database file."""
    if db_path.exists():
        print(f"✓ {db_path.name} already exists")
        return

    if not gz_path.exists():
        print(f"✗ {gz_path.name} not found")
        return False

    print(f"Decompressing {gz_path.name}...")
    try:
        with gzip.open(gz_path, 'rb') as f_in:
            with open(db_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"✓ Decompressed to {db_path.name}")
        return True
    except Exception as e:
        print(f"✗ Error decompressing: {e}")
        if db_path.exists():
            db_path.unlink()
        return False

def setup_databases(data_dir='data'):
    """Setup all databases (decompress if needed)."""
    data_path = Path(data_dir)
    data_path.mkdir(exist_ok=True)

    databases = ['verb_forms.db', 'noun_forms.db']

    for db_name in databases:
        db_path = data_path / db_name
        gz_path = data_path / f"{db_name}.gz"

        if not db_path.exists() and gz_path.exists():
            decompress_database(gz_path, db_path)

    print("\n✓ Database setup complete!")

if __name__ == '__main__':
    setup_databases()
