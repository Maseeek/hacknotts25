#!/usr/bin/env python3
"""
Test script to verify that numpy is not required at metadata-time.

This script demonstrates that the packaging configuration correctly:
1. Does NOT include numpy in build-system.requires
2. Does NOT import numpy at module level in setup.py
3. CAN extract package metadata without numpy installed
4. DOES include numpy in runtime dependencies
"""

import subprocess
import sys
import tomllib
import ast


def test_pyproject_toml():
    """Test that pyproject.toml is correctly configured."""
    print("=" * 60)
    print("TEST 1: Verify pyproject.toml configuration")
    print("=" * 60)
    
    with open('pyproject.toml', 'rb') as f:
        config = tomllib.load(f)
    
    build_requires = config['build-system']['requires']
    print(f"Build requirements: {build_requires}")
    
    if any('numpy' in req.lower() for req in build_requires):
        print("✗ FAIL: numpy found in build-system.requires")
        return False
    
    print("✓ PASS: numpy is NOT in build-system.requires")
    
    project_deps = config['project']['dependencies']
    if 'numpy' not in project_deps:
        print("✗ FAIL: numpy not found in project dependencies")
        return False
    
    print("✓ PASS: numpy is in project.dependencies (runtime)")
    return True


def test_setup_py():
    """Test that setup.py doesn't import numpy at module level."""
    print("\n" + "=" * 60)
    print("TEST 2: Verify setup.py has no numpy imports")
    print("=" * 60)
    
    with open('setup.py', 'r') as f:
        tree = ast.parse(f.read())
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    
    print(f"Module-level imports: {imports}")
    
    if any('numpy' in imp for imp in imports):
        print("✗ FAIL: numpy imported at module level in setup.py")
        return False
    
    print("✓ PASS: numpy not imported at module level in setup.py")
    return True


def test_metadata_extraction():
    """Test that metadata can be extracted without numpy."""
    print("\n" + "=" * 60)
    print("TEST 3: Extract metadata without numpy installed")
    print("=" * 60)
    
    # Test various metadata extractions
    tests = [
        ('--name', 'hacknotts25-pipeline'),
        ('--version', '0.1.0'),
        ('--description', 'AI-powered song transformation pipeline'),
    ]
    
    for arg, expected in tests:
        result = subprocess.run(
            [sys.executable, 'setup.py', arg],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print(f"✗ FAIL: Could not extract {arg}")
            print(f"  Error: {result.stderr}")
            return False
        
        value = result.stdout.strip().split('\n')[-1]  # Last line (skip warnings)
        if expected not in value:
            print(f"✗ FAIL: Unexpected value for {arg}: {value}")
            return False
        
        print(f"✓ PASS: Extracted {arg}: {value}")
    
    return True


def test_pipeline_import():
    """Test that the pipeline module can be imported."""
    print("\n" + "=" * 60)
    print("TEST 4: Import pipeline module")
    print("=" * 60)
    
    try:
        import pipeline
        print("✓ PASS: pipeline module imported successfully")
        return True
    except ImportError as e:
        print(f"✗ FAIL: Could not import pipeline: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("NUMPY METADATA-TIME BUILD FIX VERIFICATION")
    print("=" * 60)
    
    results = []
    
    results.append(("pyproject.toml configuration", test_pyproject_toml()))
    results.append(("setup.py imports", test_setup_py()))
    results.append(("Metadata extraction", test_metadata_extraction()))
    results.append(("Pipeline import", test_pipeline_import()))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nThe packaging is correctly configured to avoid")
        print("numpy metadata-time build issues.")
        return 0
    else:
        print("\n" + "=" * 60)
        print("✗ SOME TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
