import sys
import argparse
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from config import (
    EMBEDDING_MODEL, VECTOR_DB_PATH, LLM_MODEL, 
    get_mode_config, DEFAULT_MODE
)

# Try to import the SHOW_SOURCES setting from config, default to True if not present
try:
    from config import SHOW_SOURCES
except ImportError:
    SHOW_SOURCES = True

def query_rag(question, return_sources=True, mode="qa"):
    """
    Query the RAG system with specified mode
    
    Args:
        question: The question to ask
        return_sources: Whether to return source documents
        mode: "qa" for precise Q&A, "summary" for comprehensive analysis, or "extract" for systematic extraction
    """
    # Extract mode uses a different script
    if mode == "extract":
        print("Extract mode uses a dedicated script. Please use:")
        print("  python extract_documents.py 'your extraction query'")
        return None
    
    # Get mode-specific configuration
    config = get_mode_config(mode)
    
    # Initialize embeddings
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    
    # Load the existing vector store
    vectorstore = Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embeddings
    )
    
    # Initialize the LLM with mode-specific temperature
    llm = OllamaLLM(model=LLM_MODEL, temperature=config["TEMPERATURE"])
    
    # Create a retriever with mode-specific parameters
    retriever_kwargs = {
        "k": config["RETRIEVAL_K"],
    }
    
    # Add MMR-specific parameters if using MMR search
    if config["RETRIEVAL_SEARCH_TYPE"] == "mmr":
        retriever_kwargs["fetch_k"] = config["RETRIEVAL_FETCH_K"]
        retriever_kwargs["lambda_mult"] = config["RETRIEVAL_LAMBDA_MULT"]
    
    retriever = vectorstore.as_retriever(
        search_type=config["RETRIEVAL_SEARCH_TYPE"],
        search_kwargs=retriever_kwargs
    )
    
    # Use mode-specific prompt template
    QA_CHAIN_PROMPT = PromptTemplate(
        input_variables=["context", "question"],
        template=config["PROMPT_TEMPLATE"],
    )
    
    # Create the QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=return_sources,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )
    
    # Get the answer
    result = qa_chain.invoke({"query": question})
    
    return result

def main(show_sources=None, mode=None):
    # Use the provided values, or fall back to config defaults
    if show_sources is None:
        show_sources = SHOW_SOURCES
    if mode is None:
        mode = DEFAULT_MODE
        
    print("=" * 80)
    print("RAG Query System - Triple Mode")
    print("=" * 80)
    print(f"Current mode: {mode.upper()}")
    
    if mode != "extract":
        config = get_mode_config(mode)
        print(f"Retrieval: {config['RETRIEVAL_SEARCH_TYPE'].upper()} (k={config['RETRIEVAL_K']}, temp={config['TEMPERATURE']})")
    print(f"Source display: {'ON' if show_sources else 'OFF'}")
    print("\nCommands:")
    print("  - Type 'quit' or 'exit' to quit")
    print("  - Type 'mode qa', 'mode summary', or 'mode extract' to switch modes")
    print("  - Type 'sources on' or 'sources off' to toggle source display")
    print("\nNote: Extract mode requires using extract_documents.py script")
    print("=" * 80 + "\n")
    
    while True:
        question = input("Ask a question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        # Handle mode switching
        if question.lower().startswith('mode '):
            new_mode = question.lower().replace('mode ', '').strip()
            if new_mode in ['qa', 'summary', 'extract']:
                mode = new_mode
                if mode == "extract":
                    print(f"\n✓ Switched to {mode.upper()} mode")
                    print(f"  Use: python extract_documents.py 'extraction query'\n")
                else:
                    config = get_mode_config(mode)
                    print(f"\n✓ Switched to {mode.upper()} mode")
                    print(f"  Retrieval: {config['RETRIEVAL_SEARCH_TYPE'].upper()} (k={config['RETRIEVAL_K']}, temp={config['TEMPERATURE']})\n")
            else:
                print(f"\n✗ Invalid mode. Use 'mode qa', 'mode summary', or 'mode extract'\n")
            continue
        
        # Handle source toggle commands
        if question.lower() in ['sources on', 'source on']:
            show_sources = True
            print("✓ Source display turned ON\n")
            continue
        elif question.lower() in ['sources off', 'source off']:
            show_sources = False
            print("✓ Source display turned OFF\n")
            continue
        
        if not question:
            print("Please enter a question.\n")
            continue
        
        if mode == "extract":
            print("\n✗ Extract mode requires using the dedicated script:")
            print(f"  python extract_documents.py '{question}'\n")
            continue
        
        print(f"\n[{mode.upper()} mode] Searching for answer...\n")
        
        try:
            result = query_rag(question, return_sources=show_sources, mode=mode)
            
            if result:
                print("Answer:", result['result'])
                
                if show_sources and 'source_documents' in result:
                    print(f"\nSource Documents ({len(result.get('source_documents', []))}):")
                    for i, doc in enumerate(result.get('source_documents', []), 1):
                        source = doc.metadata.get('source', 'Unknown')
                        print(f"{i}. {source}")
                        print(f"   Content: {doc.page_content[:150]}...")
                
                print("\n" + "="*80 + "\n")
            
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Query RAG system with triple mode support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive QA mode
  python rag_query.py
  
  # Interactive summary mode
  python rag_query.py --mode summary
  
  # Single question in QA mode
  python rag_query.py "What are nicotine pouches?"
  
  # Single question in summary mode
  python rag_query.py --mode summary "Summarize all research on health effects"
  
  # Extract mode (uses separate script)
  python extract_documents.py "List all chemicals mentioned"
        """
    )
    parser.add_argument('question', nargs='*', help='Question to ask (optional for interactive mode)')
    parser.add_argument('--no-sources', action='store_true', help='Disable source document display')
    parser.add_argument('--sources', action='store_true', help='Enable source document display (default)')
    parser.add_argument('--mode', choices=['qa', 'summary'], default=DEFAULT_MODE, 
                       help='Retrieval mode: "qa" for precise Q&A, "summary" for comprehensive analysis')
    
    args = parser.parse_args()
    
    # Determine whether to show sources
    if args.no_sources:
        show_sources = False
    elif args.sources:
        show_sources = True
    else:
        show_sources = SHOW_SOURCES  # Use config default
    
    if args.question:
        # If command line argument provided, use it as the question
        question = " ".join(args.question)
        try:
            result = query_rag(question, return_sources=show_sources, mode=args.mode)
            if result:
                print(f"[{args.mode.upper()} mode]")
                print("Answer:", result['result'])
                
                if show_sources and 'source_documents' in result:
                    print(f"\nSource Documents ({len(result.get('source_documents', []))}):")
                    for i, doc in enumerate(result.get('source_documents', []), 1):
                        source = doc.metadata.get('source', 'Unknown')
                        print(f"{i}. {source}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        # Interactive mode
        main(show_sources=show_sources, mode=args.mode)
