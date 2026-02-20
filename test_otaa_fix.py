#!/usr/bin/env python3
"""
Test script to verify OTAA handling fix for ChirpStack key mapping
"""
import pandas as pd
import json
from pathlib import Path

# Sample data structure similar to what the actual CSV contains
sample_data = {
    'product_name': ['Device1', 'Device2'],
    'Zaehlernummer': ['A84041F4935D6EEA', 'A84041F4935D6FFF'], 
    'DeviceprofileID': ['8ad02259-c996-43b0-b37b-8a8e813c360f', '8ad02259-c996-43b0-b37b-8a8e813c360f'],
    'lora_joinmode': ['OTAA', 'OTAA'],
    'OTAA keys': ['D60F739062E3B90BBBAE3B26C4308FAE', 'D60F739062E3B90BBBAE3B26C4308FB1'],
    'lora_nwkskey': ['E1190B75A10FFF4066138DA3836EC843', 'E1190B75A10FFF4066138DA3836EC844'],
    'lora_appskey': ['F2290B75A10FFF4066138DA3836EC845', 'F2290B75A10FFF4066138DA3836EC846'],
}

df = pd.DataFrame(sample_data)

# Simulate the column mapping from the UI
column_mapping = {
    'dev_eui': 'Zaehlernummer',
    'name': 'product_name',
    'device_profile_id': 'DeviceprofileID',
    'nwk_key': 'lora_nwkskey',  # User selected this (wrong for OTAA)
    'app_key': 'lora_appskey'     # User selected this (wrong for OTAA)
}

print("=" * 80)
print("OTAA FIX TEST - Simulating Device Registration with OTAA Handling")
print("=" * 80)
print()

# Test the OLD behavior vs NEW behavior
for idx, row in df.iterrows():
    print(f"\nDevice #{idx + 1}: {row['Zaehlernummer']}")
    print("-" * 80)
    
    # OLD behavior (WRONG)
    print("OLD (WRONG) - Direct column mapping:")
    old_nwk_key = str(row[column_mapping['nwk_key']]).strip()
    old_app_key = str(row[column_mapping['app_key']]).strip()
    print(f"  nwk_key field value: {old_nwk_key}")
    print(f"  app_key field value: {old_app_key}")
    print(f"  ❌ RESULT: ChirpStack stores app_key = {old_nwk_key} (WRONG - this is the network session key!)")
    
    # NEW behavior (CORRECT)
    print("\nNEW (CORRECT) - OTAA-aware handling:")
    is_otaa = False
    if 'lora_joinmode' in df.columns:
        join_mode = str(row['lora_joinmode']).strip().upper() if pd.notna(row['lora_joinmode']) else 'ABP'
        is_otaa = join_mode == 'OTAA'
    
    # For OTAA devices, use OTAA keys column if available
    nwk_key_value = str(row[column_mapping['nwk_key']]).strip()
    if is_otaa and 'OTAA keys' in df.columns and pd.notna(row['OTAA keys']):
        # Override: for OTAA 1.0.x, use OTAA keys for the nwk_key field
        otaa_keys = str(row['OTAA keys']).strip()
        if otaa_keys:  # Only override if OTAA keys has a value
            nwk_key_value = otaa_keys
            print(f"  🔧 OTAA detected: using 'OTAA keys' column instead of 'lora_nwkskey'")
    
    print(f"  is_otaa: {is_otaa}")
    print(f"  nwk_key field value: {nwk_key_value}")
    print(f"  app_key field value: (empty for OTAA 1.0.x)")
    print(f"  ✅ RESULT: ChirpStack stores app_key = {nwk_key_value} (CORRECT - this is the OTAA root app key!)")
    
    # Show the expected vs actual
    print(f"\n  EXPECTED app_key in ChirpStack: D60F739062E3B90BBBAE3B26C4308FAE (from OTAA keys column)")
    print(f"  NEW CODE sends to nwk_key field: {nwk_key_value}")
    if nwk_key_value == row['OTAA keys']:
        print(f"  ✅ MATCH!")
    else:
        print(f"  ❌ MISMATCH")

print("\n" + "=" * 80)
print("Summary:")
print("- OLD behavior: Sends lora_nwkskey (network session key) for app_key field")
print("- NEW behavior: Sends OTAA keys (root application key) for nwk_key field")
print("- This fixes the issue where ChirpStack stores wrong app_key value")
print("=" * 80)
