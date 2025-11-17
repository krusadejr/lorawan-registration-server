# AI-Generated Sample Device Files

This folder contains sample LoRaWAN device data files for testing the bulk registration application.

## Files

### 1. `sample_devices.xlsx` - Excel Format
- **Format**: Microsoft Excel (.xlsx)
- **Devices**: 10 sample devices
- **Sheet Name**: "Devices"
- **Columns**:
  - `dev_eui`: Device EUI (16 hex characters)
  - `name`: Device name
  - `application_id`: Application ID to assign device to
  - `device_profile_id`: Device profile ID to use
  - `nwk_key`: Network key (32 hex characters)
  - `app_key`: Application key (32 hex characters)
  - `description`: Device description

### 2. `test_devices_*.xlsx` - Test Files with Timestamps
- **Purpose**: Test files created for specific testing sessions
- **Naming**: `test_devices_YYYYMMDD_HHMMSS.xlsx`
- **Format**: Same structure as sample_devices.xlsx
- **Note**: These files include the required `device_profile_id` column and are ready for testing

### 3. `sample_devices.txt` - JSON Lines Format
- **Format**: Text file with one JSON object per line
- **Devices**: 5 sample devices
- **Structure**: Each line is a complete JSON object with all device fields

### 3. `sample_devices.json` - JSON Format
- **Format**: Standard JSON file
- **Devices**: 8 sample devices
- **Structure**: Root object with "devices" array containing device objects
- **Additional Fields**: Includes "tags" object for metadata

## Field Requirements

### Required Fields
- `dev_eui`: Must be 16 hexadecimal characters (8 bytes)
- `name`: Device name (any string)
- `application_id`: Target application identifier
- `device_profile_id`: Device profile identifier
- `nwk_key`: Network session key (32 hex characters / 16 bytes)
- `app_key`: Application session key (32 hex characters / 16 bytes)

### Optional Fields
- `description`: Human-readable device description
- `tags`: Key-value pairs for metadata (JSON format only)

## Usage

1. Upload any of these files to the web application
2. Select the sheet/section containing device data
3. Map columns to required fields
4. Review and confirm device registration

## Notes

- All device EUIs and keys in these files are randomly generated for testing
- These devices are NOT real and should not be used in production
- Application IDs and Device Profile IDs must exist in your ChirpStack instance before registration
