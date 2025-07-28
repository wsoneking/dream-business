# ChromaDB SQLite Compatibility Fix for Streamlit Cloud

## Problem
When deploying to Streamlit Cloud, ChromaDB fails with the error:
```
ChromaDB dependencies failed to load: Your system has an unsupported version of sqlite3. Chroma requires sqlite3 >= 3.35.0.
```

## Solution
This fix implements the recommended solution from the [ChromaDB troubleshooting documentation](https://docs.trychroma.com/troubleshooting#sqlite):

### 1. Added pysqlite3-binary dependency
- Added `pysqlite3-binary` to `requirements.txt`
- This provides a compatible SQLite version for ChromaDB

### 2. Created SQLite compatibility module
- Created `app/sqlite_compat.py` that overrides the default sqlite3 module
- This module must be imported BEFORE any ChromaDB imports

### 3. Updated import order
- Modified `streamlit_app.py` to import `sqlite_compat` first
- Modified `app/chain.py` to import `sqlite_compat` before RAG engine
- Modified `app/rag_engine.py` to import `sqlite_compat` before ChromaDB

## Files Modified
1. `requirements.txt` - Added pysqlite3-binary dependency
2. `app/sqlite_compat.py` - New compatibility module
3. `streamlit_app.py` - Updated import order
4. `app/chain.py` - Updated import order
5. `app/rag_engine.py` - Updated import order

## How It Works
1. `pysqlite3-binary` provides a newer SQLite version (>= 3.35.0)
2. The compatibility module overrides `sys.modules['sqlite3']` with `pysqlite3`
3. When ChromaDB imports sqlite3, it gets the compatible version instead
4. This must happen before any ChromaDB imports, hence the careful import ordering

## Testing
After deployment, the system should:
1. Successfully override sqlite3 with pysqlite3-binary
2. Initialize ChromaDB without SQLite version errors
3. Fall back gracefully to simple mode if ChromaDB still fails

## Fallback Behavior
The system maintains robust fallback behavior:
- If pysqlite3-binary is not available, it logs a warning but continues
- If ChromaDB still fails to initialize, the system runs in simple mode without vector database
- Users still get AI responses, just without knowledge base retrieval

## References
- [ChromaDB Troubleshooting - SQLite](https://docs.trychroma.com/troubleshooting#sqlite)
- [pysqlite3 GitHub Repository](https://github.com/coleifer/pysqlite3)