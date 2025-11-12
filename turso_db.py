"""
Turso database connection and query utilities for Prakrit parser
"""

import os
from typing import Dict, List, Optional, Tuple
from libsql_client import create_client_sync

# Turso database configuration
# Use environment variables for security, fall back to defaults for local dev
TURSO_DATABASE_URL = os.getenv(
    'TURSO_DATABASE_URL',
    "libsql://prakrit-khasoochi.aws-ap-south-1.turso.io"
)
TURSO_AUTH_TOKEN = os.getenv(
    'TURSO_AUTH_TOKEN',
    "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicm8iLCJpYXQiOjE3NjI5NTEwNzksImlkIjoiNjg1ZTllODgtYTZlZS00OWQ3LTg1MWQtNDVlNjczODYxZDlkIiwicmlkIjoiOGJiYWQzY2UtYzA2Mi00ZDYxLWE4OWYtYzM2MDJlMzk5MDI0In0.KfqM1qp3DWP9Mm630jNVvpNy38suB9oI7JhkZaBKLS10e3W1yIsbTiqrBemL7dDgNhVB5kw3cFOa9snhEPCsBw"
)

class TursoDatabase:
    """Turso database connection wrapper"""

    def __init__(self):
        """Initialize Turso database connection"""
        self.client = None
        self.connected = False

    def connect(self):
        """Establish connection to Turso database"""
        print(f"🔌 Attempting to connect to Turso database...")
        print(f"   URL: {TURSO_DATABASE_URL}")
        print(f"   Auth token: {'*' * 20}...{TURSO_AUTH_TOKEN[-10:] if TURSO_AUTH_TOKEN else 'NOT SET'}")

        try:
            self.client = create_client_sync(
                url=TURSO_DATABASE_URL,
                auth_token=TURSO_AUTH_TOKEN
            )

            # Test the connection with a simple query
            try:
                test_result = self.client.execute("SELECT 1")
                self.connected = True
                print("✓ Connected to Turso database successfully!")
                print("✓ Test query executed - database is operational")
                return True
            except Exception as test_error:
                print(f"✗ Turso database connection test failed: {test_error}")
                print("  → This usually means:")
                print("     1. Network/DNS issue (check firewall/connectivity)")
                print("     2. Invalid auth token")
                print("     3. Database is paused or deleted")
                self.connected = False
                return False

        except ImportError as ie:
            print(f"✗ libsql_client library not installed: {ie}")
            print("  → Install with: pip install libsql-client")
            self.connected = False
            return False
        except Exception as e:
            print(f"✗ Failed to create Turso client: {e}")
            print(f"  → Error type: {type(e).__name__}")
            print("  → Check TURSO_DATABASE_URL and TURSO_AUTH_TOKEN environment variables")
            self.connected = False
            return False

    def load_verb_forms(self) -> Dict[str, Dict[str, Dict]]:
        """
        Load all verb forms from Turso database

        Returns:
            Dict mapping root -> form -> grammatical_info
            Example: {'muN': {'muNinti': {'tense': 'present', 'person': 'third', ...}}}
        """
        if not self.connected:
            if not self.connect():
                return {}

        try:
            # Query verb forms with root information
            query = """
                SELECT
                    vr.root,
                    vf.form,
                    vf.tense,
                    vf.voice,
                    vf.mood,
                    vf.dialect,
                    vf.person,
                    vf.number
                FROM verb_forms vf
                JOIN verb_roots vr ON vf.root_id = vr.root_id
            """

            result = self.client.execute(query)

            # Organize by root -> form -> info
            verb_data = {}
            for row in result.rows:
                root = row[0]
                form = row[1]

                if root not in verb_data:
                    verb_data[root] = {}

                verb_data[root][form] = {
                    'tense': row[2],
                    'voice': row[3],
                    'mood': row[4],
                    'dialect': row[5],
                    'person': row[6],
                    'number': row[7]
                }

            print(f"✓ Loaded {len(verb_data)} verb roots with forms from Turso")
            return verb_data

        except Exception as e:
            print(f"✗ Error loading verb forms from Turso: {e}")
            return {}

    def load_noun_forms(self) -> Dict[str, Dict[str, Dict]]:
        """
        Load all noun forms from Turso database

        Returns:
            Dict mapping stem -> form -> grammatical_info
            Example: {'muNi': {'muNIhinto': {'case': 'ablative', 'number': 'singular', ...}}}
        """
        if not self.connected:
            if not self.connect():
                return {}

        try:
            # Query noun forms with stem information
            query = """
                SELECT
                    ns.stem,
                    ns.gender,
                    nf.form,
                    nf.case_name,
                    nf.number
                FROM noun_forms nf
                JOIN noun_stems ns ON nf.stem_id = ns.stem_id
            """

            result = self.client.execute(query)

            # Organize by stem -> form -> info
            noun_data = {}
            for row in result.rows:
                stem = row[0]
                gender = row[1]
                form = row[2]

                # Use stem as key (combining stem+gender would be redundant)
                if stem not in noun_data:
                    noun_data[stem] = {}

                noun_data[stem][form] = {
                    'gender': gender,
                    'case': row[3],
                    'number': row[4]
                }

            print(f"✓ Loaded {len(noun_data)} noun stems with forms from Turso")
            return noun_data

        except Exception as e:
            print(f"✗ Error loading noun forms from Turso: {e}")
            return {}

    def load_verb_roots(self) -> set:
        """
        Load all verb roots from Turso database

        Returns:
            Set of verb root strings
        """
        if not self.connected:
            if not self.connect():
                return set()

        try:
            query = "SELECT DISTINCT root FROM verb_roots"
            result = self.client.execute(query)

            roots = {row[0] for row in result.rows}
            print(f"✓ Loaded {len(roots)} verb roots from Turso")
            return roots

        except Exception as e:
            print(f"✗ Error loading verb roots from Turso: {e}")
            return set()

    def get_metadata(self, key: str) -> Optional[str]:
        """
        Get metadata value from database

        Args:
            key: Metadata key

        Returns:
            Metadata value or None
        """
        if not self.connected:
            if not self.connect():
                return None

        try:
            query = "SELECT value FROM metadata WHERE key = ?"
            result = self.client.execute(query, [key])

            if result.rows:
                return result.rows[0][0]
            return None

        except Exception as e:
            print(f"✗ Error getting metadata: {e}")
            return None

    def check_verb_form(self, form: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Check if a verb form exists in the database

        Args:
            form: Verb form to check

        Returns:
            Tuple of (found, root, grammatical_info)
        """
        if not self.connected:
            if not self.connect():
                return False, None, None

        try:
            query = """
                SELECT
                    vr.root,
                    vf.tense,
                    vf.voice,
                    vf.mood,
                    vf.dialect,
                    vf.person,
                    vf.number
                FROM verb_forms vf
                JOIN verb_roots vr ON vf.root_id = vr.root_id
                WHERE vf.form = ?
                LIMIT 1
            """

            result = self.client.execute(query, [form])

            if result.rows:
                row = result.rows[0]
                return True, row[0], {
                    'tense': row[1],
                    'voice': row[2],
                    'mood': row[3],
                    'dialect': row[4],
                    'person': row[5],
                    'number': row[6]
                }

            return False, None, None

        except Exception as e:
            print(f"✗ Error checking verb form: {e}")
            return False, None, None

    def check_noun_form(self, form: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Check if a noun form exists in the database

        Args:
            form: Noun form to check

        Returns:
            Tuple of (found, stem, grammatical_info)
        """
        if not self.connected:
            if not self.connect():
                return False, None, None

        try:
            query = """
                SELECT
                    ns.stem,
                    ns.gender,
                    nf.case_name,
                    nf.number
                FROM noun_forms nf
                JOIN noun_stems ns ON nf.stem_id = ns.stem_id
                WHERE nf.form = ?
                LIMIT 1
            """

            result = self.client.execute(query, [form])

            if result.rows:
                row = result.rows[0]
                return True, row[0], {
                    'gender': row[1],
                    'case': row[2],
                    'number': row[3]
                }

            return False, None, None

        except Exception as e:
            print(f"✗ Error checking noun form: {e}")
            return False, None, None

    def load_participle_forms(self) -> Dict[str, Dict[str, Dict]]:
        """
        Load all participle forms from Turso database

        Returns:
            Dict mapping root -> form -> grammatical_info
            Example: {'pucch': {'pucchittA': {'type': 'absolutive', 'suffix': 'ttA'}}}
        """
        if not self.connected:
            if not self.connect():
                return {}

        try:
            # Check if participle_forms table exists
            query = """
                SELECT
                    vr.root,
                    pf.form,
                    pf.participle_type,
                    pf.suffix,
                    pf.gender,
                    pf.case_name,
                    pf.number
                FROM participle_forms pf
                JOIN verb_roots vr ON pf.root_id = vr.root_id
            """

            result = self.client.execute(query)

            # Organize by root -> form -> info
            participle_data = {}
            for row in result.rows:
                root = row[0]
                form = row[1]

                if root not in participle_data:
                    participle_data[root] = {}

                participle_data[root][form] = {
                    'participle_type': row[2],
                    'suffix': row[3],
                    'gender': row[4],
                    'case': row[5],
                    'number': row[6]
                }

            print(f"✓ Loaded {len(participle_data)} verb roots with participle forms from Turso")
            return participle_data

        except Exception as e:
            # Table might not exist yet
            return {}

    def check_participle_form(self, form: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Check if a participle form exists in the database

        Args:
            form: Participle form to check

        Returns:
            Tuple of (found, root, grammatical_info)
        """
        if not self.connected:
            if not self.connect():
                return False, None, None

        try:
            query = """
                SELECT
                    vr.root,
                    pf.participle_type,
                    pf.suffix,
                    pf.gender,
                    pf.case_name,
                    pf.number
                FROM participle_forms pf
                JOIN verb_roots vr ON pf.root_id = vr.root_id
                WHERE pf.form = ?
                LIMIT 1
            """

            result = self.client.execute(query, [form])

            if result.rows:
                row = result.rows[0]
                return True, row[0], {
                    'participle_type': row[1],
                    'suffix': row[2],
                    'gender': row[3],
                    'case': row[4],
                    'number': row[5]
                }

            return False, None, None

        except Exception as e:
            return False, None, None

    def close(self):
        """Close database connection"""
        if self.client:
            self.client = None
            self.connected = False
