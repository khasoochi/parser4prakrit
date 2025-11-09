#!/usr/bin/env python3
"""
Download large databases from cloud storage on first run.
"""

import os
import requests
from pathlib import Path

class DatabaseDownloader:
    """Download and cache large database files from cloud storage."""

    # Configure these URLs after uploading to cloud storage
    DB_URLS = {
        'verb_forms.db': 'https://your-storage.com/verb_forms.db',
        'noun_forms.db': 'https://your-storage.com/noun_forms.db'
    }

    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def download_database(self, db_name, url):
        """Download a database file if it doesn't exist."""
        db_path = self.data_dir / db_name

        if db_path.exists():
            print(f"✓ {db_name} already exists")
            return db_path

        print(f"Downloading {db_name} ({url})...")
        print(f"This may take a few minutes...")

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(db_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        # Show progress
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rProgress: {percent:.1f}%", end='', flush=True)

            print(f"\n✓ Downloaded {db_name} successfully!")
            return db_path

        except Exception as e:
            print(f"\n✗ Error downloading {db_name}: {e}")
            if db_path.exists():
                db_path.unlink()  # Remove partial download
            raise

    def ensure_databases(self):
        """Ensure all required databases are available."""
        for db_name, url in self.DB_URLS.items():
            self.download_database(db_name, url)

    def get_database_path(self, db_name):
        """Get path to database, downloading if necessary."""
        db_path = self.data_dir / db_name
        if not db_path.exists():
            url = self.DB_URLS.get(db_name)
            if url:
                self.download_database(db_name, url)
        return str(db_path)


# Usage in your app
if __name__ == '__main__':
    downloader = DatabaseDownloader()
    downloader.ensure_databases()
    print("All databases ready!")
