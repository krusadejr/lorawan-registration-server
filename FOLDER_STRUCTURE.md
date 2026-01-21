# Project Folder Structure Guide

## Overview

This document explains the role and purpose of each folder in the LoRaWAN Device Registration Server project.

---

## 📁 Core Application Folders

### `/` (Root Directory)
**Main application files and entry points**

Key files here:
- `app.py` - Main Flask application (1,340+ lines) - **THE HEART OF THE APP**
- `file_parser.py` - Multi-format file parsing module (CSV, Excel, JSON, TXT)
- `grpc_client.py` - gRPC client for ChirpStack API communication
- `requirements.txt` - Python package dependencies
- `app.spec` - PyInstaller configuration for building Windows executable
- `start_app.bat` - Quick launch script for end users
- `README.md` - Public documentation

---

## 🎨 Frontend & UI

### `/templates/`
**HTML templates for web interface**

Files:
- `base.html` - Base template with navigation and layout
- `index.html` - Home page with file upload form
- `server_config.html` - Server configuration settings page
- `select_sheet.html` - Sheet/table selection for multi-sheet files
- `column_mapping.html` - Column mapping interface
- `registration_preview.html` - Device preview before registration
- `registration_progress.html` - Real-time progress during registration
- `registration_results.html` - Final registration results summary
- `test_connection.html` - Connection test results page
- `help.html` - User help and documentation
- `delimiter_input.html` - Manual CSV delimiter selection

**Purpose**: Renders the web UI that users interact with
**Uses**: Jinja2 templating, Bulma CSS framework

---

### `/static/`
**Static assets (CSS, JavaScript, images)**

Files:
- `style.css` - Custom styling (Bulma theme customizations)
- `favicon.ico` - Browser tab icon

**Purpose**: Styling, fonts, icons for the web interface
**Framework**: Bulma CSS (responsive, mobile-friendly)

---

## 🔧 Generated Code & Protocols

### `/generated/`
**Auto-generated gRPC Protocol Buffer code**

Structure:
```
generated/
├── __init__.py
├── api/
│   ├── device_pb2.py
│   ├── device_pb2_grpc.py
│   ├── application_pb2.py
│   ├── application_pb2_grpc.py
│   └── ... (other proto definitions)
└── common/
    ├── common_pb2.py
    └── ... (shared message types)
```

**Purpose**: Contains compiled Protocol Buffer stubs for ChirpStack gRPC communication
**Generated From**: ChirpStack v4 `.proto` files
**Usage**: Imported by `grpc_client.py` for gRPC API calls
**Note**: Do NOT manually edit - auto-generated from proto definitions

---

### `/protoBuffsAPI/`
**Original Protocol Buffer source files**

**Purpose**: Contains `.proto` definition files from ChirpStack
**Status**: Reference/backup - actual code is in `/generated/`
**Usage**: If updating ChirpStack API, regenerate `/generated/` from these

---

## 📁 Data & Storage

### `/uploads/`
**Temporary storage for uploaded files**

Files:
- `{UUID}_{extension}` - User-uploaded files (Excel, CSV, JSON, TXT)
- `{UUID}_parsed.json` - Cached parsed device data (JSON format)

**Purpose**: 
- Temporary holding area for user file uploads
- Cache for parsed data during registration workflow
- Session-based storage

**Lifecycle**:
1. User uploads file → stored with UUID name
2. File is parsed → cached as `_parsed.json`
3. Data used during preview/registration
4. Cleaned up after session (files can be manually deleted)

**Git Status**: Ignored by `.gitignore` (local-only)

---

### `/logs/`
**Application runtime logs**

Files:
- `app_YYYYMMDD.log` - Daily log files (one per day)

**Purpose**: 
- Track application events (startup, uploads, registrations)
- Debug information for troubleshooting
- Error logging

**Log Levels**: DEBUG, INFO, WARNING, ERROR

**Git Status**: Ignored by `.gitignore` (local-only)
**Retention**: Historical logs backed up in `PRIVATE/logs_backup/`

---

## 🔒 Private & Non-Tracked

### `/PRIVATE/`
**Personal, development, and non-public files**

**IMPORTANT**: Not tracked by Git - stays local only

Subfolders:
- `CheckOutFolder/` - Thesis documentation and chapter drafts
- `exampleDevicesAIGenerated/` - AI-generated test device data
- `logs_backup/` - Historical log files
- `README.md` - Explanation of PRIVATE folder

**Purpose**: 
- Keep thesis work, internal notes, test data local-only
- Prevent personal information from public repository
- Maintain clean public repo

**Git Status**: Listed in `.gitignore` - will never be pushed

---

### `/examplesHersteller/`
**Vendor/manufacturer example data** (still in public repo)

Files:
- `data_elvaco_neu.txt` - Sample device data from vendor
- `gRPC_Api_Device.xlsm` - Example device data template

**Purpose**: Reference examples for data format
**Status**: Part of repository (for documentation)

---

## 🏗️ Build & Distribution

### `/dist/`
**Standalone Windows executable build output**

Structure:
```
dist/
└── LoRaWAN_Device_Registration/
    ├── LoRaWAN_Device_Registration.exe
    ├── START_APPLICATION.bat
    ├── README.txt
    ├── _internal/
    │   ├── python.exe (Python 3.13.4 bundled)
    │   └── (All Python libraries + timezone database)
    ├── templates/
    ├── static/
    └── generated/
```

**Purpose**: 
- Final distributable application for end users
- No Python installation required
- Ready to run Windows executable

**Building**: `pyinstaller app.spec`
**Distribution**: Zipped and released on GitHub

---

### `/build/`
**Temporary PyInstaller build artifacts**

**Purpose**: Intermediate files during executable building
**Status**: Can be safely deleted after build completes
**Git Status**: Ignored by `.gitignore`

---

## 📚 Testing & Examples

### `/UploadTest_20251119/`
**Test upload files for development/testing**

Files:
- `testUploadFile_*.csv` - CSV files with different delimiters (comma, semicolon, pipe)
- `testUploadFile_*.txt` - Text files (tab, space, JSON-lines delimiters)
- `README.md` - Test documentation

**Purpose**: Manual testing of delimiter detection and file parsing
**Usage**: Upload these files to test the application locally
**Location**: Kept at root for easy testing (not in PRIVATE)

---

## 🐍 Python Environment

### `/venv/`
**Virtual environment directory**

**Purpose**: Isolated Python environment with all dependencies
**Contents**: 
- Python 3.13.4 interpreter
- All packages from `requirements.txt`
- Activation scripts for Windows/Linux/Mac

**Usage**:
```bash
venv\Scripts\activate    # Windows
source venv/bin/activate # Linux/Mac
```

**Git Status**: Ignored by `.gitignore` (large, system-specific)

---

### `/__pycache__/`
**Python bytecode cache**

**Purpose**: Compiled Python files for faster imports
**Auto-generated**: By Python interpreter
**Git Status**: Ignored by `.gitignore` (not needed for distribution)

---

## 📄 Configuration & Documentation

### Root Configuration Files

| File | Purpose |
|------|---------|
| `.gitignore` | Git ignore patterns (uploads, venv, logs, PRIVATE, etc.) |
| `.gitattributes` | Line ending configuration for cross-platform compatibility |
| `requirements.txt` | Python package dependencies |
| `config_history.json` | User's saved server configurations (local-only) |

### Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Main project documentation (English/German) |
| `IMPLEMENTATION_PLAN.md` | Technical implementation details |
| `OPTIMIZATIONS.md` | Performance optimization notes |
| `QUICK_START.md` | Quick reference guide |
| `FOLDER_STRUCTURE.md` | This file - folder explanations |

---

## 📊 Git Repository Files

### `/.git/`
**Git repository metadata**

**Purpose**: Version control system data
**Contains**: Commit history, branches, remotes
**Status**: Auto-managed by Git (don't manually edit)

---

## 🔄 Data Flow Through Folders

### User Upload Workflow

```
User Action
    ↓
Templates/ (User sees HTML interface)
    ↓
app.py (Receives upload, routes to file_parser)
    ↓
file_parser.py (Parses file)
    ↓
uploads/ (File cached + parsed JSON stored)
    ↓
Templates/ (Preview shown to user)
    ↓
app.py (Receives registration confirmation)
    ↓
grpc_client.py + generated/ (gRPC calls to ChirpStack)
    ↓
logs/ (Events logged)
    ↓
Templates/ (Results displayed to user)
```

---

## 🎯 Folder Purposes Summary Table

| Folder | Type | Purpose | Git Status |
|--------|------|---------|-----------|
| `/templates/` | Frontend | HTML web pages | Tracked ✓ |
| `/static/` | Frontend | CSS, icons, styles | Tracked ✓ |
| `/generated/` | Backend | gRPC protocol buffers | Tracked ✓ |
| `/protoBuffsAPI/` | Backend | Proto source files | Tracked ✓ |
| `/uploads/` | Runtime | Temporary file storage | Ignored ✗ |
| `/logs/` | Runtime | Application logs | Ignored ✗ |
| `/venv/` | Dev | Python environment | Ignored ✗ |
| `/build/` | Dev | PyInstaller artifacts | Ignored ✗ |
| `/__pycache__/` | Dev | Python cache | Ignored ✗ |
| `/dist/` | Build | Executable distribution | Tracked (*.exe) ✓ |
| `/PRIVATE/` | Internal | Personal/non-public files | Ignored ✗ |
| `/examplesHersteller/` | Reference | Vendor examples | Tracked ✓ |
| `/.git/` | VCS | Git repository | System |

---

## 📝 Key Takeaways

1. **Production Code**: `/` (root) + `/templates/` + `/static/` + `/generated/`
2. **Runtime Data**: `/uploads/` and `/logs/` (regenerated, not pushed)
3. **Development Only**: `/venv/`, `/build/`, `/__pycache__/`, `/PRIVATE/`
4. **Distribution**: `/dist/` folder contains the standalone executable
5. **Configuration**: `requirements.txt`, `.gitignore`, `app.spec` control the build

---

## 🚀 For Production Deployment

**Essential folders to deploy**:
- `dist/LoRaWAN_Device_Registration/` - Use the standalone executable

**Optional for developers**:
- All root Python files (app.py, grpc_client.py, file_parser.py)
- `/templates/`, `/static/`, `/generated/`
- `requirements.txt`

**DO NOT deploy**:
- `/venv/` - User installs or uses standalone exe
- `/PRIVATE/` - Keep local only
- `/build/` - Temporary files
- `/__pycache__/` - Regenerated automatically

---

**Last Updated**: January 21, 2026
