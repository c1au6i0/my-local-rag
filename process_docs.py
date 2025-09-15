import os
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, UnstructuredFileLoader
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from config import DOCUMENT_PATHS, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, VECTOR_DB_PATH, COLLECTION_NAME

def process_documents(docs_directories, db_path):
    documents = []

    for docs_directory in docs_directories:
        print(f"Loading documents from {docs_directory}...")

        # Use a single DirectoryLoader with UnstructuredFileLoader for all document types
        loader = DirectoryLoader(
            docs_directory,
            glob="**/*",
            loader_cls=UnstructuredFileLoader,
            silent_errors=True
        )
        loaded_docs = loader.load()
        documents.extend(loaded_docs)

    print(f"Total documents found: {len(documents)}")

    if not documents:
        print("Error: No documents were found in the specified directories. Please check your paths and file types.")
        return None

    # Split documents into chunks
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    splits = text_splitter.split_documents(documents)
    print(f"Split documents into {len(splits)} chunks.")

    if not splits:
        print("Error: No chunks were created. This may be due to empty documents.")
        return None

    # Create embeddings
    print(f"Creating embeddings using model '{EMBEDDING_MODEL}' and building vector store...")
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    # Create vector store
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=db_path
    )

    print(f"Successfully processed {len(documents)} documents into {len(splits)} chunks.")
    return vectorstore

if __name__ == "__main__":
    try:
        vectorstore = process_documents(DOCUMENT_PATHS, VECTOR_DB_PATH)
        if vectorstore:
            print("Successfully created vector store.")
    except Exception as e:
        print(f"An error occurred: {e}")
