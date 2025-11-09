#!/usr/bin/env python3
"""
Migrate SQLite databases to PostgreSQL (for cloud hosting).
Use with Supabase, Neon, PlanetScale, etc.
"""

import sqlite3
import os
from typing import Dict, List

# For PostgreSQL - install: pip install psycopg2-binary
# import psycopg2

# For Supabase - install: pip install supabase
# from supabase import create_client, Client

class DatabaseMigrator:
    """Migrate SQLite to cloud database."""

    def __init__(self, sqlite_path: str):
        self.sqlite_path = sqlite_path
        self.conn = sqlite3.connect(sqlite_path)
        self.cursor = self.conn.cursor()

    def get_schema(self) -> List[str]:
        """Get CREATE TABLE statements."""
        self.cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        return [row[0] for row in self.cursor.fetchall() if row[0]]

    def get_table_names(self) -> List[str]:
        """Get all table names."""
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        return [row[0] for row in self.cursor.fetchall()]

    def get_table_data(self, table_name: str) -> tuple:
        """Get all data from a table."""
        self.cursor.execute(f"SELECT * FROM {table_name}")
        columns = [desc[0] for desc in self.cursor.description]
        data = self.cursor.fetchall()
        return columns, data

    def export_to_sql(self, output_file: str):
        """Export to SQL file for manual import."""
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write schema
            f.write("-- Database Schema\n\n")
            for schema in self.get_schema():
                # Convert SQLite syntax to PostgreSQL if needed
                schema_pg = schema.replace('AUTOINCREMENT', 'SERIAL')
                f.write(schema_pg + ';\n\n')

            # Write data
            f.write("-- Data\n\n")
            for table in self.get_table_names():
                if table == 'sqlite_sequence':
                    continue

                columns, data = self.get_table_data(table)
                f.write(f"-- Table: {table}\n")

                for row in data:
                    # Format values
                    values = []
                    for val in row:
                        if val is None:
                            values.append('NULL')
                        elif isinstance(val, str):
                            # Escape single quotes
                            escaped = val.replace("'", "''")
                            values.append(f"'{escaped}'")
                        else:
                            values.append(str(val))

                    cols_str = ', '.join(columns)
                    vals_str = ', '.join(values)
                    f.write(f"INSERT INTO {table} ({cols_str}) VALUES ({vals_str});\n")

                f.write("\n")

        print(f"✓ Exported to {output_file}")

    def migrate_to_supabase(self, url: str, key: str):
        """
        Migrate to Supabase (PostgreSQL).

        Usage:
            migrator = DatabaseMigrator('verb_forms.db')
            migrator.migrate_to_supabase('YOUR_SUPABASE_URL', 'YOUR_SUPABASE_KEY')
        """
        # TODO: Implement Supabase migration
        # from supabase import create_client
        # supabase = create_client(url, key)
        # ... upload data
        pass

    def close(self):
        """Close SQLite connection."""
        self.conn.close()


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python migrate_to_postgres.py <sqlite_db_path> [output_sql_file]")
        print("\nExample:")
        print("  python migrate_to_postgres.py data/verb_forms.db verb_forms.sql")
        sys.exit(1)

    sqlite_db = sys.argv[1]
    output_sql = sys.argv[2] if len(sys.argv) > 2 else sqlite_db.replace('.db', '.sql')

    if not os.path.exists(sqlite_db):
        print(f"Error: {sqlite_db} not found")
        sys.exit(1)

    print(f"Migrating {sqlite_db} → {output_sql}")
    migrator = DatabaseMigrator(sqlite_db)
    migrator.export_to_sql(output_sql)
    migrator.close()

    print(f"\n✓ Migration complete!")
    print(f"\nNext steps:")
    print(f"1. Create a database on Supabase/Neon/PlanetScale")
    print(f"2. Import {output_sql} to your cloud database")
    print(f"3. Update your app to connect to the cloud database")
