#!/usr/bin/env python3
"""
Test script to verify URL parsing with various escaped formats.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.helpers import extract_video_id

def test_url_parsing():
    """Test URL parsing with various formats including escaped characters."""
    
    test_cases = [
        # Regular URLs
        ("https://www.youtube.com/watch?v=GfH4QL4VqJ0", "GfH4QL4VqJ0"),
        ("https://youtu.be/GfH4QL4VqJ0", "GfH4QL4VqJ0"),
        
        # Escaped URLs (like from shell)
        ("https://www.youtube.com/watch\\?v\\=GfH4QL4VqJ0", "GfH4QL4VqJ0"),
        ("https://youtu.be/GfH4QL4VqJ0\\?t\\=123", "GfH4QL4VqJ0"),
        
        # Edge cases
        ("GfH4QL4VqJ0", "GfH4QL4VqJ0"),  # Just video ID
        ("invalid-url", None),  # Invalid input
        ("", None),  # Empty string
    ]
    
    print("Testing URL parsing with escaped characters:")
    print("=" * 60)
    
    all_passed = True
    for test_input, expected in test_cases:
        result = extract_video_id(test_input)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        if result != expected:
            all_passed = False
            
        print(f"{status} Input: {test_input!r}")
        print(f"      Expected: {expected}")
        print(f"      Got:      {result}")
        print()
    
    print("=" * 60)
    if all_passed:
        print("🎉 All tests PASSED! URL parsing handles escaped characters correctly.")
    else:
        print("❌ Some tests FAILED!")
    
    return all_passed

if __name__ == "__main__":
    test_url_parsing()
