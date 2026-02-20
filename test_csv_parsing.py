import pandas as pd

filepath = r'PRIVATE\2026-02-20 Test Devices\Feuchtesensoren LoRa 2025-SO-52960 keys.csv'

# Test with semicolon delimiter
df_semi = pd.read_csv(filepath, delimiter=';', encoding='utf-8')
print('=== CSV Parsing Test ===')
print(f'Columns: {len(df_semi.columns)}')
print(f'Rows: {len(df_semi)}')

# Check columns
cols = list(df_semi.columns)
print(f'\nFirst 15 column names:')
for i, col in enumerate(cols[:15]):
    print(f'  {i}: {col}')

print(f'\nLast 15 column names:')
for i, col in enumerate(cols[-15:], start=len(cols)-15):
    print(f'  {i}: {col}')

# Check the specific columns we need
has_appkey11 = 'lora_appkey11' in cols
has_nwkskey = 'lora_nwkskey' in cols
print(f'\nlora_appkey11 present: {has_appkey11}')
print(f'lora_nwkskey present: {has_nwkskey}')

# Get first device
print('\n=== First Device ===')
row = df_semi.iloc[0]
print(f'DevEUI: {row["lora_deveui"]}')
print(f'AppKey11: {row["lora_appkey11"]}')
print(f'NwkSKey: {row["lora_nwkskey"]}')

# Get device A84041F4935D6EEA (from the screenshot)
print('\n=== Device A84041F4935D6EEA ===')
matching_rows = df_semi[df_semi['lora_deveui'] == 'A84041F4935D6EEA']
if len(matching_rows) > 0:
    row = matching_rows.iloc[0]
    print(f'DevEUI: {row["lora_deveui"]}')
    print(f'Name: {row["product_name"]}')
    print(f'AppKey11 (should be used as app_key): {row["lora_appkey11"]}')
    print(f'NwkSKey (network session key): {row["lora_nwkskey"]}')
else:
    print('Device not found')
    # Try case-insensitive
    matching_rows = df_semi[df_semi['lora_deveui'].str.upper() == 'A84041F4935D6EEA']
    if len(matching_rows) > 0:
        print('Found with case-insensitive search')
        row = matching_rows.iloc[0]
        print(f'DevEUI: {row["lora_deveui"]}')
        print(f'AppKey11: {row["lora_appkey11"]}')
        print(f'NwkSKey: {row["lora_nwkskey"]}')
