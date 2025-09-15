#!/usr/bin/env python3
"""Test the web RAG server"""

import requests
import json
import time

def test_web_server():
    base_url = "http://localhost:5000"
    
    # Test health endpoint
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the web server first.")
        print("Run: pixi run python web_rag.py")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test query endpoint
    print("\nTesting query endpoint...")
    test_question = "What are nicotine pouches?"
    
    try:
        response = requests.post(
            f"{base_url}/query",
            json={"question": test_question},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Query successful!")
            print(f"Question: {test_question}")
            print(f"Answer: {data.get('answer', 'No answer')[:200]}...")
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error querying: {e}")
    
    # Test web interface
    print("\nTesting web interface...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Web interface is accessible")
            print(f"   Visit http://localhost:5000 in your browser")
        else:
            print(f"❌ Web interface returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing web interface: {e}")

if __name__ == "__main__":
    test_web_server()
