# LoRaWAN Device Registration Web Application

**[Für die deutsche Version nach unten scrollen](#deutsche-version) / [For German version, scroll down](#deutsche-version)**

A Flask web application for bulk registration of LoRaWAN devices to ChirpStack server using gRPC API.

## 🚀 Standalone Executable Available!

**No Python installation required!** Download the ready-to-use Windows executable from the [Releases](https://github.com/krusadejr/lorawan-registration-server/releases) page.

### For End Users (No Python Required)

1. Download `LoRaWAN_Device_Registration.zip` from the latest release
2. Extract the zip file to any folder
3. Run `START_APPLICATION.bat` or `LoRaWAN_Device_Registration.exe`
4. Open browser to `http://localhost:5000`
5. Configure ChirpStack settings and start registering devices!

**Note**: First startup may take 10-15 seconds. Your antivirus might flag it initially (false positive - safe to allow).

### For Developers

If you want to run from source code or contribute to development, see the [Setup Instructions](#setup-instructions-first-time-only) below.

---

## Features

- **Multi-Format Support**: Upload Excel (.xlsx, .xls, .xlsm), JSON, or TXT files
- **Flexible Column Mapping**: Map your file columns to device fields
- **Per-Device Configuration**: Specify device_profile_id for each device in your file
- **Bulk Registration**: Register hundreds of devices at once with real-time progress
- **Device Management**: View, search, and bulk delete existing devices
- **Duplicate Handling**: Choose to skip or replace existing devices
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

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

After setup, use `start_app.bat` for easy launching!

## Usage Guide

### Step-by-Step Workflow

#### 1. Configure Server Connection

Navigate to **Einstellungen** (Settings) and provide:
- **ChirpStack Server URL**: Your ChirpStack server address (e.g., `localhost:8080`)
- **API Key**: ChirpStack API token (JWT format)
- **Tenant ID**: Your ChirpStack tenant UUID

💡 **Tip**: Test the connection using the **Verbindungstest** button to ensure everything is configured correctly.

#### 2. Prepare Your Device File

Your input file must contain these columns:

**Required Fields:**
- `dev_eui`: Device EUI (16 hex characters, e.g., `0004A30B001A2B3C`)
- `name`: Device name (e.g., "Temperature Sensor Room 101")
- `application_id`: ChirpStack Application UUID
- `device_profile_id`: ChirpStack Device Profile UUID
- `nwk_key`: Network key (32 hex characters)

**Optional Fields:**
- `app_key`: Application key (32 hex characters)
- `description`: Device description

**Supported File Formats:**
- Excel: `.xlsx`, `.xls`, `.xlsm`
- JSON: `.json`
- Text: `.txt` (tab or comma-separated)

#### 3. Upload and Map Columns

1. Click **Datei hochladen** (Upload File) on the main page
2. Select your device file
3. If the file has multiple sheets, choose the relevant sheet
4. Map your file columns to the required device fields
5. Review the preview of your devices

#### 4. Register Devices

1. Review the device preview
2. Choose duplicate handling:
   - **Skip existing devices**: Don't modify devices that already exist
   - **Replace existing devices**: Delete and re-create existing devices with new data
3. Click **Registrierung starten** to begin
4. Watch real-time progress as devices are registered
5. Review the results showing successful and failed registrations

### 🎯 Per-Device Profile Configuration

**Important Feature**: Each device can have a **different device_profile_id**!

This allows you to:
- Mix different device types in one registration batch
- Use different LoRaWAN configurations per device
- Apply region-specific profiles (EU868, US915, etc.)
- Handle devices with different data rates or power settings

Simply include the appropriate `device_profile_id` UUID for each device in your file.

### Device Management

Navigate to **Geräteverwaltung** (Device Management) to:

- **List Devices**: View all devices from a specific application
- **Search & Filter**: Find devices by name or DevEUI
- **Select & Delete**: Use checkboxes to select devices for deletion
- **Bulk Operations**: Delete multiple devices at once
- **Delete All**: Remove all devices from an application (use with caution!)

### Error Messages

The application provides detailed error messages to help troubleshoot issues:

- **Authentication failed**: Check your API key in Settings
- **Application ID not found**: Verify the Application UUID exists in your ChirpStack
- **Device Profile ID not found**: Ensure the Device Profile UUID is valid
- **Invalid DevEUI format**: DevEUI must be exactly 16 hexadecimal characters
- **Invalid key format**: Keys must be exactly 32 hexadecimal characters

## Example Files

Check the `exampleDevicesAIGenerated/` folder for sample files:
- `test_devices_YYYYMMDD_HHMMSS.xlsx`: Template with correct format
- `sample_devices.xlsx`: Example device data

## Project Structure

```
lorawan-registration-server/
│
├── app.py                    # Main Flask application
├── grpc_client.py           # ChirpStack gRPC API client
├── file_parser.py           # File parsing utilities
├── requirements.txt         # Python dependencies
├── start_app.bat           # Easy launcher script
├── README.md               # This documentation
│
├── templates/              # HTML templates
│   ├── base.html          # Base template with navigation
│   ├── index.html         # Upload page
│   ├── server_config.html # Server configuration
│   ├── column_mapping.html # Column mapping interface
│   ├── registration_progress.html # Real-time progress
│   ├── device_management.html # Device list & delete
│   └── help.html          # Help documentation
│
├── static/                # Static files
│   └── style.css         # Custom dark theme styles
│
├── generated/             # Generated gRPC code from protobufs
│   ├── api/              # ChirpStack API definitions
│   └── common/           # Common message types
│
├── exampleDevicesAIGenerated/ # Example device files
│   ├── test_devices_*.xlsx
│   └── sample_devices*.xlsx
│
├── uploads/              # Temporary upload storage
└── logs/                 # Application logs
```

## Technologies Used

- **Backend**: Python 3.x, Flask web framework
- **gRPC Communication**: ChirpStack v4 API via gRPC
- **File Processing**: pandas, openpyxl for Excel parsing
- **Frontend**: HTML5, Bulma CSS framework
- **Real-time Updates**: Server-Sent Events (SSE)

## Troubleshooting

### Connection Issues

- Ensure ChirpStack server is running and accessible
- Verify the server URL uses the correct port (default: `8080` for gRPC)
- Check that your API token has not expired
- Confirm your Tenant ID is correct

### Registration Failures

- **UNAUTHENTICATED errors**: Usually means Application ID or Device Profile ID doesn't exist in your tenant
- **Duplicate devices**: Use "Replace" option if you want to overwrite existing devices
- **Invalid UUID format**: Ensure all UUIDs follow the format `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

### File Format Issues

- Excel files must have at least one sheet with data
- Column headers should be in the first row
- DevEUI and keys must be in hexadecimal format (0-9, A-F)
- Remove any special characters or spaces from DevEUI and keys

## License

This project is for internal use and device management with ChirpStack LoRaWAN Network Server.

---

# Deutsche Version

## LoRaWAN Geräteregistrierungs-Webanwendung

Eine Flask-Webanwendung zur Massenregistrierung von LoRaWAN-Geräten auf einem ChirpStack-Server über die gRPC-API.

## 🚀 Eigenständige Exe-Datei verfügbar!

**Keine Python-Installation erforderlich!** Laden Sie die gebrauchsfertige Windows-Anwendung von der [Releases](https://github.com/krusadejr/lorawan-registration-server/releases)-Seite herunter.

### Für Endbenutzer (keine Python-Installation erforderlich)

1. Laden Sie `LoRaWAN_Device_Registration.zip` vom neuesten Release herunter
2. Entpacken Sie die ZIP-Datei in einen beliebigen Ordner
3. Führen Sie `START_APPLICATION.bat` oder `LoRaWAN_Device_Registration.exe` aus
4. Öffnen Sie den Browser unter `http://localhost:5000`
5. Konfigurieren Sie die ChirpStack-Einstellungen und beginnen Sie mit der Geräteregistrierung!

**Hinweis**: Der erste Start kann 10-15 Sekunden dauern. Ihr Antivirusprogramm könnte es anfangs markieren (Fehlalarm - sicher zu erlauben).

### Für Entwickler

Wenn Sie aus dem Quellcode ausführen oder zur Entwicklung beitragen möchten, siehe die [Einrichtungsanleitung](#einrichtungsanleitung-nur-beim-ersten-mal) unten.

---

## Funktionen

- **Mehrfache Dateiformate**: Upload von Excel (.xlsx, .xls, .xlsm), JSON oder TXT-Dateien
- **Flexible Spaltenzuordnung**: Ordnen Sie Ihre Dateispalten den Gerätefeldern zu
- **Gerätespezifische Konfiguration**: Geben Sie für jedes Gerät eine eigene device_profile_id an
- **Massenregistrierung**: Registrieren Sie hunderte Geräte auf einmal mit Echtzeit-Fortschritt
- **Geräteverwaltung**: Anzeigen, Suchen und Massenlöschen vorhandener Geräte
- **Duplikat-Behandlung**: Wählen Sie, ob vorhandene Geräte übersprungen oder ersetzt werden sollen
- **Modernes Dark UI**: Saubere, responsive Oberfläche mit Bulma CSS
- **Einfacher Start**: Ein-Klick-Start mit `start_app.bat`

## Schnellstart

Doppelklicken Sie einfach auf **`start_app.bat`**, um die Anwendung zu starten.

Die App ist dann verfügbar unter `http://localhost:5000`

## Einrichtungsanleitung (nur beim ersten Mal)

### 1. Virtuelle Umgebung erstellen

```bash
python -m venv venv
```

### 2. Virtuelle Umgebung aktivieren

**Windows:**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

Nach der Einrichtung verwenden Sie `start_app.bat` für den einfachen Start!

## Bedienungsanleitung

### Schritt-für-Schritt-Workflow

#### 1. Server-Verbindung konfigurieren

Navigieren Sie zu **Einstellungen** und geben Sie an:
- **ChirpStack Server-URL**: Ihre ChirpStack-Serveradresse (z.B. `localhost:8080`)
- **API-Schlüssel**: ChirpStack API-Token (JWT-Format)
- **Tenant-ID**: Ihre ChirpStack-Tenant-UUID

💡 **Tipp**: Testen Sie die Verbindung mit dem **Verbindungstest**-Button, um sicherzustellen, dass alles korrekt konfiguriert ist.

#### 2. Gerätedatei vorbereiten

Ihre Eingabedatei muss folgende Spalten enthalten:

**Pflichtfelder:**
- `dev_eui`: Geräte-EUI (16 Hexadezimalzeichen, z.B. `0004A30B001A2B3C`)
- `name`: Gerätename (z.B. "Temperatursensor Raum 101")
- `application_id`: ChirpStack Application UUID
- `device_profile_id`: ChirpStack Device Profile UUID
- `nwk_key`: Netzwerkschlüssel (32 Hexadezimalzeichen)

**Optionale Felder:**
- `app_key`: Anwendungsschlüssel (32 Hexadezimalzeichen)
- `description`: Gerätebeschreibung

**Unterstützte Dateiformate:**
- Excel: `.xlsx`, `.xls`, `.xlsm`
- JSON: `.json`
- Text: `.txt` (Tab- oder Komma-getrennt)

#### 3. Datei hochladen und Spalten zuordnen

1. Klicken Sie auf der Hauptseite auf **Datei hochladen**
2. Wählen Sie Ihre Gerätedatei aus
3. Falls die Datei mehrere Blätter hat, wählen Sie das relevante Blatt
4. Ordnen Sie Ihre Dateispalten den erforderlichen Gerätefeldern zu
5. Überprüfen Sie die Vorschau Ihrer Geräte

#### 4. Geräte registrieren

1. Überprüfen Sie die Gerätevorschau
2. Wählen Sie die Duplikat-Behandlung:
   - **Vorhandene Geräte überspringen**: Bereits existierende Geräte nicht ändern
   - **Vorhandene Geräte ersetzen**: Existierende Geräte löschen und mit neuen Daten neu erstellen
3. Klicken Sie auf **Registrierung starten**
4. Beobachten Sie den Echtzeit-Fortschritt während der Geräteregistrierung
5. Überprüfen Sie die Ergebnisse mit erfolgreichen und fehlgeschlagenen Registrierungen

### 🎯 Gerätespezifische Profil-Konfiguration

**Wichtige Funktion**: Jedes Gerät kann eine **andere device_profile_id** haben!

Dies ermöglicht Ihnen:
- Verschiedene Gerätetypen in einem Registrierungsvorgang zu mischen
- Unterschiedliche LoRaWAN-Konfigurationen pro Gerät zu verwenden
- Regionsspezifische Profile anzuwenden (EU868, US915, etc.)
- Geräte mit unterschiedlichen Datenraten oder Leistungseinstellungen zu verwalten

Geben Sie einfach die entsprechende `device_profile_id` UUID für jedes Gerät in Ihrer Datei an.

### Geräteverwaltung

Navigieren Sie zu **Geräteverwaltung**, um:

- **Geräte auflisten**: Alle Geräte einer bestimmten Anwendung anzeigen
- **Suchen & Filtern**: Geräte nach Name oder DevEUI finden
- **Auswählen & Löschen**: Checkboxen verwenden, um Geräte zum Löschen auszuwählen
- **Massenoperationen**: Mehrere Geräte auf einmal löschen
- **Alle löschen**: Alle Geräte aus einer Anwendung entfernen (mit Vorsicht verwenden!)

### Fehlermeldungen

Die Anwendung bietet detaillierte Fehlermeldungen zur Fehlerbehebung:

- **Authentication failed**: Überprüfen Sie Ihren API-Schlüssel in den Einstellungen
- **Application ID not found**: Stellen Sie sicher, dass die Application UUID in Ihrem ChirpStack existiert
- **Device Profile ID not found**: Prüfen Sie, ob die Device Profile UUID gültig ist
- **Invalid DevEUI format**: DevEUI muss genau 16 Hexadezimalzeichen sein
- **Invalid key format**: Schlüssel müssen genau 32 Hexadezimalzeichen sein

## Beispieldateien

Schauen Sie sich den Ordner `exampleDevicesAIGenerated/` für Beispieldateien an:
- `test_devices_JJJJMMTT_HHMMSS.xlsx`: Vorlage mit korrektem Format
- `sample_devices.xlsx`: Beispiel-Gerätedaten

## Projektstruktur

```
lorawan-registration-server/
│
├── app.py                    # Haupt-Flask-Anwendung
├── grpc_client.py           # ChirpStack gRPC API Client
├── file_parser.py           # Datei-Parsing-Utilities
├── requirements.txt         # Python-Abhängigkeiten
├── start_app.bat           # Einfaches Startskript
├── README.md               # Diese Dokumentation
│
├── templates/              # HTML-Vorlagen
│   ├── base.html          # Basis-Vorlage mit Navigation
│   ├── index.html         # Upload-Seite
│   ├── server_config.html # Server-Konfiguration
│   ├── column_mapping.html # Spaltenzuordnung-Oberfläche
│   ├── registration_progress.html # Echtzeit-Fortschritt
│   ├── device_management.html # Geräteliste & Löschen
│   └── help.html          # Hilfe-Dokumentation
│
├── static/                # Statische Dateien
│   └── style.css         # Benutzerdefinierte Dark-Theme-Styles
│
├── generated/             # Generierter gRPC-Code aus Protobufs
│   ├── api/              # ChirpStack API-Definitionen
│   └── common/           # Gemeinsame Nachrichtentypen
│
├── exampleDevicesAIGenerated/ # Beispiel-Gerätedateien
│   ├── test_devices_*.xlsx
│   └── sample_devices*.xlsx
│
├── uploads/              # Temporärer Upload-Speicher
└── logs/                 # Anwendungsprotokolle
```

## Verwendete Technologien

- **Backend**: Python 3.x, Flask Web-Framework
- **gRPC-Kommunikation**: ChirpStack v4 API über gRPC
- **Dateiverarbeitung**: pandas, openpyxl für Excel-Parsing
- **Frontend**: HTML5, Bulma CSS-Framework
- **Echtzeit-Updates**: Server-Sent Events (SSE)

## Fehlerbehebung

### Verbindungsprobleme

- Stellen Sie sicher, dass der ChirpStack-Server läuft und erreichbar ist
- Überprüfen Sie, dass die Server-URL den richtigen Port verwendet (Standard: `8080` für gRPC)
- Prüfen Sie, ob Ihr API-Token noch gültig ist
- Bestätigen Sie, dass Ihre Tenant-ID korrekt ist

### Registrierungsfehler

- **UNAUTHENTICATED-Fehler**: Bedeutet normalerweise, dass Application ID oder Device Profile ID in Ihrem Tenant nicht existiert
- **Doppelte Geräte**: Verwenden Sie die Option "Ersetzen", wenn Sie vorhandene Geräte überschreiben möchten
- **Ungültiges UUID-Format**: Stellen Sie sicher, dass alle UUIDs dem Format `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` folgen

### Dateiformat-Probleme

- Excel-Dateien müssen mindestens ein Blatt mit Daten haben
- Spaltenüberschriften sollten in der ersten Zeile stehen
- DevEUI und Schlüssel müssen im Hexadezimalformat sein (0-9, A-F)
- Entfernen Sie alle Sonderzeichen oder Leerzeichen aus DevEUI und Schlüsseln

## Lizenz

Dieses Projekt ist für den internen Gebrauch und die Geräteverwaltung mit ChirpStack LoRaWAN Network Server gedacht.
