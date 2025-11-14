# LoRaWAN Device Registration Web Application

A Flask web application for bulk registration of LoRaWAN devices to ChirpStack server using gRPC API.

## Features

- **Multi-Format Support**: Upload Excel (.xlsx, .xls, .xlsm), JSON, or TXT files
- **Flexible Column Mapping**: Map your file columns to device fields
- **Per-Device Configuration**: Specify device_profile_id for each device in your file
- **Bulk Registration**: Register hundreds of devices at once with real-time progress
- **Device Management**: View, search, and bulk delete existing devices
- **Modern Dark UI**: Clean, responsive interface with Bulma CSS
- **Easy Startup**: One-click launch with `start_app.bat`

## Quick Start

Simply double-click **`start_app.bat`** to launch the application.

The app will be available at `http://localhost:5000`

## Setup Instructions (First Time Only)

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```cmd
venv\Scripts\activate.bat
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

After setup, use `start_app.bat` for easy launching!

## Usage

### Basic Workflow

1. **Configure Server** - Enter ChirpStack URL and API key
2. **Upload File** - Select your Excel/JSON/TXT file with device data
3. **Map Columns** - Map your file columns to required device fields
4. **Review & Register** - Preview devices and start bulk registration

### Required Fields in Your File

Your input file must contain these columns:
- `dev_eui`: Device EUI (16 hex characters, e.g., `0004A30B001A2B3C`)
- `name`: Device name
- `application_id`: ChirpStack Application UUID
- `device_profile_id`: ChirpStack Device Profile UUID (**can be different for each device!**)
- `nwk_key`: Network key (32 hex characters)

Optional fields:
- `app_key`: Application key (32 hex characters)
- `description`: Device description

### 🎯 Per-Device Profile Configuration

**New Feature**: You can now specify a **different device_profile_id for each device** in your file!

This is useful when:
- Different devices have different LoRaWAN configurations
- Mixing device types (sensors, actuators, etc.)
- Using different regional parameters per device

Simply include a `device_profile_id` column in your Excel/JSON file with the appropriate UUID for each device.

### Device Management

Navigate to **Geräteverwaltung** to:
- List all devices from an application
- Search and filter devices
- Bulk delete devices with checkboxes
- Delete all devices at once

## Example Files

See `exampleDevicesAIGenerated/` folder for sample files showing the correct format.

## Project Structure

```
lorawan-registration-server/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore            # Git ignore rules
│
├── templates/            # HTML templates
│   ├── base.html        # Base template with Bulma
│   ├── index.html       # Upload page
│   └── preview.html     # Preview page
│
├── static/              # Static files (CSS, JS, images)
│   └── style.css        # Custom styles
│
└── uploads/             # Uploaded files directory
    └── .gitkeep
```

## Technologies Used

- **Backend**: Python Flask
- **Frontend**: HTML, Bulma CSS
- **Excel Processing**: pandas, openpyxl
