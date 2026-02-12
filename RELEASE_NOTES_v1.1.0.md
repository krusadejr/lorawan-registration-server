# LoRaWAN Device Registration v1.1.0 Release

## Release Date
February 12, 2026

## Changelog

### ✨ New Features

#### 1. **Custom Tags Support**
- Users can now define up to 4 custom tags per registration batch
- Tags apply uniformly to all devices in a single registration session
- Perfect for batch organization: Department, Location, Project, etc.
- Merges seamlessly with device-specific tags from CSV columns

#### 2. **Dynamic Column Mapping**
- Auto-detection of device data columns from CSV/Excel files
- Users can customize column assignments during preview
- Supports: DevEUI, Name, Application ID, Device Profile ID, Network Key, App Key
- Flexible tagging support

#### 3. **Parallel Processing**
- ThreadPoolExecutor-based device registration (up to 10 workers)
- Significantly faster registration for large batches
- Automatic worker scaling based on device count
- Comprehensive logging for monitoring

#### 4. **Application ID Input Field**
- Manual entry when Application ID is not in data file
- Single input applies to all devices in batch
- Stored in session for convenience

#### 5. **Last Sessions Page**
- Save and restore last 5 registration configurations
- Quick recall of server settings, file selections, and mappings
- Always visible on homepage for easy access
- Improves workflow efficiency for recurring tasks

### 🐛 Bug Fixes
- CSV file upload now properly supported in file picker
- Device registration key validation (exactly 32-char hex keys required)
- Improved error handling and user feedback
- Fixed duplicate device handling (skip/replace options)

### 🎨 UI Improvements
- Enhanced dark mode styling matching application theme
- Better visual hierarchy in registration forms
- Improved notification system
- Better responsive design for different screen sizes

### 📝 Documentation & Code
- Comprehensive logging throughout device registration flow
- Internal implementation documentation
- Better code organization and comments
- Improved error messages for debugging

## System Requirements

- **OS**: Windows 10 or later
- **RAM**: 2 GB minimum, 4 GB recommended
- **.NET Framework**: Optional (some features may benefit from modern .NET)
- **Internet**: Required for ChirpStack API communication

## Installation

1. Download `LoRaWAN_Device_Registration_v1.1.0.zip`
2. Extract to your preferred location
3. Open folder `LoRaWAN_Device_Registration`
4. Double-click `START_APPLICATION.bat` or `LoRaWAN_Device_Registration.exe`
5. Application launches in browser at `http://localhost:5000`

## Usage

### Basic Workflow
1. **Configure Server**: Set ChirpStack server URL, API key, and tenant ID
2. **Upload File**: Select CSV, Excel, JSON, or TXT file with device data
3. **Map Columns**: Select or auto-detect device data columns
4. **Add Tags** (Optional): Define up to 4 custom tags for batch organization
5. **Review & Register**: Preview devices and click to register
6. **Check Results**: View success/failure for each device

### Custom Tags Example
```
Tag 1: Abteilung (Department) = IT-Team
Tag 2: Standort (Location) = Berlin
Tag 3: Projekt (Project) = IoT-Gateway
```
All 15 devices in the batch automatically get tagged with these values.

### File Format Support
- **CSV**: Comma-separated values with headers
- **Excel** (.xlsx): Multiple sheets supported
- **JSON**: Array of device objects
- **TXT**: Pipe-separated or custom format (with column headers)

## Known Limitations

- Maximum 4 custom tags per registration batch
- Custom tags apply to all devices uniformly (not per-device)
- ChirpStack keys must be exactly 32 hexadecimal characters
- Tenant-based multi-tenancy per ChirpStack configuration

## Technical Details

- **Framework**: Flask 3.x with Bulma CSS
- **Backend**: Python 3.13 with gRPC client for ChirpStack
- **Database**: In-memory session storage (no persistent DB)
- **Architecture**: Single-page application with Server-Sent Events for streaming

## Upgrade from v1.0.0

✅ **Fully backward compatible** - No breaking changes

Existing users can upgrade without any issues:
- All previous features work identically
- New features are optional and defaulted off
- Configuration remains the same

## Support & Issues

For bug reports or feature requests, please visit the GitHub repository:
https://github.com/krusadejr/lorawan-registration-server

## License

[License Information Here]

## Contributors

Development Team: [@krusadejr]

---

**Thank you for using LoRaWAN Device Registration!**

Visit: https://github.com/krusadejr/lorawan-registration-server
