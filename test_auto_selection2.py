import pandas as pd

filepath = r'PRIVATE\2026-02-20 Test Devices\Feuchtesensoren LoRa 2025-SO-52960 keys.csv'
df = pd.read_csv(filepath, delimiter=';', encoding='utf-8')

columns = list(df.columns)

print("=== Updated Application Key Auto-Selection Logic ===\n")

print("Pattern: col.lower() in ['app_key', 'appkey', 'application_key', 'applicationkey'] OR")
print("         'otaa' in col_lower OR")
print("         'lora_appkey' in col_lower OR")
print("         ('app' in col_lower AND 'key' in col_lower AND 'skey' not in col_lower AND 'session' not in col_lower)")
print()

for col in columns:
    col_lower = col.lower()
    matches = (col_lower in ['app_key', 'appkey', 'application_key', 'applicationkey'] or 
               'otaa' in col_lower or 
               'lora_appkey' in col_lower or 
               ('app' in col_lower and 'key' in col_lower and 'skey' not in col_lower and 'session' not in col_lower))
    if 'app' in col_lower or 'otaa' in col_lower or 'key' in col_lower:
        status = "✅ AUTO-SELECT" if matches else "❌ No"
        print(f"  {col:30} → {status}")

print("\n\n=== Summary ===")
print("Expected behavior with this CSV:")
print("  MUST auto-select 'OTAA keys' for app_key ✓")
print("  SHOULD auto-select 'lora_appkey11' for app_key ✓")
print("  SHOULD NOT auto-select 'lora_appskey' for app_key (Session Key)")
print("  SHOULD NOT auto-select 'lora_nwkskey' for nwk_key (Session Key)")
