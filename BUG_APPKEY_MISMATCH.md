# Bug Analysis: Wrong Application Key Being Used

## Issue Description
When users upload a CSV file with LoRaWAN device keys, the application key value that ends up in ChirpStack is incorrect. Instead of the actual application key, a different key (network session key) appears.

**User Report:** "die Applikation Key wird nicht übernommen und es steht ein andere Key drin"
(Translation: "The application key is not being adopted and a different key is there instead")

## Root Cause Analysis

### CSV File Structure Issue
The CSV file `Feuchtesensoren LoRa 2025-SO-52960 keys.csv` has a **misaligned column structure**:

**Header Line:**
- Column 17: `OTAA keys`
- Column 18: `lora_appkey11`
- Column 19: `lora_devaddr`
- Column 20: `lora_appskey`
- Column 21: `lora_nwkskey`

**Actual Data for Device A84041F4935D6EEA:**
- Column 17 (OTAA keys): `393F8A7954AAC6584ACC9CCE66FBB532` ← **ACTUAL APPLICATION KEY IS HERE**
- Column 18 (lora_appkey11): `NaN` (empty) ← **Should be here but is empty!**
- Column 20 (lora_appskey): `00ED62A7ADF862D5C2F9CC2E588FD04D`
- Column 21 (lora_nwkskey): `E1190B75A10FFF4066138DA3836EC843` ← This is showing up in ChirpStack instead

### Column Auto-Detection Problem

In `templates/column_mapping.html`, the form auto-selects columns based on case-insensitive name matching:

```html
<!-- For app_key field -->
{% if col.lower() in ['app_key', 'appkey', 'application_key', 'applicationkey'] %}selected{% endif %}

<!-- For nwk_key field -->  
{% if col.lower() in ['nwk_key', 'nwkkey', 'network_key', 'networkkey'] %}selected{% endif %}
```

**Problem:** Neither `'otaa keys'` nor `'lora_appkey11'` match the auto-detection patterns, so:
- `app_key` field shows as NOT SELECTED
- User must manually select a column
- User confusion: They might select the wrong column or not realize `lora_appkey11` is empty
- If they select `lora_nwkskey` by mistake, the network session key becomes the application key

## Impact
- Devices register with wrong Application Key  
- Devices may fail to communicate with gateway
- ChirpStack Device configuration shows unexpected key values

## Solution Strategy

### Immediate Fix: Improve Column Detection
1. Expand auto-detection patterns to include variations like:
   - 'otaa' - matches 'OTAA keys'
   - 'app.*key' - matches 'lora_appkey11', 'app_key', etc.
   - 'nwk.*key|network' - better matching for network keys

2. Add validation to detect when lora_appkey11 column is empty and suggest using OTAA keys instead

3. Add a preview/confirmation step that shows:
   - Which column was selected for each key type
   - The actual value that will be used
   - Warning if the selected column is mostly empty

### File Changes Needed
1. `templates/column_mapping.html` - Improve auto-selection patterns
2. `app.py` - Add validation logic
3. `grpc_client.py` - Already correct, no changes needed
4. Add new validation functions to detect and handle CSV misalignment

## Testing
- Test with the provided CSV file
- Verify auto-detection selects 'OTAA keys' for app_key
- Verify nwk_key selection doesn't use network session key
- Create test device and verify correct keys in ChirpStack
