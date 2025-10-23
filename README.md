# Local RAG System

A local Retrieval-Augmented Generation (RAG) system using ChromaDB and Ollama.

## Project Structure

```
local-rag/
├── config.py              # Configuration settings for the RAG system
├── process_docs.py        # Script to process and index documents into ChromaDB
├── rag_query.py          # Script to query the RAG system
├── check_db.py           # Script to check the database contents
├── debug_db.py           # Database debugging utilities
├── test_rag.py           # Test script for RAG functionality
├── documents/            # Folder containing documents to be indexed
├── chroma_db/            # ChromaDB vector database storage
├── other/                # Development/experimental features (web interface, etc.)
│   ├── web_rag.py       # Flask-based web server (in development)
│   ├── test_web.py      # Web server testing script
│   ├── start_server.sh  # Script to start the web server
│   ├── stop_server.sh   # Script to stop the web server
│   └── NETWORK_ACCESS.md # Network access documentation
├── pixi.toml             # Pixi dependency configuration
└── pixi.lock             # Pixi lock file
```

## Prerequisites

### Ollama Installation

This RAG system requires Ollama to be installed and running on your machine. Ollama provides the local LLM capabilities.

**Installation:**

- **macOS/Linux:** 
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```

- **Windows:** Download from [ollama.com](https://ollama.com/download)

**Start Ollama:**
```bash
ollama serve
```

**Required Models:**

The system uses the following models by default (configured in `config.py`):
- **LLM:** `llama3.1:8b` - For text generation
- **Embeddings:** `nomic-embed-text` - For document embeddings

Pull these models before running the RAG system:
```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

**Verify Ollama is Running:**
```bash
ollama list  # Should show installed models
```

## Setup

The project uses Pixi for dependency management. All dependencies are already configured in `pixi.toml`.

## Usage

### 1. Process Documents

To index documents into the vector database:

```bash
pixi run python process_docs.py
```

This will process all documents in the `documents/` folder and create embeddings in ChromaDB.

### 2. Query the System

You can query the RAG system in two ways:

**Interactive mode:**
```bash
pixi run python rag_query.py
```

**Command line mode:**
```bash
pixi run python rag_query.py "Your question here"
```

Example:
```bash
pixi run python rag_query.py "What are nicotine pouches?"
```

### 3. Check Database Contents

To view the documents stored in the database:

```bash
pixi run python check_db.py
```

### 4. Test the System

To run tests on the RAG functionality:

```bash
pixi run python test_rag.py
```

## Configuration

Edit `config.py` to modify:
- Document paths
- Chunk size and overlap
- Embedding model (default: nomic-embed-text)
- LLM model (default: llama3.1:8b)
- Number of chunks to retrieve

## Core Files

- `config.py` - Central configuration for the system
- `process_docs.py` - Document processing and indexing pipeline
- `rag_query.py` - Core RAG functionality with query interface
- `check_db.py` / `fixed_check_db.py` - Database inspection utilities
- `debug_db.py` - Database debugging tools
- `test_rag.py` - Testing suite for RAG system

## Development Features

The `other/` directory contains experimental and development features:

- **Web Interface** (in development): A Flask-based web server providing a browser interface for the RAG system
  - See `other/NETWORK_ACCESS.md` for network configuration details
  - Use `other/start_server.sh` and `other/stop_server.sh` for server management

## Notes

- The system uses the default "langchain" collection in ChromaDB
- Documents are automatically chunked for better retrieval performance
- Ensure Ollama is running before starting any RAG operations
