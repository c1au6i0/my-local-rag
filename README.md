# Local RAG System

A local Retrieval-Augmented Generation (RAG) system using ChromaDB and Ollama with **three operational modes** for different use cases.

## Project Structure

```
local-rag/
├── config.py              # Configuration settings with triple-mode support
├── process_docs.py        # Script to process and index documents into ChromaDB
├── rag_query.py          # Triple-mode query interface (QA, Summary, Extract)
├── extract_documents.py  # Systematic document extraction using map-reduce
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

**Configuration:** The system uses optimized chunking parameters:
- **Chunk Size:** 512 tokens (for semantic coherence)
- **Chunk Overlap:** 128 tokens (25% overlap for context preservation)

### 2. Query the System - Triple Mode

The RAG system now supports **three operational modes**, each optimized for different use cases:

#### **Mode 1: QA Mode** (Quick & Precise)

For specific questions requiring precise answers from the most relevant documents.

**Parameters:**
- Retrieves top-5 most relevant chunks
- Uses MMR (Maximum Marginal Relevance) for diversity
- Low temperature (0.1) for factual responses

**Usage:**
```bash
# Interactive mode
pixi run python rag_query.py

# Single question
pixi run python rag_query.py "What are nicotine pouches?"

# Without sources
pixi run python rag_query.py --no-sources "What health effects are documented?"
```

#### **Mode 2: Summary Mode** (Comprehensive Analysis)

For broad questions requiring comprehensive analysis from many documents.

**Parameters:**
- Retrieves top-50 most relevant chunks
- Uses similarity search for maximum relevance
- Higher temperature (0.3) for synthesized responses

**Usage:**
```bash
# Interactive mode
pixi run python rag_query.py --mode summary

# Single question
pixi run python rag_query.py --mode summary "Summarize all health effects research"

# Save output to file
pixi run python rag_query.py --mode summary "Overview of nicotine pouch research" > summary.txt
```

#### **Mode 3: Extract Mode** (Systematic Data Extraction)

For extracting structured information from **ALL documents** systematically using map-reduce pattern. This mode processes every document individually, then combines results.

**Parameters:**
- Zero temperature (0.0) for consistent extraction
- Processes documents in batches
- Map-reduce approach for comprehensive coverage

**Usage:**
```bash
# Test with limited documents first
pixi run python extract_documents.py "List all chemicals mentioned" --max-docs 5

# Extract from all documents and save to JSON
pixi run python extract_documents.py "List all chemicals mentioned" -o chemicals.json

# Extract metadata
pixi run python extract_documents.py "Extract: title, authors, publication year, journal" -o metadata.json

# Classify papers
pixi run python extract_documents.py "Classify each paper as: Review Article, Original Research, or Meta-Analysis" -o paper_types.json

# Find specific mentions
pixi run python extract_documents.py "Which papers mention ONP? List paper title and what they say about ONP" -o onp_papers.json

# Quiet mode (minimal output)
pixi run python extract_documents.py "Extract study designs and sample sizes" -o studies.json -q
```

**⏱️ Performance Note:** Extract mode processes each document through the LLM sequentially. For 100 documents, expect 30-60 minutes processing time. Always test with `--max-docs 5` first.

**Extract Mode Features:**
- ✅ Processes **every document** systematically (not just retrieved chunks)
- ✅ Real-time progress tracking with ETA
- ✅ Handles missing information gracefully ("Not mentioned")
- ✅ Can infer/classify based on content (e.g., paper types)
- ✅ Saves individual extractions + combined results to JSON
- ✅ Deduplicates and structures final output

### 3. Interactive Mode Commands

In interactive mode (`pixi run python rag_query.py`), you can use these commands:

```bash
# Switch modes
mode qa          # Switch to QA mode
mode summary     # Switch to Summary mode
mode extract     # (Shows extract_documents.py usage)

# Toggle source display
sources on       # Show source documents
sources off      # Hide source documents

# Exit
quit             # or 'exit' or 'q'
```

### 4. Check Database Contents

To view the documents and chunks stored in the database:

```bash
pixi run python check_db.py
```

### 5. Test the System

To run tests on the RAG functionality:

```bash
pixi run python test_rag.py
```

## Configuration

Edit `config.py` to modify system behavior. The configuration now includes mode-specific settings:

### General Settings
- **Document paths:** Where to find documents to index
- **Chunk size:** 512 tokens (optimized for semantic coherence)
- **Chunk overlap:** 128 tokens (25% overlap)
- **Embedding model:** nomic-embed-text
- **LLM model:** llama3.1:8b

### Mode-Specific Settings

**QA Mode:**
- `RETRIEVAL_K`: 5 chunks
- `RETRIEVAL_SEARCH_TYPE`: "mmr" (Maximum Marginal Relevance)
- `TEMPERATURE`: 0.1 (factual)

**Summary Mode:**
- `RETRIEVAL_K`: 50 chunks
- `RETRIEVAL_SEARCH_TYPE`: "similarity" (relevance-focused)
- `TEMPERATURE`: 0.3 (synthesized)

**Extract Mode:**
- `TEMPERATURE`: 0.0 (consistent)
- `BATCH_SIZE`: 10 documents per batch
- Custom prompts for map-reduce extraction

Change the default mode:
```python
DEFAULT_MODE = "qa"  # or "summary" or "extract"
```

## Use Case Guide

| Task | Recommended Mode | Example |
|------|------------------|---------|
| Quick fact lookup | **QA Mode** | "What is the nicotine content in ZYN?" |
| Literature review | **Summary Mode** | "Summarize all health effects research" |
| Data extraction | **Extract Mode** | "List all chemicals in each paper" |
| Finding papers | **Extract Mode** | "Which papers mention oral nicotine pouches?" |
| Classification | **Extract Mode** | "Classify papers as review or original research" |
| Metadata extraction | **Extract Mode** | "Extract: title, authors, year, journal" |

## Core Files

- `config.py` - Central configuration with triple-mode support
- `process_docs.py` - Document processing and indexing pipeline
- `rag_query.py` - Triple-mode RAG interface (QA, Summary, Extract-aware)
- `extract_documents.py` - **NEW:** Systematic extraction with map-reduce
- `check_db.py` - Database inspection utilities
- `debug_db.py` - Database debugging tools
- `test_rag.py` - Testing suite for RAG system

## Advanced Examples

### Extract Mode Examples

```bash
# Extract chemicals with health effects
pixi run python extract_documents.py "For each paper, list: 1) Chemicals mentioned, 2) Associated health effects" -o chemicals_effects.json

# Find papers with specific criteria
pixi run python extract_documents.py "List papers that discuss cardiovascular effects. Include paper title and main findings" -o cardio_papers.json

# Extract study characteristics
pixi run python extract_documents.py "Extract: Study type (RCT/observational/review), Sample size, Population studied, Main outcome" -o study_design.json

# Comparative analysis
pixi run python extract_documents.py "Compare nicotine concentrations reported across papers" -o nicotine_comparison.json
```

### Summary Mode Examples

```bash
# Comprehensive topic overview
pixi run python rag_query.py --mode summary "What are the main health concerns with nicotine pouches?"

# Research trends
pixi run python rag_query.py --mode summary "What research methodologies are commonly used?"

# Synthesize findings
pixi run python rag_query.py --mode summary "Summarize contradictory findings across studies"
```

### QA Mode Examples

```bash
# Specific factual questions
pixi run python rag_query.py "What is the FDA's stance on nicotine pouches?"

# Quick lookups
pixi run python rag_query.py "What brands are mentioned most frequently?"

# Definition queries
pixi run python rag_query.py "What is snus?"
```

## Development Features

The `other/` directory contains experimental and development features:

- **Web Interface** (in development): A Flask-based web server providing a browser interface for the RAG system
  - See `other/NETWORK_ACCESS.md` for network configuration details
  - Use `other/start_server.sh` and `other/stop_server.sh` for server management

## Performance & Optimization

### Chunk Size Impact
The system uses 512-token chunks (reduced from 1000) for:
- More precise semantic matching
- Better retrieval accuracy
- Reduced noise in results

### Mode Performance Comparison

| Mode | Speed | Coverage | Best For |
|------|-------|----------|----------|
| QA | ⚡ Fast (seconds) | 5 chunks | Specific questions |
| Summary | 🏃 Medium (seconds) | 50 chunks | Broad overviews |
| Extract | 🐌 Slow (30-60 min for 100 docs) | All documents | Systematic extraction |

## Notes

- The system uses the default "langchain" collection in ChromaDB
- Documents are automatically chunked with optimized parameters (512/128)
- Ensure Ollama is running before starting any RAG operations
- Extract mode processes documents sequentially - use `--max-docs` for testing
- All modes support source citation display (toggle with `--sources`/`--no-sources`)
- JSON output from extract mode is structured for programmatic processing

## Troubleshooting

**Extract mode is slow:**
- This is expected behavior - it processes every document through the LLM
- Use `--max-docs 5` to test before full runs
- Consider running overnight for large document sets

**Out of context errors:**
- Reduce `MAX_CONTEXT_LENGTH` in config.py
- Reduce chunk size or retrieval count

**Poor retrieval quality:**
- Try different modes (Summary for broader coverage)
- Adjust temperature settings in config.py
- Rephrase your query to be more specific

**Database issues:**
- Run `check_db.py` to verify contents
- Reprocess documents with `process_docs.py` if needed
