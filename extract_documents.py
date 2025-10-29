"""
Extract structured information from all documents using map-reduce pattern.
This systematically processes each document to extract specific information.
"""

import json
import time
from collections import defaultdict
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from config import (
    EMBEDDING_MODEL, VECTOR_DB_PATH, LLM_MODEL, 
    EXTRACT_MODE, get_mode_config
)

def get_all_documents_by_source(vectorstore):
    """
    Group all chunks by their source document
    Returns: dict {source_path: [chunks]}
    """
    collection = vectorstore._collection
    all_data = collection.get(include=["metadatas", "documents"])
    
    docs_by_source = defaultdict(list)
    
    for i, metadata in enumerate(all_data["metadatas"]):
        source = metadata.get("source", "Unknown")
        content = all_data["documents"][i]
        docs_by_source[source].append(content)
    
    return docs_by_source

def extract_from_document(llm, document_chunks, extraction_query, map_prompt):
    """
    Extract information from a single document's chunks (MAP phase)
    """
    # Combine chunks from the same document (limit to avoid overflow)
    combined_content = "\n\n".join(document_chunks[:15])  # Reduced from 20 to 15
    
    # Truncate if too long
    if len(combined_content) > 5000:  # Reduced from 6000
        combined_content = combined_content[:5000] + "..."
    
    prompt = PromptTemplate(
        input_variables=["extraction_query", "context"],
        template=map_prompt
    )
    
    formatted_prompt = prompt.format(
        extraction_query=extraction_query,
        context=combined_content
    )
    
    result = llm.invoke(formatted_prompt)
    return result

def reduce_extractions(llm, extractions, extraction_query, reduce_prompt):
    """
    Combine and deduplicate extracted information (REDUCE phase)
    """
    # Combine all extractions
    combined_extractions = "\n\n---\n\n".join([
        f"From {source.split('/')[-1]}:\n{extraction}" 
        for source, extraction in extractions.items()
    ])
    
    # Truncate if too long
    if len(combined_extractions) > 8000:  # Reduced from 10000
        combined_extractions = combined_extractions[:8000] + "\n\n[... truncated for length ...]"
    
    prompt = PromptTemplate(
        input_variables=["extraction_query", "summaries"],
        template=reduce_prompt
    )
    
    formatted_prompt = prompt.format(
        extraction_query=extraction_query,
        summaries=combined_extractions
    )
    
    result = llm.invoke(formatted_prompt)
    return result

def extract_from_all_documents(extraction_query, output_file=None, verbose=True, max_docs=None):
    """
    Main extraction function - processes all documents systematically
    
    Args:
        extraction_query: What to extract (e.g., "List all chemicals mentioned")
        output_file: Optional file path to save results
        verbose: Print progress
        max_docs: Limit number of documents to process (for testing)
    """
    config = get_mode_config("extract")
    
    if verbose:
        print("=" * 80)
        print("Document Extraction Mode")
        print("=" * 80)
        print(f"Extraction query: {extraction_query}")
        print(f"Temperature: {config['TEMPERATURE']}")
        if max_docs:
            print(f"Max documents: {max_docs}")
        print("=" * 80 + "\n")
    
    # Initialize
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embeddings
    )
    
    llm = OllamaLLM(model=LLM_MODEL, temperature=config["TEMPERATURE"])
    
    # Get all documents grouped by source
    if verbose:
        print("Loading documents from database...")
    docs_by_source = get_all_documents_by_source(vectorstore)
    
    # Limit documents if specified
    if max_docs and max_docs < len(docs_by_source):
        docs_by_source = dict(list(docs_by_source.items())[:max_docs])
    
    if verbose:
        print(f"Processing {len(docs_by_source)} documents\n")
        print("=" * 80)
        print("MAP PHASE: Extracting from each document")
        print("=" * 80 + "\n")
    
    # MAP phase: Extract from each document
    extractions = {}
    start_time = time.time()
    
    for i, (source, chunks) in enumerate(docs_by_source.items(), 1):
        doc_start = time.time()
        
        if verbose:
            filename = source.split('/')[-1]
            print(f"[{i}/{len(docs_by_source)}] Processing: {filename[:60]}")
        
        try:
            extraction = extract_from_document(
                llm, 
                chunks, 
                extraction_query,
                config["MAP_PROMPT_TEMPLATE"]
            )
            extractions[source] = extraction
            
            doc_time = time.time() - doc_start
            
            if verbose:
                # Show preview and timing
                preview = extraction[:100].replace('\n', ' ')
                print(f"    Time: {doc_time:.1f}s | Preview: {preview}...")
                
                # Estimate remaining time
                avg_time = (time.time() - start_time) / i
                remaining = avg_time * (len(docs_by_source) - i)
                print(f"    ETA: {remaining/60:.1f} minutes remaining")
                
        except Exception as e:
            if verbose:
                print(f"    Error: {e}")
            extractions[source] = f"Error: {str(e)}"
        
        print()
    
    # REDUCE phase: Combine all extractions
    if verbose:
        print("=" * 80)
        print("REDUCE PHASE: Combining all extractions")
        print("=" * 80 + "\n")
    
    try:
        final_result = reduce_extractions(
            llm,
            extractions,
            extraction_query,
            config["REDUCE_PROMPT_TEMPLATE"]
        )
    except Exception as e:
        if verbose:
            print(f"Error in reduce phase: {e}")
        final_result = "Error combining results"
    
    # Save to file if requested
    if output_file:
        output_data = {
            "extraction_query": extraction_query,
            "total_documents": len(docs_by_source),
            "individual_extractions": {k.split('/')[-1]: v for k, v in extractions.items()},
            "final_result": final_result
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        if verbose:
            print(f"\nResults saved to: {output_file}\n")
    
    total_time = time.time() - start_time
    if verbose:
        print(f"\nTotal processing time: {total_time/60:.1f} minutes")
    
    return {
        "query": extraction_query,
        "individual_extractions": extractions,
        "final_result": final_result
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Extract structured information from all documents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract all chemicals mentioned (test with 5 docs)
  python extract_documents.py "List all chemicals and substances mentioned" --max-docs 5
  
  # Extract health effects from all docs and save to file
  python extract_documents.py "What health effects are described?" -o results.json
  
  # Extract authors and publication info (quiet mode)
  python extract_documents.py "Extract: authors, publication date, journal name" -o metadata.json -q
        """
    )
    
    parser.add_argument('query', help='What information to extract from documents')
    parser.add_argument('-o', '--output', help='Output file to save results (JSON format)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Minimal output')
    parser.add_argument('--max-docs', type=int, help='Limit number of documents to process (for testing)')
    
    args = parser.parse_args()
    
    result = extract_from_all_documents(
        args.query, 
        output_file=args.output,
        verbose=not args.quiet,
        max_docs=args.max_docs
    )
    
    print("\n" + "=" * 80)
    print("FINAL COMBINED RESULT")
    print("=" * 80 + "\n")
    print(result["final_result"])
    print("\n" + "=" * 80)
