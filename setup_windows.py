"""
Windows Setup Script for Decision Intelligence API
Run this to automatically create all necessary files
"""

import os
import sys

def create_file(filename, content):
    """Create a file with given content"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Created {filename}")
        return True
    except Exception as e:
        print(f"✗ Failed to create {filename}: {e}")
        return False

def main():
    print("=" * 60)
    print("Decision Intelligence API - Windows Setup")
    print("=" * 60)
    print()
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("⚠️  Warning: Python 3.9+ recommended")
        print(f"   Current version: {sys.version}")
        print()
    
    # Create minimal main.py
    main_py = '''"""
Decision Intelligence API - Minimal Version
This is a simplified version to get you started quickly.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Decision Intelligence API",
    description="AI-powered customer message triage",
    version="2.0.0"
)

# Enable CORS for browser testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "operational",
        "service": "Decision Intelligence API",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "api": "online"
    }

@app.post("/v1/decision")
def make_decision(request: dict):
    """
    Simplified decision endpoint.
    Returns a basic response for testing.
    """
    message = request.get("message", "")
    
    # Simple rule: check for legal keywords
    legal_keywords = ["lawsuit", "lawyer", "sue", "attorney"]
    if any(keyword in message.lower() for keyword in legal_keywords):
        return {
            "decision": "immediate_escalation",
            "priority": "critical",
            "churn_risk": 0.9,
            "confidence": 0.95,
            "recommended_action": "Escalate to legal team immediately"
        }
    
    # Default response
    return {
        "decision": "standard_response",
        "priority": "medium",
        "churn_risk": 0.2,
        "confidence": 0.75,
        "recommended_action": "Review and respond within 24 hours"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    # Create requirements.txt
    requirements = '''fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
google-generativeai==0.3.2
python-multipart==0.0.6
'''
    
    # Create .gitignore
    gitignore = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# API Keys
.env
*.key

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
'''
    
    # Create README
    readme = '''# Decision Intelligence API

## Quick Start

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the API:
   ```
   uvicorn main:app --reload
   ```

3. Open in browser:
   ```
   http://localhost:8000/docs
   ```

## Test Endpoints

### Health Check
```
GET http://localhost:8000/health
```

### Make Decision
```
POST http://localhost:8000/v1/decision
Content-Type: application/json

{
  "message": "I will sue you",
  "user_plan": "pro"
}
```

## Next Steps

- Add Gemini API key for AI features
- Check out the full documentation
- Test in browser using Swagger UI at /docs
'''
    
    # Create test script
    test_script = '''# Test the API
# Run this after starting the API with: uvicorn main:app --reload

import requests
import json

BASE_URL = "http://localhost:8000"

print("Testing Decision Intelligence API...")
print()

# Test 1: Health check
print("1. Health Check")
response = requests.get(f"{BASE_URL}/health")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")
print()

# Test 2: Simple decision
print("2. Simple Decision")
response = requests.post(
    f"{BASE_URL}/v1/decision",
    json={"message": "How do I reset my password?", "user_plan": "free"}
)
print(f"   Status: {response.status_code}")
print(f"   Decision: {response.json()['decision']}")
print(f"   Priority: {response.json()['priority']}")
print()

# Test 3: Legal threat
print("3. Legal Threat")
response = requests.post(
    f"{BASE_URL}/v1/decision",
    json={"message": "I will contact my lawyer", "user_plan": "pro"}
)
print(f"   Status: {response.status_code}")
print(f"   Decision: {response.json()['decision']}")
print(f"   Priority: {response.json()['priority']}")
print()

print("✓ All tests completed!")
'''
    
    # Create batch file to run API
    run_bat = '''@echo off
echo Starting Decision Intelligence API...
echo.
echo API will be available at: http://localhost:8000
echo Docs available at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn main:app --reload
'''
    
    # Create files
    print("Creating files...")
    print()
    
    success = True
    success &= create_file("main.py", main_py)
    success &= create_file("requirements.txt", requirements)
    success &= create_file(".gitignore", gitignore)
    success &= create_file("README.md", readme)
    success &= create_file("test_api.py", test_script)
    success &= create_file("run.bat", run_bat)
    
    print()
    
    if success:
        print("=" * 60)
        print("✓ Setup completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print()
        print("1. Install dependencies:")
        print("   pip install -r requirements.txt")
        print()
        print("2. Run the API:")
        print("   uvicorn main:app --reload")
        print("   OR double-click: run.bat")
        print()
        print("3. Open in browser:")
        print("   http://localhost:8000/docs")
        print()
        print("4. Test the API:")
        print("   python test_api.py")
        print()
    else:
        print("=" * 60)
        print("⚠️  Setup completed with errors")
        print("=" * 60)
        print()
        print("Please check the error messages above")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()