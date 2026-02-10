#!/usr/bin/env python3
"""
Test Data Generator for Performance Testing
Generates CSV files with sample LoRaWAN devices for testing registration speed
"""

import pandas as pd
import uuid
import random
import sys
from pathlib import Path

def generate_test_devices(count=100, filename=None):
    """
    Generate test device CSV file
    
    Args:
        count: Number of devices to generate
        filename: Output filename (default: test_{count}_devices.csv)
    
    Returns:
        path to generated file
    """
    
    if filename is None:
        filename = f"test_{count}_devices.csv"
    
    # Sample device types and locations
    device_types = [
        "Temperature Sensor",
        "Humidity Sensor",
        "Water Meter (Elvaco)",
        "Gas Meter",
        "Energy Meter",
        "Pressure Sensor",
        "GPS Tracker",
        "Motion Detector"
    ]
    
    locations = [
        "Building A - Floor 1",
        "Building A - Floor 2",
        "Building B - Ground Floor",
        "Building B - 1st Floor",
        "Outdoor Area 1",
        "Outdoor Area 2",
        "Warehouse",
        "Laboratory"
    ]
    
    # Generate data
    data = {
        'dev_eui': [f'{i:016X}' for i in range(0x0004A30B001A2B3C, 0x0004A30B001A2B3C + count)],
        'name': [f'Device_{i:05d}' for i in range(count)],
        'application_id': [str(uuid.uuid4())] * count,
        'device_profile_id': [str(uuid.uuid4())] * count,
        'nwk_key': [f'{random.randint(0, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF):032X}' for _ in range(count)],
        'app_key': [f'{random.randint(0, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF):032X}' for _ in range(count)],
        'Typ': [random.choice(device_types) for _ in range(count)],
        'Standort': [random.choice(locations) for _ in range(count)],
        'SerialNo': [f'SN-{random.randint(100000, 999999):06d}' for _ in range(count)],
        'Status': ['Aktiv'] * count
    }
    
    df = pd.DataFrame(data)
    
    # Ensure uploads directory exists
    uploads_dir = Path('uploads')
    uploads_dir.mkdir(exist_ok=True)
    
    # Save to file
    filepath = uploads_dir / filename
    df.to_csv(filepath, index=False)
    
    print(f"✓ Generated test file: {filepath}")
    print(f"  - Total devices: {count}")
    print(f"  - File size: {filepath.stat().st_size / 1024:.1f} KB")
    print(f"  - Columns: {', '.join(df.columns)}")
    
    return str(filepath)


def main():
    """Generate multiple test files"""
    
    print("=" * 60)
    print("LoRaWAN Test Data Generator")
    print("=" * 60)
    
    # Generate test files
    test_configs = [
        (10, "test_10_devices.csv"),
        (100, "test_100_devices.csv"),
        (330, "test_330_devices.csv"),
        (1000, "test_1000_devices.csv"),
    ]
    
    generated_files = []
    
    for count, filename in test_configs:
        try:
            filepath = generate_test_devices(count, filename)
            generated_files.append((count, filepath))
            print()
        except Exception as e:
            print(f"✗ Error generating {count} devices: {e}")
            print()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Generated {len(generated_files)} test files:\n")
    
    for count, filepath in generated_files:
        print(f"  {count:,} devices → {filepath}")
    
    print("\n" + "=" * 60)
    print("Performance Testing Recommendations")
    print("=" * 60)
    print("""
  10 devices:     Quick smoke test (no performance benefit visible)
  100 devices:    Notice 2-3x speed improvement
  330 devices:    Real manufacturer data volume test
  1000 devices:   Stress test (should complete in <10 min with parallel)
    
  Usage:
  1. Upload any of these files via the web UI
  2. Map columns (Typ, Standort, SerialNo as tags)
  3. Time the registration process
  4. Compare against expected baseline:
     - Sequential: ~3-5 sec per device
     - Parallel:   ~1-2 sec per device (2-3x faster)
    """)


if __name__ == '__main__':
    # If run with argument, generate specific count
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
            filename = sys.argv[2] if len(sys.argv) > 2 else None
            filepath = generate_test_devices(count, filename)
            print(f"\n✓ Test file ready: {filepath}")
        except ValueError:
            print(f"Error: First argument must be a number (device count)")
            sys.exit(1)
    else:
        main()
