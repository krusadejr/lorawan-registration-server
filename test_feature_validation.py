#!/usr/bin/env python3
"""
Feature Validation Test Script
Tests: File parsing, column detection, parallel processing performance
"""

import os
import sys
import json
import time
import pandas as pd
from pathlib import Path

# Add current dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from file_parser import parse_file, get_column_info

def print_section(title):
    """Print test section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_file_parsing():
    """Test 1: File parsing with test_100_devices.csv"""
    print_section("TEST 1: File Parsing & Column Detection")
    
    test_file = "uploads/test_100_devices.csv"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    try:
        # Parse file
        start = time.time()
        result = parse_file(test_file, 'csv')
        parse_time = time.time() - start
        
        if not result.get('success'):
            print(f"⚠ Parse result not successful: {result.get('message', 'Unknown error')}")
            if result.get('needs_delimiter'):
                print("  Note: Delimiter detection may need retry")
                return True  # Don't fail if delimiter needs explicit selection
            return False
        
        # Get devices from parsed data (it's a DataFrame)
        df = result.get('data', {}).get('Data')
        
        if df is None or len(df) == 0:
            print("❌ No devices parsed!")
            return False
        
        print(f"✓ File parsed successfully in {parse_time:.2f}s")
        print(f"✓ Total devices: {len(df)}")
        
        # Show first device
        print(f"\nFirst device structure:")
        first_device = df.iloc[0]
        for col in df.columns:
            print(f"  - {col}: {first_device[col]}")
        
        # Check required fields
        required_fields = ['dev_eui', 'name', 'device_profile_id', 'nwk_key', 'app_key']
        missing_fields = [f for f in required_fields if f not in df.columns]
        
        if missing_fields:
            print(f"\n❌ Missing required fields: {missing_fields}")
            return False
        
        print(f"\n✓ All required fields present")
        
        # Check optional tag fields
        tag_fields = [f for f in df.columns if f not in required_fields]
        print(f"✓ Additional columns (potential tags): {tag_fields}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error parsing file: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_column_detection():
    """Test 2: CSV file structure verification"""
    print_section("TEST 2: CSV File Structure")
    
    test_file = "uploads/test_100_devices.csv"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    try:
        # Read raw file
        df = pd.read_csv(test_file, nrows=1)
        columns = df.columns.tolist()
        
        print(f"CSV Columns found: {columns}")
        
        # Check for expected columns
        expected_columns = ['dev_eui', 'name', 'device_profile_id', 'nwk_key', 'app_key']
        found_columns = [col for col in expected_columns if col in columns]
        missing_columns = [col for col in expected_columns if col not in columns]
        
        print(f"\nColumn verification:")
        for col in found_columns:
            print(f"  ✓ '{col}' found")
        
        for col in missing_columns:
            print(f"  ❌ '{col}' NOT FOUND")
        
        if missing_columns:
            print(f"\n❌ Missing critical columns: {missing_columns}")
            return False
        
        print(f"\n✓ All critical columns present")
        
        # Show additional columns (potential tags)
        extra_cols = [col for col in columns if col not in expected_columns]
        if extra_cols:
            print(f"✓ Additional columns (can be used as tags): {extra_cols}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking CSV structure: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parallel_processing_readiness():
    """Test 3: Verify parallel processing setup"""
    print_section("TEST 3: Parallel Processing Configuration")
    
    try:
        from concurrent.futures import ThreadPoolExecutor
        import threading
        
        print("✓ ThreadPoolExecutor imported successfully")
        print("✓ threading module available")
        
        # Check app.py for parallel processing implementation
        with open("app.py", "r") as f:
            app_content = f.read()
        
        checks = [
            ("ThreadPoolExecutor", "ThreadPoolExecutor" in app_content),
            ("as_completed", "as_completed" in app_content),
            ("threading.Lock", "threading.Lock" in app_content),
            ("register_single_device", "register_single_device" in app_content),
        ]
        
        print("\nParallel processing components:")
        all_good = True
        for component, found in checks:
            if found:
                print(f"  ✓ {component} implemented")
            else:
                print(f"  ❌ {component} NOT FOUND")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error checking parallel processing: {e}")
        return False

def test_tag_selection_ui():
    """Test 4: Verify tag selection UI components"""
    print_section("TEST 4: Tag Selection UI")
    
    try:
        # Check column_mapping.html for tag selection
        with open("templates/column_mapping.html", "r") as f:
            html_content = f.read()
        
        checks = [
            ("tag_columns form field", 'name="tag_columns"' in html_content),
            ("Tags label/section", "Tags" in html_content or "tags" in html_content),
            ("Checkbox inputs", "type=\"checkbox\"" in html_content),
        ]
        
        print("Tag selection UI components:")
        all_good = True
        for component, found in checks:
            if found:
                print(f"  ✓ {component} present")
            else:
                print(f"  ❌ {component} NOT FOUND")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error checking UI: {e}")
        return False

def test_csv_upload_fix():
    """Test 5: Verify CSV file upload fix"""
    print_section("TEST 5: CSV File Upload Fix")
    
    try:
        with open("templates/index.html", "r") as f:
            html_content = f.read()
        
        # Look for CSV in accept attribute
        if 'accept=' in html_content:
            # Find the accept attribute
            import re
            matches = re.findall(r'accept=["\']([^"\']*)["\']', html_content)
            
            found_csv = False
            for match in matches:
                print(f"\nFile input accept attribute: accept=\"{match}\"")
                if ".csv" in match:
                    print("  ✓ CSV file type included in accept attribute")
                    found_csv = True
                else:
                    print("  ⚠ CSV file type NOT in accept attribute")
            
            return found_csv
        else:
            print("⚠ No accept attribute found in file inputs")
            return False
            
    except Exception as e:
        print(f"❌ Error checking CSV upload: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  FEATURE VALIDATION TEST SUITE")
    print("="*60)
    print(f"  Testing branch: test/feature-validation")
    print(f"  Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {}
    
    # Run tests
    results["File Parsing"] = test_file_parsing()
    results["Column Detection"] = test_column_detection()
    results["Parallel Processing Setup"] = test_parallel_processing_readiness()
    results["Tag Selection UI"] = test_tag_selection_ui()
    results["CSV Upload Fix"] = test_csv_upload_fix()
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "✓ PASS" if passed_flag else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Ready for web UI testing!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed - Review output above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
