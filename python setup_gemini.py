#!/usr/bin/env python3
"""
Gemini API Key Setup Helper - FIXED VERSION
Run this to set up your Gemini API key correctly
"""

import os
import sys

def check_env_file():
    """Check if .env file exists and has API key."""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            content = f.read()
            if 'GOOGLE_API_KEY=' in content and 'your_gemini_api_key_here' not in content:
                # Extract key
                for line in content.split('\n'):
                    if line.startswith('GOOGLE_API_KEY='):
                        key = line.split('=', 1)[1].strip()
                        if key and not key.startswith('your_'):
                            return True, key[:10] + '...'
        return False, None
    return False, None

def check_env_variable():
    """Check if environment variable is set."""
    key = os.getenv('GOOGLE_API_KEY')
    if key and not key.startswith('your_'):
        return True, key[:10] + '...'
    return False, None

def create_env_file(api_key):
    """Create or update .env file with API key."""
    content = f"""# Google Gemini API Configuration
# Get your API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY={api_key}

# Optional: Application Settings
# LOG_LEVEL=INFO
# API_PORT=8000
# API_HOST=0.0.0.0
"""
    
    with open('.env', 'w') as f:
        f.write(content)
    
    print("✅ Created .env file with your API key")

def test_api_key(api_key):
    """Test if the API key works - FIXED VERSION."""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        
        # FIXED: Use correct model name format
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        # Simple test
        response = model.generate_content("Say 'API key works!'")
        
        if response and response.text:
            return True
        return False
    except ImportError:
        print("⚠️  google-generativeai not installed")
        print("   Run: pip install google-generativeai")
        return None
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        return False

def list_available_models(api_key):
    """List all available Gemini models."""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        
        print("\n📋 Available Gemini models:")
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"   ✓ {model.name}")
        print()
        
    except Exception as e:
        print(f"   Could not list models: {e}")

def main():
    print("=" * 60)
    print("Gemini API Key Setup Helper - FIXED VERSION")
    print("=" * 60)
    print()
    
    # Check current status
    print("🔍 Checking current setup...")
    print()
    
    env_file_ok, env_file_key = check_env_file()
    env_var_ok, env_var_key = check_env_variable()
    
    if env_file_ok:
        print(f"✅ .env file has API key: {env_file_key}")
    else:
        print("❌ .env file missing or has placeholder key")
    
    if env_var_ok:
        print(f"✅ Environment variable set: {env_var_key}")
    else:
        print("❌ GOOGLE_API_KEY environment variable not set")
    
    print()
    
    # If no key is set, guide user
    if not env_file_ok and not env_var_ok:
        print("📝 Let's set up your API key!")
        print()
        print("1. Get your API key:")
        print("   https://makersuite.google.com/app/apikey")
        print()
        print("2. Enter your API key below:")
        print("   (It should look like: AIzaSyD...)")
        print()
        
        api_key = input("Paste your API key here: ").strip()
        
        if not api_key:
            print("❌ No API key provided")
            return
        
        if api_key.startswith('your_') or len(api_key) < 20:
            print("❌ That doesn't look like a valid API key")
            print("   Valid keys start with 'AIza' and are ~40 characters")
            return
        
        # Create .env file
        create_env_file(api_key)
        
        # Test the key
        print()
        print("🧪 Testing API key...")
        result = test_api_key(api_key)
        
        if result is True:
            print("✅ API key works perfectly!")
            list_available_models(api_key)
        elif result is False:
            print("❌ API key test failed - check if the key is correct")
        else:
            print("⚠️  Could not test (install google-generativeai first)")
        
        print()
        print("=" * 60)
        print("✨ Setup complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start the API: uvicorn main:app --reload")
        print("3. Open test.html in your browser")
        
    else:
        print("✅ API key is already configured!")
        print()
        
        # Determine which key to test
        test_key = None
        if env_var_ok:
            test_key = os.getenv('GOOGLE_API_KEY')
            print("Using environment variable")
        elif env_file_ok:
            # Load from .env
            with open('.env', 'r') as f:
                for line in f.read().split('\n'):
                    if line.startswith('GOOGLE_API_KEY='):
                        test_key = line.split('=', 1)[1].strip()
                        break
            print("Using .env file")
        
        if test_key:
            print()
            print("🧪 Testing API key with FIXED model name...")
            result = test_api_key(test_key)
            
            if result is True:
                print("✅ API key works perfectly!")
                list_available_models(test_key)
            elif result is False:
                print("❌ API key test failed")
                print()
                print("To update your key:")
                print("1. Edit .env file")
                print("2. Replace GOOGLE_API_KEY value with new key")
                print("3. Restart the API")
            else:
                print("⚠️  Install dependencies to test:")
                print("   pip install google-generativeai")
        
        print()
        print("You're ready to go! Start the API with:")
        print("uvicorn main:app --reload")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")