#!/bin/bash

# Stop the Local RAG Server

echo "Stopping Local RAG Server..."

# Check if the server is running
if pgrep -f "python.*web_rag" > /dev/null; then
    # Kill the process
    pkill -f "python.*web_rag"
    echo "✅ Server stopped successfully"
else
    echo "ℹ️  Server is not running"
fi

# Double-check
sleep 1
if pgrep -f "python.*web_rag" > /dev/null; then
    echo "⚠️  Server still running, forcing stop..."
    pkill -9 -f "python.*web_rag"
    echo "✅ Server force stopped"
fi

# Show any remaining Python processes (for debugging)
remaining=$(ps aux | grep -E "python.*web_rag" | grep -v grep | wc -l)
if [ "$remaining" -gt 0 ]; then
    echo "⚠️  Warning: Some processes may still be running:"
    ps aux | grep -E "python.*web_rag" | grep -v grep
else
    echo "✅ All web_rag processes stopped"
fi
