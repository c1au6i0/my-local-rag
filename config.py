import os

# Document sources - add your paths here
DOCUMENT_PATHS = [
    "/home/heverz/py_projects/local-rag/documents/",
    "/home/heverz/docs/docs_clz/work/pouched_products/"
]

# File patterns to include (leave empty to include all)
INCLUDE_PATTERNS = [
    "**/*.txt",
    "**/*.md",
    "**/*.pdf",
    "**/*.docx",
    "**/*.py",   # Include code files
    "**/*.rst",  # ReStructuredText
    "**/*.html",  # HTML files
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

# Processing settings - optimized for semantic chunking
CHUNK_SIZE = 512  # Reduced for more precise retrieval and better semantic coherence
CHUNK_OVERLAP = 128  # 25% overlap to preserve context at chunk boundaries
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3.1:8b"

# Database settings
VECTOR_DB_PATH = "./chroma_db"
COLLECTION_NAME = "documents"

# ============================================================================
# TRIPLE MODE CONFIGURATION
# ============================================================================

# Mode selection: "qa", "summary", or "extract"
DEFAULT_MODE = "qa"  # Change default mode here

# QA Mode - For precise question answering
QA_MODE = {
    "RETRIEVAL_K": 5,  # Top-5 most relevant chunks
    "RETRIEVAL_SEARCH_TYPE": "mmr",  # Maximum Marginal Relevance
    "RETRIEVAL_FETCH_K": 20,  # Fetch more candidates for reranking
    "RETRIEVAL_LAMBDA_MULT": 0.7,  # Balance relevance vs diversity
    "TEMPERATURE": 0.1,  # Low temperature for factual responses
    "PROMPT_TEMPLATE": """Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Use three sentences maximum and keep the answer concise and focused on the most relevant information.
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:"""
}

# Summary Mode - For comprehensive document analysis/summarization
SUMMARY_MODE = {
    "RETRIEVAL_K": 50,  # Retrieve many chunks for comprehensive view
    "RETRIEVAL_SEARCH_TYPE": "similarity",  # Pure similarity (no diversity penalty)
    "RETRIEVAL_FETCH_K": 100,  # Not used in similarity mode
    "RETRIEVAL_LAMBDA_MULT": 1.0,  # Full relevance weight
    "TEMPERATURE": 0.3,  # Slightly higher for more creative summarization
    "PROMPT_TEMPLATE": """Based on the following document excerpts, provide a comprehensive answer or summary.
    Consider all the context provided and synthesize the information into a coherent response.
    Be thorough and include key details, themes, and insights from the documents.
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:"""
}

# Extract Mode - For systematic extraction across all documents
EXTRACT_MODE = {
    "TEMPERATURE": 0.0,  # Zero temperature for consistent extraction
    "BATCH_SIZE": 10,  # Number of documents to process per batch
    "MAP_PROMPT_TEMPLATE": """Extract the following information from this document excerpt:

{extraction_query}

Document content:
{context}

Provide a structured extraction. If information is not found, state "Not mentioned".

Extraction:""",
    "REDUCE_PROMPT_TEMPLATE": """Combine and deduplicate the following extracted information from multiple documents.
Remove redundancies and organize the data in a clear, structured format.

Extraction query: {extraction_query}

Extracted data from documents:
{summaries}

Combined result:"""
}

# Get current mode settings (defaults to QA_MODE)
def get_mode_config(mode=None):
    """Get configuration for specified mode"""
    if mode is None:
        mode = DEFAULT_MODE
    
    mode_lower = mode.lower()
    if mode_lower == "summary":
        return SUMMARY_MODE
    elif mode_lower == "extract":
        return EXTRACT_MODE
    else:
        return QA_MODE

# Legacy compatibility - use default mode settings
_current_mode = get_mode_config(DEFAULT_MODE)
if DEFAULT_MODE != "extract":
    RETRIEVAL_K = _current_mode["RETRIEVAL_K"]
    RETRIEVAL_SEARCH_TYPE = _current_mode["RETRIEVAL_SEARCH_TYPE"]
    RETRIEVAL_FETCH_K = _current_mode["RETRIEVAL_FETCH_K"]
    RETRIEVAL_LAMBDA_MULT = _current_mode["RETRIEVAL_LAMBDA_MULT"]
    TEMPERATURE = _current_mode["TEMPERATURE"]
else:
    # Extract mode doesn't use retrieval
    RETRIEVAL_K = 5
    RETRIEVAL_SEARCH_TYPE = "similarity"
    RETRIEVAL_FETCH_K = 20
    RETRIEVAL_LAMBDA_MULT = 1.0
    TEMPERATURE = EXTRACT_MODE["TEMPERATURE"]

# Advanced retrieval settings
SIMILARITY_SCORE_THRESHOLD = 0.5  # Minimum similarity score for retrieved chunks
MAX_CONTEXT_LENGTH = 8000  # Maximum characters to send to LLM as context

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

# Display settings
SHOW_SOURCES = True  # Set to False to hide source documents by default
