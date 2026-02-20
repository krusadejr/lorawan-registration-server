import pandas as pd

filepath = r'PRIVATE\2026-02-20 Test Devices\Feuchtesensoren LoRa 2025-SO-52960 keys.csv'
df = pd.read_csv(filepath, delimiter=';', encoding='utf-8')

columns = list(df.columns)

print("=== Testing Auto-Selection Logic ===\n")

# Test nwk_key auto-selection
print("Network Key (nwk_key) auto-selection:")
print("Pattern: col.lower() in ['nwk_key', 'nwkkey', 'network_key', 'networkkey'] OR")
print("         ('nwk' in col_lower AND 'key' in col_lower AND 'skey' not in col_lower)")
for col in columns:
    col_lower = col.lower()
    matches = (col_lower in ['nwk_key', 'nwkkey', 'network_key', 'networkkey'] or 
               ('nwk' in col_lower and 'key' in col_lower and 'skey' not in col_lower))
    if matches or 'nwk' in col_lower:
        print(f"  {col:30} → auto-select: {matches}")

print("\n\nApplication Key (app_key) auto-selection:")
print("Pattern: col.lower() in ['app_key', 'appkey', 'application_key', 'applicationkey'] OR")
print("         'otaa' in col_lower OR")
print("         ('app' in col_lower AND 'key' in col_lower) OR")
print("         'lora_appkey' in col_lower")
for col in columns:
    col_lower = col.lower()
    matches = (col_lower in ['app_key', 'appkey', 'application_key', 'applicationkey'] or 
               'otaa' in col_lower or 
               ('app' in col_lower and 'key' in col_lower) or 
               'lora_appkey' in col_lower)
    if matches or 'app' in col_lower or 'otaa' in col_lower:
        print(f"  {col:30} → auto-select: {matches}")

# Test validation logic
print("\n\n=== Testing Validation Logic ===\n")
test_cases = [
    ('lora_nwkskey', 'OTAA keys', 'Network Session Key selected - SHOULD WARN'),
    ('lora_nwkskey', '', 'Network Session Key selected, no app_key - SHOULD WARN'),
    ('', 'OTAA keys', 'No nwk_key selected, app_key selected - SHOULD WARN ABOUT MISSING NWK'),
    ('lora_nwkskey', 'lora_nwkskey', 'Same column for both keys - SHOULD WARN'),
]

for nwk_col, app_col, description in test_cases:
    print(f"\nTest: {description}")
    print(f"  nwk_key: {nwk_col or 'NOT SELECTED'}")
    print(f"  app_key: {app_col or 'NOT SELECTED'}")
    
    nwk_lower = nwk_col.lower() if nwk_col else ''
    app_lower = app_col.lower() if app_col else ''
    
    # Check for Session key warning
    if 'nwkskey' in nwk_lower or 'appskey' in nwk_lower:
        print(f"  ⚠️  WARNING: Session key detected in nwk_key!")
    
    # Check for missing app_key warning
    if not app_lower:
        print(f"  ℹ️  INFO: No app_key selected (is this intentional?)")
        
    # Check for same column warning
    if app_lower and nwk_lower == app_lower:
        print(f"  ⚠️  WARNING: Both keys selected from same column!")
