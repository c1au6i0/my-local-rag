#!/bin/bash
# Start the Local RAG Web Server

echo "🚀 Starting Local RAG Web Server..."
echo "=================================="
echo ""

# Check if pixi is available
if ! command -v pixi &> /dev/null; then
    echo "❌ Error: pixi is not installed or not in PATH"
    echo "Please install pixi first: https://pixi.sh"
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Warning: Ollama doesn't seem to be running on port 11434"
    echo "   Make sure Ollama is installed and running"
    echo "   Run: ollama serve"
    echo ""
fi

# Start the server
echo "Starting web server..."
echo "Press Ctrl+C to stop"
echo ""
pixi run python web_rag.py
