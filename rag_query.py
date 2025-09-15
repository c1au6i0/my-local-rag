import sys
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from config import EMBEDDING_MODEL, VECTOR_DB_PATH, LLM_MODEL, RETRIEVAL_K, TEMPERATURE

def query_rag(question):
    # Initialize embeddings
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    
    # Load the existing vector store
    vectorstore = Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embeddings
    )
    
    # Initialize the LLM
    llm = OllamaLLM(model=LLM_MODEL, temperature=TEMPERATURE)
    
    # Create a retriever
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": RETRIEVAL_K}
    )
    
    # Create a custom prompt template
    template = """Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:"""
    
    QA_CHAIN_PROMPT = PromptTemplate(
        input_variables=["context", "question"],
        template=template,
    )
    
    # Create the QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )
    
    # Get the answer
    result = qa_chain.invoke({"query": question})
    
    return result

def main():
    print("RAG Query System")
    print("Type 'quit' to exit\n")
    
    while True:
        question = input("Ask a question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not question:
            print("Please enter a question.\n")
            continue
        
        print("\nSearching for answer...\n")
        
        try:
            result = query_rag(question)
            
            print("Answer:", result['result'])
            
            print("\nSource Documents:")
            for i, doc in enumerate(result.get('source_documents', []), 1):
                source = doc.metadata.get('source', 'Unknown')
                print(f"{i}. {source}")
                print(f"   Content: {doc.page_content[:150]}...")
            
            print("\n" + "="*80 + "\n")
            
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If command line argument provided, use it as the question
        question = " ".join(sys.argv[1:])
        try:
            result = query_rag(question)
            print("Answer:", result['result'])
            print("\nSource Documents:")
            for i, doc in enumerate(result.get('source_documents', []), 1):
                source = doc.metadata.get('source', 'Unknown')
                print(f"{i}. {source}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        # Interactive mode
        main()

# Add alias for web_rag compatibility
def query_documents(question):
    """Wrapper function for web_rag.py compatibility"""
    try:
        result = query_rag(question)
        return result['result']
    except Exception as e:
        return f"Error processing query: {str(e)}"

def query_documents(question):
    """
    Simple wrapper function for web interface compatibility.
    Returns just the answer text without metadata.
    """
    try:
        result = query_rag(question)
        return result.get('result', 'No answer found.')
    except Exception as e:
        return f"Error processing query: {str(e)}"
