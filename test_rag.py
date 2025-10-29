import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_query import query_rag

print("Testing RAG query...")
result = query_rag("What is nicotine?")

if isinstance(result, dict):
    answer = result.get('result', 'No result')
    sources = result.get('source_documents', [])
    print(f"Answer: {answer[:200]}...")
    print(f"Sources found: {len(sources)}")
    if sources:
        print(f"First source: {sources[0].metadata.get('source', 'Unknown')}")
else:
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
