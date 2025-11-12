# LoRaWAN Device Registration Web App - Implementation Plan

## Project Overview
Web application for bulk registration of LoRaWAN devices to ChirpStack server using gRPC API.

---

## Requirements Summary

### 1. File Upload & Processing
- **Supported Formats**: Excel (.xlsx, .xls, .xlsm), Text files (.txt, .json)
- **Multi-Sheet Support**: Yes - user can select which sheet to process
- **Column Mapping**: User selects which columns map to device properties
- **Preview**: Show parsed data before registration

### 2. Server Configuration
- **ChirpStack URL**: http://localhost:8080 (configurable)
- **API Key**: User-provided (stored in global variable)
- **Tenant ID**: Optional - prompt if not in Excel file
- **Application ID**: Use existing - prompt if not in Excel file  
- **Device Profile ID**: Required - prompt if not in Excel file

### 3. Device Registration Fields (from examples)
**Required Fields:**
- `dev_eui` - Device EUI (16 hex characters)
- `name` - Device name (usually same as dev_eui)
- `application_id` - UUID of application
- `device_profile_id` - UUID of device profile
- `nwk_key` - Network key (32 hex characters)
- `app_key` - Application key (32 hex characters)

**Optional Fields:**
- `description` - Device description
- `is_disabled` - Boolean (default: false)
- `skip_fcnt_check` - Boolean (default: false)
- `tags` - Dictionary (Ort, Typ, Zaehlernummer, SerialNo)
- `variables` - Dictionary (SerialNo)

### 4. gRPC Implementation
- **Proto Files**: Located in `protoBuffsAPI/api/proto/api/device.proto`
- **Methods to Use**:
  - `DeviceService.Create` - Create device
  - `DeviceService.CreateKeys` - Create device keys
- **Authentication**: API key in metadata

### 5. Logging System
- **Log Location**: `logs/` folder
- **Log Format**: JSON for structured data, text for human-readable
- **Log Contents**:
  - Timestamp
  - Action (upload, preview, registration start/end)
  - Device details (dev_eui, name)
  - Success/Failure status
  - Error messages if any
  - Request/Response data
- **UI Access**: Button to view logs in web interface

### 6. User Interface Flow

#### Page 1: Home (Excel Upload)
- Upload file
- Select sheet (if multiple)
- Preview data in table
- Select column mappings
- Button: "Weiter zur Konfiguration" (Continue to Configuration)

#### Page 2: Server Configuration
- Server URL (default: http://localhost:8080)
- API Key
- Tenant ID (optional)
- Application ID (if not in Excel)
- Device Profile ID (if not in Excel)
- Button: "ChirpStack öffnen" (Open ChirpStack) - opens in new tab
- Button: "Konfiguration speichern" (Save Configuration)

#### Page 3: Registration Preview
- Show all devices to be registered
- Configuration summary
- Real-time progress bar
- Button: "Registrierung starten" (Start Registration)
- Live status updates during registration

#### Page 4: Registration Results
- Summary: Total, Successful, Failed
- Detailed list with status per device
- Download logs button
- View logs in browser button

### 7. Technical Stack
- **Backend**: Python Flask
- **gRPC**: grpcio, grpcio-tools
- **Excel Processing**: pandas, openpyxl
- **Proto Compilation**: protoc (compile .proto to Python)
- **Frontend**: Bulma CSS (dark mode)
- **Progress Updates**: Server-Sent Events (SSE) or WebSockets

---

## Implementation Steps

### Phase 1: Setup gRPC
1. Install grpcio and grpcio-tools
2. Compile proto files to Python
3. Create gRPC client helper class
4. Test connection to ChirpStack

### Phase 2: Enhanced File Upload
1. Update upload page to support .txt and .json files
2. Add sheet selection UI for multi-sheet Excel files
3. Add column mapping interface
4. Store uploaded data in session

### Phase 3: Server Configuration Enhancement
1. Add Tenant ID field
2. Add Application ID field
3. Add Device Profile ID field
4. Add ChirpStack URL field
5. Add "Open ChirpStack" button

### Phase 4: Registration Logic
1. Create device registration service
2. Implement gRPC calls for device creation
3. Implement gRPC calls for key creation
4. Add error handling and retries
5. Implement progress tracking

### Phase 5: Logging System
1. Create logging module
2. Create logs directory
3. Implement file logging
4. Create log viewer page
5. Add download logs functionality

### Phase 6: Real-time Progress
1. Implement Server-Sent Events
2. Create progress tracking endpoint
3. Update UI with live progress
4. Show device-by-device status

### Phase 7: Testing & Refinement
1. Test with example files
2. Test error scenarios
3. Validate gRPC communication
4. UI/UX improvements

---

## File Structure
```
lorawan-registration-server/
├── app.py                          # Main Flask application
├── grpc_client.py                  # gRPC client helper
├── device_service.py               # Device registration logic
├── logger_service.py               # Logging functionality
├── requirements.txt                # Python dependencies
├── protoBuffsAPI/                  # Proto files
│   └── api/proto/api/
│       ├── device.proto
│       └── ...
├── generated/                      # Generated gRPC code (from proto)
│   └── api/
│       ├── device_pb2.py
│       └── device_pb2_grpc.py
├── templates/
│   ├── base.html
│   ├── index.html                  # File upload
│   ├── column_mapping.html         # Map columns
│   ├── server_config.html          # Server configuration
│   ├── registration_preview.html   # Preview before registration
│   ├── registration_progress.html  # Live progress
│   ├── registration_results.html   # Results
│   └── logs_viewer.html            # View logs
├── static/
│   ├── style.css
│   └── js/
│       └── progress.js             # Progress updates
├── logs/                           # Log files
│   ├── registration_YYYYMMDD_HHMMSS.log
│   └── registration_YYYYMMDD_HHMMSS.json
├── uploads/                        # Temporary file storage
└── examplesHersteller/             # Example files
    ├── gRPC_Api_Device.xlsm
    ├── data_elvaco_neu.txt
    └── data_elvaco_neu_keys.txt
```

---

## Data Flow

1. **User uploads file** → File stored in session → Parse sheets/columns
2. **User selects sheet & maps columns** → Data extracted → Preview shown
3. **User configures server** → Config stored in global variables
4. **User reviews preview** → Clicks "Start Registration"
5. **Backend processes each device**:
   - Create device via gRPC
   - Create device keys via gRPC
   - Log result
   - Update progress
6. **User views results** → Can download/view logs

---

## Global Variables to Track

```python
SERVER_URL = None          # ChirpStack server URL
API_CODE = None            # API key for authentication
TENANT_ID = None           # Tenant ID (optional)
APPLICATION_ID = None      # Application ID
DEVICE_PROFILE_ID = None   # Device Profile ID
UPLOADED_DATA = None       # Parsed device data from file
REGISTRATION_STATUS = {}   # Current registration progress
```

---

## Error Handling

1. **File Upload Errors**
   - Invalid format
   - Empty file
   - Corrupted file

2. **gRPC Errors**
   - Connection refused
   - Authentication failed
   - Device already exists
   - Invalid parameters

3. **Validation Errors**
   - Missing required fields
   - Invalid DevEUI format
   - Invalid key format
   - Missing configuration

---

## Notes for Development

- Use example files in `examplesHersteller/` for testing
- Proto files are in `protoBuffsAPI/api/proto/api/`
- ChirpStack endpoint: `http://localhost:8080`
- gRPC typically uses port 8080 (check ChirpStack config)
- API key goes in gRPC metadata: `('authorization', 'Bearer <api_key>')`
- Device must be created before keys can be added
- Test with small batch first (5-10 devices)

---

## Questions Still to Clarify

1. Should we validate DevEUI format before registration?
2. What happens if a device already exists? Skip or update?
3. Should we support device deletion/cleanup?
4. Maximum batch size recommendation?
5. Retry logic - how many times?

---

## Example Device JSON Structure (from txt files)

```json
{
  "device": {
    "dev_eui": "94193A0103001D3C",
    "name": "94193A0103001D3C",
    "description": "",
    "application_id": "00000000-0000-0000-0000-000000000008",
    "device_profile_id": "1b14ae72-1bdf-4781-bab6-fb0054e46d86",
    "is_disabled": false,
    "skip_fcnt_check": false,
    "tags": {
      "Ort": "",
      "Typ": "CMi4160i / interne Antenne / Sharky",
      "Zaehlernummer": "",
      "SerialNo": "94193A0103001D3C"
    },
    "variables": {
      "SerialNo": "94193A0103001D3C"
    }
  }
}
```

```json
{
  "device_keys": {
    "dev_eui": "94193A0103001D3C",
    "nwk_key": "49C1B29AFAB03794E82EDDF657DB22FC",
    "app_key": "49C1B29AFAB03794E82EDDF657DB22FC"
  }
}
```

---

**Last Updated**: October 23, 2025
