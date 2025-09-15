import os

# Document sources - add your paths here
DOCUMENT_PATHS = [
    "/home/heverz/py_projects/local-rag/documents/"
]

# File patterns to include (leave empty to include all)
INCLUDE_PATTERNS = [
    "**/*.txt",
    "**/*.md",
    "**/*.pdf",
    "**/*.docx",
    "**/*.py",   # Include code files
    "**/*.rst",  # ReStructuredText
]

# Patterns to exclude
EXCLUDE_PATTERNS = [
    "**/.git/**",
    "**/node_modules/**",
    "**/__pycache__/**",
    "**/*.pyc",
    "**/.DS_Store",
    "**/Thumbs.db",
    "**/*.tmp",
    "**/*.log",
    "**/.*/**",  # Hidden directories
]

# Processing settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3.1:8b"

# Database settings
VECTOR_DB_PATH = "./chroma_db"
COLLECTION_NAME = "documents"

# Retrieval settings
RETRIEVAL_K = 4  # Number of chunks to retrieve
TEMPERATURE = 0.1  # LLM temperature

# Optional: Filter by file modification time (days)
# Only process files modified in the last N days (0 = all files)
MAX_FILE_AGE_DAYS = 0

def validate_paths():
    """Check if document paths exist"""
    missing_paths = []
    for path in DOCUMENT_PATHS:
        if not os.path.exists(path):
            missing_paths.append(path)

    if missing_paths:
        print(f"Warning: These paths don't exist:")
        for path in missing_paths:
            print(f"  - {path}")
        return False
    return True

def get_valid_paths():
    """Return only existing paths"""
    return [path for path in DOCUMENT_PATHS if os.path.exists(path)]
