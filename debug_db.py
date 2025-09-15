import chromadb
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from config import VECTOR_DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL

def debug_chroma():
    # Direct ChromaDB access
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    collections = client.list_collections()
    print(f"Available collections: {collections}")
    
    # Try to access via Langchain Chroma
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embeddings
    )
    
    # Try to get documents through langchain
    try:
        # Get the underlying collection
        collection = vectorstore._collection
        count = collection.count()
        print(f"Document count via Langchain: {count}")
        
        # Get some documents
        if count > 0:
            results = collection.get(limit=3, include=["metadatas", "documents"])
            print(f"\nFirst few documents:")
            for i, doc in enumerate(results["documents"]):
                print(f"\nDocument {i+1}:")
                print(f"Content: {doc[:200]}...")
                if results["metadatas"] and i < len(results["metadatas"]):
                    print(f"Metadata: {results['metadatas'][i]}")
    except Exception as e:
        print(f"Error accessing documents: {e}")

if __name__ == "__main__":
    debug_chroma()
