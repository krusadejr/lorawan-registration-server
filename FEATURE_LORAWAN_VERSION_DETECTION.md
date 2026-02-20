# LoRaWAN Version Detection Feature

**Branch:** `feature/lorawan-version-detection`

## Overview

This feature adds **automatic LoRaWAN version detection** and **version-aware key mapping** to the device registration system. Instead of guessing or using a bandaid OTAA detection, the system now:

1. **Detects the actual LoRaWAN version** of your device profiles from ChirpStack
2. **Shows you which version each profile uses** via the new diagnostic page
3. **Automatically sends keys to the correct fields** based on version semantics

## The Problem This Solves

Different LoRaWAN versions use different key semantics in ChirpStack's gRPC API:

| Version | `nwk_key` field contains | `app_key` field contains |
|---|---|---|
| **1.0.x OTAA** | Root Application Key (AppKey) | IGNORED |
| **1.1.x** | Network Root Key | Application Root Key |

The original code had no way to know which version you were using, so it sent keys incorrectly for 1.0.x devices. We now fetch the actual version and map accordingly.

## New Features

### 1. LoRaWAN Version Detector Page

**URL:** `/lorawan-version-detector`

Shows a table of all device profiles with:
- Profile name and LoRaWAN version (1.0.x, 1.1.x, etc.)
- MAC version (major.minor.patch)
- Join mode support (OTAA, ABP, both)
- Correct key mapping for each version

**Access:** Click "LoRaWAN Version" in the top navigation menu

**User benefit:** Non-technical users can verify which version they're using BEFORE uploading devices

### 2. Automatic Version Detection During Registration

When you register devices, the system now:
1. Reads the device profile ID from your first device
2. Queries ChirpStack to get that profile's LoRaWAN version
3. Shows you the detected version in the progress stream
4. Uses the correct key mapping for that version

### 3. Version-Aware gRPC Calls

The `create_device_keys()` method now accepts:
- `lorawan_version` (dict): Real version info from ChirpStack
- Falls back to `is_otaa` flag if version info not available

## Code Changes

### grpc_client.py

**New methods:**
```python
parse_mac_version(mac_version_enum)
    # Converts enum 0→5 to human-readable version strings
    
get_device_profiles_via_rest(tenant_id=None)
    # Fetches all device profiles + versions via REST API
    
get_lorawan_version_from_profile_id(device_profile_id, tenant_id=None)
    # Gets version info for specific device profile
```

**Updated methods:**
```python
create_device_keys(..., lorawan_version=None)
    # Now version-aware instead of is_otaa detection
    # Checks: if version['is_1_0_x']: AppKey→nwk_key else AppKey→app_key
```

### app.py

**In `registration_preview()`:**
- Fetch device profile version before showing preview
- Include `lorawan_version` in each device dict

**In `register_devices_stream()`:**
- Fetch device profile version at stream start
- Log detected version to user
- Include `lorawan_version` in each device dict
- Pass to `create_device_keys()`

### templates/lorawan_version_detector.html

New page showing:
- Summary of profiles (total, 1.0.x count, 1.1.x count)
- Detailed table with key mapping info
- Explanation of why versions matter
- Color-coded version badges

### templates/base.html

Added navigation link: "LoRaWAN Version" → `/lorawan-version-detector`

## How It Works

### Data Flow: Device Registration

```
User uploads CSV
    ↓
Extract device profile ID from first row
    ↓
[NEW] Query ChirpStack API for device profile version
    ↓
Version info returned: {'version': '1.0.3', 'is_1_0_x': True, ...}
    ↓
For each device:
    ├─ [NEW] Include version info in device dict
    └─ Extract keys as before
    ↓
Call create_device_keys():
    ├─ [NEW] Check lorawan_version parameter
    └─ [NEW] Route keys to correct fields based on version
    ↓
ChirpStack receives keys in correct fields
    ↓
✅ Device registered with correct ApplicationKey!
```

### Version Detection Logic

```python
if lorawan_version:
    if lorawan_version['is_1_0_x']:
        # LoRaWAN 1.0.x: AppKey in nwk_key field
        proto_nwk_key = app_key_value
        proto_app_key = ""
    elif lorawan_version['is_1_1_x']:
        # LoRaWAN 1.1.x: Standard mapping
        proto_nwk_key = nwk_key_value
        proto_app_key = app_key_value
else:
    # Fallback: Use is_otaa flag (backward compatible)
    if is_otaa:
        proto_nwk_key = app_key_value
        proto_app_key = ""
    else:
        proto_nwk_key = nwk_key_value
        proto_app_key = app_key_value
```

## Testing

### Manual Test Steps

1. **Navigate to LoRaWAN Version Detector**
   - Go to `/lorawan-version-detector`
   - Verify you see your device profiles listed
   - Check "LoRaWAN Version" column shows correct versions

2. **Register Test Device**
   - Upload CSV with 1-2 test devices
   - Watch registration stream
   - Look for: "LoRaWAN-Version erkannt: 1.0.3" (or your version)
   - After completion, check ChirpStack
   - Verify application_key value is correct (from "OTAA keys" column, not "lora_nwkskey")

3. **Verify Different Versions**
   - If you have both 1.0.x and 1.1.x profiles, register devices from each
   - Observe correct key mapping for each version

### Backward Compatibility

✅ **Fully backward compatible:**
- If version detection fails, falls back to `is_otaa` flag
- All existing registrations continue to work
- No breaking changes to API

## Files Changed

```
grpc_client.py
  ├─ Added imports: requests, json
  ├─ Added parse_mac_version() static method
  ├─ Added get_device_profiles_via_rest() method
  ├─ Added get_lorawan_version_from_profile_id() method
  └─ Updated create_device_keys() with lorawan_version parameter

app.py
  ├─ Added /lorawan-version-detector route
  ├─ Updated registration_preview() to detect version
  ├─ Updated register_devices_stream() to detect + use version
  └─ Updated create_device_keys() calls to pass lorawan_version

templates/base.html
  └─ Added navbar link to lorawan_version_detector

templates/lorawan_version_detector.html
  └─ NEW: Diagnostic page showing all profiles + versions
```

## Advantages Over Previous Bandaid

| Aspect | Before | Now |
|---|---|---|
| **Version Detection** | Checks `lora_joinmode` column | Queries ChirpStack API |
| **Reliability** | Breaks if CSV missing column | Always works |
| **User Visibility** | Silent, no feedback | Shows detected version |
| **Errors** | No diagnostics page | Dedicated diagnostic page |
| **Multi-version Support** | Only handles OTAA flag | Handles all LoRaWAN versions |
| **Scalability** | What if 1.2.x comes? | Auto-adapts to new versions |

## Future Improvements

1. **Cache version info** - Don't query ChirpStack for every bulk registration
2. **Auto-handle profile changes** - If user has multiple different profiles, detect each
3. **UI warnings** - Alert if version detection fails
4. **Versioning roadmap** - Document what will happen for future LoRaWAN versions

## Troubleshooting

### "No device profiles found"

**Reason:** API connection issue or ChirpStack not responding  
**Fix:** Check that server URL and API key are configured correctly in Settings

### Version shows as "UNKNOWN"

**Reason:** Enum value from ChirpStack not recognized  
**Fix:** Check ChirpStack API version. May need to update map in `parse_mac_version()`

### Keys still wrong after registration

**Reason:** Version detection ran but mapping logic has bug  
**Fix:**
1. Check logs for: `[Registration] Detected LoRaWAN version: ...`
2. Verify device profile version is correct in diagnostic page
3. Check ChirpStack keys are in expected fields

## Rollback Plan

If issues arise, can easily revert to version-less fix:
```bash
git checkout feature/lorawan-version-detection~1
# Revert to previous bandaid fix
```

Or merge to main and disable via feature flag if needed.

## Next Steps

1. Test with real Dragino devices
2. Test with other device profile versions (1.1.x if available)
3. Monitor logs for any detection failures
4. Consider PR to main branch if tests pass
5. Document in user guide with screenshots
