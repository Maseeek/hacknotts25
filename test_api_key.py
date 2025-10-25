#!/usr/bin/env python3
"""
Test script to verify Gemini API key loading and connectivity
"""

import os
import sys
from dotenv import load_dotenv

def test_env_loading():
    """Test if .env file is loaded correctly"""
    print("="*60)
    print("TEST 1: Environment Variable Loading")
    print("="*60)
    
    # Load .env file
    load_dotenv()
    
    # Check if API key is loaded
    api_key = os.environ.get('GEMINI_API_KEY')
    
    if not api_key:
        print("✗ FAILED: GEMINI_API_KEY not found in environment")
        print("  Make sure you have a .env file with GEMINI_API_KEY=your-key-here")
        return False
    
    if api_key == "put-key-here":
        print("⚠ WARNING: GEMINI_API_KEY is set to placeholder value 'put-key-here'")
        print("  Please update your .env file with a real API key")
        return False
    
    # Store length for display (avoid accessing api_key in print statements)
    key_length = len(api_key)
    
    # Mask the API key for security (show only first and last 4 characters)
    if key_length > 8:
        masked_key = f"{api_key[:4]}...{api_key[-4:]}"
    else:
        masked_key = "***"
    
    print(f"✓ SUCCESS: GEMINI_API_KEY loaded from .env file")
    print(f"  Key: {masked_key}")
    print(f"  Length: {key_length} characters")
    return True


def test_api_connectivity():
    """Test if the Gemini API key works by making a simple API call"""
    print("\n" + "="*60)
    print("TEST 2: Gemini API Connectivity")
    print("="*60)
    
    # Load .env file
    load_dotenv()
    api_key = os.environ.get('GEMINI_API_KEY')
    
    if not api_key or api_key == "put-key-here":
        print("⚠ SKIPPED: Cannot test API connectivity without a valid API key")
        return None
    
    try:
        import google.generativeai as genai
        
        print("  → Configuring Gemini API...")
        genai.configure(api_key=api_key)
        
        print("  → Creating model instance...")
        model = genai.GenerativeModel('gemini-pro')
        
        print("  → Testing with a simple prompt...")
        response = model.generate_content("Say 'Hello, the API key is working!' in one sentence.")
        
        if response and hasattr(response, 'text') and response.text:
            print("✓ SUCCESS: Gemini API is working correctly!")
            print(f"  Response: {response.text[:100]}...")
            return True
        else:
            print("✗ FAILED: API call succeeded but response was empty or invalid")
            return False
            
    except ImportError:
        print("⚠ SKIPPED: google-generativeai package not installed")
        print("  Install it with: pip install google-generativeai")
        return None
    except Exception as e:
        print(f"✗ FAILED: Error connecting to Gemini API")
        print(f"  Error: {str(e)}")
        print("\n  Common issues:")
        print("  - Invalid API key")
        print("  - Network connectivity problems")
        print("  - API quota exceeded")
        print("  - API key doesn't have proper permissions")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("GEMINI API KEY TEST SUITE")
    print("="*60)
    print()
    
    results = []
    
    # Test 1: Environment loading
    env_loaded = test_env_loading()
    results.append(("Environment Loading", env_loaded))
    
    # Test 2: API connectivity (only if env loaded successfully)
    if env_loaded:
        api_works = test_api_connectivity()
        if api_works is not None:
            results.append(("API Connectivity", api_works))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("="*60)
    
    # Return exit code
    if all(r for _, r in results):
        print("\n✓ All tests passed! Your Gemini API key is properly configured.")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
