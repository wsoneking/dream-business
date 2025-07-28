"""
SQLite Compatibility Module for Streamlit Cloud
Overrides default sqlite3 with pysqlite3-binary for ChromaDB compatibility
"""

import sys

def setup_sqlite_compatibility():
    """
    Override sqlite3 with pysqlite3-binary for ChromaDB compatibility on Streamlit Cloud.
    This must be called before importing chromadb or any modules that use it.
    """
    try:
        # Try to import pysqlite3 and override sqlite3
        import pysqlite3
        sys.modules['sqlite3'] = pysqlite3
        print("✅ Successfully overrode sqlite3 with pysqlite3-binary for ChromaDB compatibility")
        return True
    except ImportError:
        print("⚠️ pysqlite3-binary not available, using system sqlite3")
        return False

# Call this immediately when module is imported
setup_sqlite_compatibility()