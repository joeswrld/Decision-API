#!/bin/bash

# Decision Intelligence API - Quick Start Script
# This script launches both the API and browser UI

echo "========================================="
echo "Decision Intelligence API"
echo "========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.11+ from https://python.org"
    exit 1
fi

# Check if Gemini API key is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  Warning: GOOGLE_API_KEY not set"
    echo "The API will use fallback mode (rules only, no AI)"
    echo ""
    echo "To enable AI:"
    echo "  1. Get key from: https://makersuite.google.com/app/apikey"
    echo "  2. Run: export GOOGLE_API_KEY='your_key_here'"
    echo ""
    read -p "Continue without AI? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if dependencies are installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Start the API server
echo "🚀 Starting API server..."
echo "   - API: http://localhost:8000"
echo "   - Docs: http://localhost:8000/docs"
echo ""

# Kill any existing uvicorn process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start uvicorn in background
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!

# Wait for API to start
echo "⏳ Waiting for API to start..."
sleep 3

# Check if API is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Error: API failed to start"
    kill $API_PID 2>/dev/null
    exit 1
fi

echo "✅ API is running!"
echo ""

# Check if browser test UI exists
if [ -f "browser_test.html" ]; then
    echo "🌐 Opening browser test UI..."
    
    # Start a simple HTTP server for the HTML file
    python3 -m http.server 8080 --bind 127.0.0.1 > /dev/null 2>&1 &
    HTTP_PID=$!
    
    sleep 1
    
    # Try to open browser (works on Mac, Linux, Windows)
    if command -v open &> /dev/null; then
        open http://localhost:8080/browser_test.html
    elif command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:8080/browser_test.html
    elif command -v start &> /dev/null; then
        start http://localhost:8080/browser_test.html
    else
        echo "   Manual: Open http://localhost:8080/browser_test.html in your browser"
    fi
    
    echo "   - Browser UI: http://localhost:8080/browser_test.html"
else
    echo "ℹ️  Browser UI not found (browser_test.html)"
    echo "   You can still test at: http://localhost:8000/docs"
fi

echo ""
echo "========================================="
echo "✨ Decision Intelligence API is ready!"
echo "========================================="
echo ""
echo "Demo API Keys (pre-configured):"
echo "  Free:    sk_test_demo_free_key_12345678901234567890"
echo "  Starter: sk_test_demo_starter_key_1234567890123456"
echo "  Pro:     sk_test_demo_pro_key_123456789012345678"
echo ""
echo "Quick Test:"
echo '  curl -X POST http://localhost:8000/v1/decision \'
echo '    -H "Authorization: Bearer sk_test_demo_pro_key_123456789012345678" \'
echo '    -H "Content-Type: application/json" \'
echo '    -d '"'"'{"message": "I will sue you", "user_plan": "pro"}'"'"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for user to stop
wait $API_PID