#!/usr/bin/env python3
"""
Test script to verify Spleeter service connectivity
Run this to ensure the service is properly set up
"""

import requests
import sys

SPLEETER_SERVICE_URL = "http://localhost:5001"

def test_spleeter_service():
    """Test if Spleeter service is running and healthy"""
    print("=" * 60)
    print("TESTING SPLEETER SERVICE")
    print("=" * 60)
    
    try:
        print(f"\n1. Testing connection to {SPLEETER_SERVICE_URL}/health...")
        response = requests.get(f"{SPLEETER_SERVICE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("   ✓ Service is running!")
            print(f"   ✓ Status: {data['status']}")
            print(f"   ✓ Spleeter available: {data['spleeter_available']}")
            print(f"   ✓ Python version: {data['python_version']}")
            
            if not data['spleeter_available']:
                print("\n   ⚠ WARNING: Spleeter is not available!")
                print("   → Check that Spleeter is installed in the service environment")
                return False
            
            if not data['python_version'].startswith('3.8'):
                print(f"\n   ⚠ WARNING: Service is running on Python {data['python_version']}")
                print("   → Spleeter requires Python 3.8 for best compatibility")
            
            print("\n✓ All checks passed!")
            print("=" * 60)
            return True
        else:
            print(f"   ✗ Service returned status code {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ✗ Could not connect to service!")
        print(f"\n   → Make sure the Spleeter service is running:")
        print(f"      cd spleeter_service")
        print(f"      ./start.sh")
        print(f"\n   → Or manually start it:")
        print(f"      cd spleeter_service")
        print(f"      python3.8 app.py")
        print("=" * 60)
        return False
    
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_spleeter_service()
    sys.exit(0 if success else 1)
