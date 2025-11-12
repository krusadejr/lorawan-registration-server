"""
Script to update sample device files with correct UUIDs
"""
import pandas as pd
import json

def update_excel_file(filepath, new_device_profile_id):
    """Update the device_profile_id in Excel file"""
    print(f"Reading {filepath}...")
    df = pd.read_excel(filepath)
    
    print(f"Current unique device_profile_ids: {df['device_profile_id'].unique()}")
    
    # Update all device_profile_id values
    df['device_profile_id'] = new_device_profile_id
    
    print(f"Updated all device_profile_ids to: {new_device_profile_id}")
    
    # Save back to Excel
    df.to_excel(filepath, index=False)
    print(f"✓ Saved {filepath}")
    print(f"Total devices updated: {len(df)}")


def update_txt_file(filepath, new_device_profile_id):
    """Update the device_profile_id in TXT file (JSON lines)"""
    print(f"\nReading {filepath}...")
    
    updated_lines = []
    with open(filepath, 'r') as f:
        for line in f:
            device = json.loads(line.strip())
            print(f"  Old device_profile_id: {device.get('device_profile_id')}")
            device['device_profile_id'] = new_device_profile_id
            updated_lines.append(json.dumps(device))
    
    # Write back
    with open(filepath, 'w') as f:
        for line in updated_lines:
            f.write(line + '\n')
    
    print(f"✓ Saved {filepath}")
    print(f"Total devices updated: {len(updated_lines)}")


def update_json_file(filepath, new_device_profile_id):
    """Update the device_profile_id in JSON file"""
    print(f"\nReading {filepath}...")
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    devices = data if isinstance(data, list) else data.get('devices', [])
    
    for device in devices:
        print(f"  Old device_profile_id: {device.get('device_profile_id')}")
        device['device_profile_id'] = new_device_profile_id
    
    # Write back
    with open(filepath, 'w') as f:
        if isinstance(data, list):
            json.dump(devices, f, indent=2)
        else:
            json.dump(data, f, indent=2)
    
    print(f"✓ Saved {filepath}")
    print(f"Total devices updated: {len(devices)}")


if __name__ == "__main__":
    print("="*80)
    print("UPDATE SAMPLE DATA WITH CORRECT DEVICE PROFILE UUID")
    print("="*80)
    
    # Get the new device profile ID from user
    print("\nPlease enter the correct Device Profile ID (UUID) from ChirpStack:")
    print("Example: a1b2c3d4-e5f6-4789-a012-3456789abcde")
    new_device_profile_id = input("Device Profile ID: ").strip()
    
    # Validate UUID format
    import re
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
    
    if not uuid_pattern.match(new_device_profile_id):
        print("\n❌ ERROR: Invalid UUID format!")
        print("Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        exit(1)
    
    print(f"\n✓ Valid UUID format")
    print(f"Will update all sample files with device_profile_id: {new_device_profile_id}")
    
    confirm = input("\nContinue? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Cancelled.")
        exit(0)
    
    print("\n" + "="*80)
    
    # Update all sample files
    try:
        update_excel_file('exampleDevicesAIGenerated/sample_devices.xlsx', new_device_profile_id)
        update_txt_file('exampleDevicesAIGenerated/sample_devices.txt', new_device_profile_id)
        update_json_file('exampleDevicesAIGenerated/sample_devices.json', new_device_profile_id)
        
        print("\n" + "="*80)
        print("✓ ALL FILES UPDATED SUCCESSFULLY!")
        print("="*80)
        print("\nYou can now upload these files to test registration.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
