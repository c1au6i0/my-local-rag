import chromadb
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from config import VECTOR_DB_PATH, EMBEDDING_MODEL

def view_vector_store_contents():
    try:
        # Initialize embeddings (must be the same as used for creation)
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        
        # Connect to the existing ChromaDB using Langchain
        # Don't specify collection_name to use the default "langchain" collection
        vectorstore = Chroma(
            persist_directory=VECTOR_DB_PATH,
            embedding_function=embeddings
        )
        
        # Get the underlying collection
        collection = vectorstore._collection
        count = collection.count()
        
        print(f"Connected to default Langchain collection with {count} items.")
        
        # Get some documents from the collection
        if count > 0:
            results = collection.get(limit=10, include=["metadatas", "documents"])
            
            print("\n--- SAMPLE DOCUMENTS ---")
            for i, doc in enumerate(results["documents"]):
                metadata = results["metadatas"][i] if results["metadatas"] else {}
                print(f"\nChunk {i + 1}:")
                print(f"Source: {metadata.get('source', 'N/A')}")
                print(f"Content: {doc[:200]}...") # Print a snippet of the content
                print("-" * 40)
        else:
            print("No documents found in the collection.")
    
    except Exception as e:
        print(f"An error occurred while trying to view the vector store: {e}")

if __name__ == "__main__":
    view_vector_store_contents()
