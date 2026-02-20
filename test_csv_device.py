import pandas as pd
import numpy as np

filepath = r'PRIVATE\2026-02-20 Test Devices\Feuchtesensoren LoRa 2025-SO-52960 keys.csv'
df = pd.read_csv(filepath, delimiter=';', encoding='utf-8')

# Get device A84041F4935D6EEA
device_eui = 'A84041F4935D6EEA'
rows = df[df['lora_deveui'] == device_eui]

if len(rows) == 0:
    print(f"Device {device_eui} not found with exact match")
    # Try case-insensitive
    rows = df[df['lora_deveui'].str.upper() == device_eui]
    print(f"Found with upper(): {len(rows)} rows")

if len(rows) > 0:
    row = rows.iloc[0]
    print(f"Device: {row['lora_deveui']}")
    print(f"\n=== Key Columns ===")
    print(f"lora_appeui: {row['lora_appeui']}")
    print(f"OTAA keys: {row['OTAA keys']} (type: {type(row['OTAA keys']).__name__}, NaN: {pd.isna(row['OTAA keys'])})")
    print(f"lora_appkey11: {row['lora_appkey11']} (NaN: {pd.isna(row['lora_appkey11'])})")
    print(f"lora_devaddr: {row['lora_devaddr']} (type: {type(row['lora_devaddr']).__name__})")
    print(f"lora_appskey: {row['lora_appskey']}")
    print(f"lora_nwkskey: {row['lora_nwkskey']}")
    
    # Get column content as dataframe slice
    print(f"\n=== All columns 15-21 ===")
    for i in range(15, 22):
        col_name = df.columns[i]
        col_value = row[col_name]
        print(f"  {i} ({col_name}): {col_value} (type: {type(col_value).__name__}, NaN: {pd.isna(col_value)})")
else:
    print(f"Device {device_eui} not found")
    # Show first device to check format
    print("\nFirst device:")
    row = df.iloc[0]
    print(f"  lora_deveui: {row['lora_deveui']}")
    print(f"  lora_appkey11: {row['lora_appkey11']}")
    print(f"  lora_nwkskey: {row['lora_nwkskey']}")
