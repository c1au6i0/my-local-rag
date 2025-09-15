#!/usr/bin/env python3
"""
Fixed Web RAG Server - Accessible from network
"""

from flask import Flask, request, jsonify, render_template_string, make_response
import socket
import logging
import sys
import os

# Add the current directory to path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import flask_cors, but work without it if not available
try:
    from flask_cors import CORS
    HAS_CORS = True
except ImportError:
    HAS_CORS = False
    print("Warning: flask-cors not available, using manual CORS headers")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the query function
try:
    from rag_query import query_rag
except ImportError as e:
    logger.error(f"Failed to import rag_query: {e}")
    # Create a dummy function for testing
    def query_rag(question):
        return {"result": f"Test response for: {question}. (Note: rag_query module not loaded)", "source_documents": []}

app = Flask(__name__)

# Enable CORS if available
if HAS_CORS:
    CORS(app)

# Manual CORS headers function
def add_cors_headers(response):
    """Add CORS headers to response"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Apply manual CORS if flask-cors not available
if not HAS_CORS:
    @app.after_request
    def after_request(response):
        return add_cors_headers(response)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Local RAG System</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 800px;
            width: 100%;
            padding: 40px;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2em;
        }
        .status-bar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 30px;
            font-size: 0.9em;
        }
        .status-bar strong {
            display: inline-block;
            margin-right: 10px;
        }
        .network-info {
            background: rgba(255,255,255,0.2);
            padding: 8px 12px;
            border-radius: 5px;
            margin-top: 10px;
            display: inline-block;
            font-family: 'Courier New', monospace;
        }
        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            resize: vertical;
            min-height: 120px;
            transition: border-color 0.3s;
        }
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            margin-top: 15px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        button:disabled {
            background: #cccccc;
            cursor: not-allowed;
            transform: none;
        }
        #answer {
            margin-top: 30px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 10px;
            min-height: 60px;
            border-left: 4px solid #667eea;
        }
        .loading {
            color: #666;
            font-style: italic;
            display: flex;
            align-items: center;
        }
        .loading::before {
            content: '';
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .error {
            color: #d32f2f;
            background-color: #ffebee;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #d32f2f;
        }
        .success {
            color: #2e7d32;
            background-color: #e8f5e9;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #4caf50;
        }
        h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Local RAG System</h1>
        <div class="status-bar">
            <strong>✅ Server Status:</strong> Online and Ready<br>
            <div class="network-info">
                <strong>Network Access:</strong> http://{{ host_ip }}:{{ port }}
            </div>
        </div>
        
        <form id="queryForm">
            <textarea id="question" 
                      placeholder="Ask any question about your documents..." 
                      autofocus></textarea>
            <button type="submit" id="submitBtn">
                Search Documents
            </button>
        </form>
        
        <div id="answer"></div>
    </div>
    
    <script>
        document.getElementById('queryForm').onsubmit = async (e) => {
            e.preventDefault();
            const question = document.getElementById('question').value.trim();
            
            if (!question) {
                document.getElementById('answer').innerHTML = 
                    '<div class="error">⚠️ Please enter a question.</div>';
                return;
            }
            
            const submitBtn = document.getElementById('submitBtn');
            const answerDiv = document.getElementById('answer');
            
            submitBtn.disabled = true;
            submitBtn.textContent = 'Searching...';
            answerDiv.innerHTML = '<div class="loading">Searching through your documents...</div>';
            
            try {
                const response = await fetch('/query', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question})
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.error) {
                    answerDiv.innerHTML = 
                        `<div class="error">❌ Error: ${data.error}</div>`;
                } else {
                    const formattedAnswer = data.answer
                        .replace(/\n\n/g, '</p><p>')
                        .replace(/\n/g, '<br>');
                    answerDiv.innerHTML = 
                        `<div class="success">
                            <h3>📄 Answer:</h3>
                            <p>${formattedAnswer}</p>
                        </div>`;
                }
            } catch (error) {
                answerDiv.innerHTML = 
                    `<div class="error">❌ Failed to get response: ${error.message}</div>`;
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Search Documents';
            }
        }
    </script>
</body>
</html>
"""

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Try to connect to an external server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        # Use Google's DNS server as a connection point
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        logger.warning(f"Could not determine local IP: {e}")
        # Fallback to hostname method
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            if local_ip.startswith("127."):
                return "localhost"
            return local_ip
        except:
            return "localhost"

@app.route('/')
def home():
    """Serve the main web interface"""
    host_ip = get_local_ip()
    port = request.environ.get('SERVER_PORT', 5000)
    return render_template_string(HTML_TEMPLATE, host_ip=host_ip, port=port)

@app.route('/query', methods=['POST', 'OPTIONS'])
def query():
    """Handle document queries"""
    # Handle preflight requests for CORS
    if request.method == 'OPTIONS':
        response = make_response()
        if not HAS_CORS:
            response = add_cors_headers(response)
        return response
    
    try:
        data = request.json
        if not data or 'question' not in data:
            return jsonify({'error': 'No question provided'}), 400
        
        question = data['question']
        logger.info(f"Processing query: {question}")
        
        # Call the RAG query function
        result = query_rag(question)
        
        # Extract the answer from the result
        if isinstance(result, dict) and 'result' in result:
            answer = result['result']
            sources = result.get('source_documents', [])
            # Format sources if available
            if sources:
                source_info = "\n\nSources:\n"
                for i, doc in enumerate(sources[:3], 1):  # Limit to 3 sources
                    source = doc.metadata.get('source', 'Unknown')
                    source_info += f"{i}. {source}\n"
                answer += source_info
        else:
            answer = str(result) if result else "I couldn't find relevant information in the documents to answer your question."
        
        if not answer or answer == "None":
            answer = "I couldn't find relevant information in the documents to answer your question. Please make sure documents have been processed."
        
        logger.info(f"Query processed successfully")
        return jsonify({'answer': answer})
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return jsonify({'error': f"Server error: {str(e)}"}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ip': get_local_ip(),
        'cors_enabled': HAS_CORS
    })

def main():
    """Main entry point"""
    local_ip = get_local_ip()
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "="*70)
    print("🚀 LOCAL RAG SERVER STARTING")
    print("="*70)
    print(f"📍 Local access:    http://localhost:{port}")
    print(f"🌐 Network access:  http://{local_ip}:{port}")
    print("\="*70)
    print("✅ Server is ready to accept connections from any device on your network")
    print(f"⚠️  Make sure port {port} is accessible through your firewall")
    print("💡 Tip: Share the network URL with other devices on your network")
    print("="*70 + "\n")
    
    # Run the Flask app
    try:
        app.run(
            host='0.0.0.0',  # Listen on all interfaces
            port=port,
            debug=False,  # Set to False for production
            threaded=True  # Enable threading for better performance
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
