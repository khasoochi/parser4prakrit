#!/usr/bin/env python3
"""
Download Prakrit Databases from Dropbox

Downloads dictionary and form databases on first run or when missing.
Automatically called by unified_parser.py on initialization.

Usage:
    python3 download_databases.py              # Download all databases
    python3 download_databases.py --dict-only  # Download dictionary only
    python3 download_databases.py --check      # Check which databases exist
"""

import os
import sys
import urllib.request
import argparse


# Database configuration
DATABASES = {
    'prakrit-dict.db': {
        'url': 'https://www.dropbox.com/scl/fi/pzftxtvk8p4iji08v6jno/prakrit-dict.db?rlkey=vkuwuhlmo0z0yu33n1pn2smty&st=y1yxu53l&dl=1',
        'description': 'Prakrit Dictionary (words with meanings)',
        'required': False  # Parser works without dictionary, just no meanings
    },
    'verb_forms.db': {
        'url': 'https://www.dropbox.com/scl/fi/9vsgdwryy997lg0x8if8m/verb_forms.db?rlkey=oj8xeabqxwyf69rrnn3uiaeps&st=izd2cdez&dl=1',
        'description': 'Verb Forms Database',
        'required': False  # Parser has fallback verb analysis
    },
    'noun_forms.db': {
        'url': 'https://www.dropbox.com/scl/fi/y55jdapz829kg0p01fkft/noun_forms.db?rlkey=v1s938s20declyifrkllr36o0&st=w2tswabh&dl=1',
        'description': 'Noun Forms Database',
        'required': False  # Parser has fallback noun analysis
    }
}


def format_size(bytes):
    """Format bytes as human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"


def download_database(db_name, db_info, force=False):
    """
    Download a single database file

    Args:
        db_name: Name of database file
        db_info: Dictionary with 'url' and 'description'
        force: Force re-download even if exists

    Returns:
        True if successful, False otherwise
    """
    # Check if already exists
    if os.path.exists(db_name) and not force:
        size = os.path.getsize(db_name)
        print(f"✓ {db_name} already exists ({format_size(size)})")
        return True

    print(f"\n📥 Downloading {db_name}...")
    print(f"   {db_info['description']}")
    print(f"   Source: Dropbox")

    try:
        # Download with progress reporting
        def reporthook(count, block_size, total_size):
            if total_size > 0:
                percent = int(count * block_size * 100 / total_size)
                downloaded = count * block_size
                sys.stdout.write(
                    f"\r   Progress: {percent:3d}% ({format_size(downloaded)} / {format_size(total_size)})"
                )
                sys.stdout.flush()

        urllib.request.urlretrieve(db_info['url'], db_name, reporthook)
        print()  # New line after progress

        # Verify download
        if os.path.exists(db_name):
            size = os.path.getsize(db_name)
            print(f"   ✓ Downloaded successfully ({format_size(size)})")

            # Basic SQLite validation
            with open(db_name, 'rb') as f:
                header = f.read(16)
                if header[:6] != b'SQLite':
                    print(f"   ⚠ Warning: File may not be a valid SQLite database")
                    return False

            return True
        else:
            print(f"   ✗ Download failed: File not created")
            return False

    except Exception as e:
        print(f"\n   ✗ Error downloading {db_name}: {e}")
        print(f"   Manual download: {db_info['url'].replace('dl=1', 'dl=0')}")
        return False


def check_databases():
    """Check status of all databases"""
    print("\n📊 Database Status:")
    print("=" * 70)

    all_present = True
    total_size = 0

    for db_name, db_info in DATABASES.items():
        if os.path.exists(db_name):
            size = os.path.getsize(db_name)
            total_size += size
            status = f"✓ Present ({format_size(size)})"
        else:
            status = "✗ Missing" + (" [Required]" if db_info['required'] else " [Optional]")
            all_present = False

        print(f"  {db_name:<20} {status}")
        print(f"    → {db_info['description']}")

    print("=" * 70)
    if all_present:
        print(f"✓ All databases present (Total: {format_size(total_size)})")
    else:
        print("⚠ Some databases missing. Run without --check to download.")
    print()

    return all_present


def download_all(dict_only=False, force=False):
    """
    Download all missing databases

    Args:
        dict_only: Only download dictionary database
        force: Force re-download even if exists

    Returns:
        True if all downloads successful
    """
    print("\n" + "=" * 70)
    print("Prakrit Parser - Database Download")
    print("=" * 70)

    if dict_only:
        databases_to_download = {'prakrit-dict.db': DATABASES['prakrit-dict.db']}
    else:
        databases_to_download = DATABASES

    success_count = 0
    total_count = len(databases_to_download)

    for db_name, db_info in databases_to_download.items():
        if download_database(db_name, db_info, force):
            success_count += 1

    print("\n" + "=" * 70)
    print(f"Download Summary: {success_count}/{total_count} successful")

    if success_count == total_count:
        print("✓ All databases ready!")
    elif success_count > 0:
        print("⚠ Some databases downloaded, parser will work with reduced features")
    else:
        print("✗ No databases downloaded, parser will use fallback analysis only")

    print("=" * 70 + "\n")

    return success_count == total_count


def download_if_missing():
    """
    Download missing databases (called automatically by parser)

    Returns:
        Dictionary with database paths or None for missing databases
    """
    db_paths = {}

    for db_name in DATABASES.keys():
        if os.path.exists(db_name):
            db_paths[db_name] = db_name
        else:
            # Silently try to download
            try:
                download_database(db_name, DATABASES[db_name], force=False)
                if os.path.exists(db_name):
                    db_paths[db_name] = db_name
                else:
                    db_paths[db_name] = None
            except:
                db_paths[db_name] = None

    return db_paths


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Download Prakrit Parser databases from Dropbox'
    )
    parser.add_argument(
        '--dict-only',
        action='store_true',
        help='Download only the dictionary database'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check database status without downloading'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-download even if files exist'
    )

    args = parser.parse_args()

    if args.check:
        all_present = check_databases()
        sys.exit(0 if all_present else 1)
    else:
        success = download_all(dict_only=args.dict_only, force=args.force)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
