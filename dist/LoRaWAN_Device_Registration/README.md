# LoRaWAN Device Registration Server

Eine Flask-Webanwendung zur Massenregistrierung von LoRaWAN-Geräten auf einem ChirpStack-Server mit gRPC-API.

## 🚀 Schnellstart

**Keine Python-Installation erforderlich!** Laden Sie die vorkonfigurierte Windows-Anwendung aus der [Releases](https://github.com/krusadejr/lorawan-registration-server/releases) Seite herunter.

### Für Endbenutzer (Windows EXE)

1. **Download**: Laden Sie LoRaWAN_Device_Registration_v1.2.0.zip aus der neuesten Version herunter
2. **Entpacken**: Extrahieren Sie die ZIP-Datei an einen beliebigen Ort
3. **Starten**: Doppelklicken Sie auf START_APPLICATION.bat
4. **Öffnen**: Der Browser öffnet sich automatisch auf http://localhost:5000
5. **Konfigurieren**: Geben Sie die ChirpStack-Servereinstellungen ein

### Für Entwickler (Python-Entwicklung)

Siehe [Entwicklungs-Setup](#entwicklungs-setup) Abschnitt unten.

---

## 📋 Funktionen

- ✅ Multi-Format Support: Excel (XLSX, XLS, XLSM), CSV, JSON, TXT
- ✅ Automatische Erkennung von CSV-Trennzeichen
- ✅ Flexible Spaltenzuordnung
- ✅ Massenregistrierung von Geräten (hunderte gleichzeitig)
- ✅ Echtzeitfortschritt während der Registrierung
- ✅ Konfigurationsverlauf mit Autovervollständigung
- ✅ Modernes dunkles Design mit responsive UI
- ✅ gRPC Kommunikation mit ChirpStack API
- ✅ Detaillierte Fehlerbehandlung und Duplikat-Handling

---

## 🔧 Anwendungsworkflow

### Schritt 1: Server-Konfiguration

Beim ersten Start ChirpStack-Servereinstellungen konfigurieren:

1. Klicken Sie auf **Server-Konfiguration** in der Navigation
2. Geben Sie ein: Server URL, API Key Token, Tenant ID
3. Klicken Sie auf **Verbindung testen**
4. Einstellungen werden automatisch gespeichert

### Schritt 2: Datei hochladen

1. Klicken Sie auf **Datei hochladen** auf der Startseite
2. Wählen Sie Ihre Datei (Excel, CSV, JSON oder TXT)
3. Für Excel: Wählen Sie das richtige Arbeitsblatt aus

### Schritt 3: Spaltenzuordnung

1. Das System zeigt automatisch erkannte Spalten
2. Ordnen Sie Ihre Datei-Spalten zu:

**Erforderliche Felder:**
- dev_eui: EUI des Geräts
- name: Gerätename
- application_id: Application-UUID
- device_profile_id: Device Profile UUID
- nwk_key: Network Key (32 Hex-Zeichen)
- app_key: Application Key (32 Hex-Zeichen)

**Optional:**
- description: Gerätebeschreibung
- tags: Tags im Format key1:value1|key2:value2

### Schritt 4: Datenvorschau

Das System zeigt erkannte Daten mit Status an

### Schritt 5: LoRaWAN-Version wählen

**WICHTIG**: Wählen Sie die richtige LoRaWAN-Version!

**LoRaWAN 1.0.x (OTAA):**
- Application Key → nwk_key Feld
- app_key Feld wird ignoriert

**LoRaWAN 1.1.x:**
- Network Key → nwk_key Feld
- Application Key → app_key Feld

**Wie finde ich die Version?**
In ChirpStack: Device Profiles → Profil öffnen → MAC Version anschauen

### Schritt 6: Registrierung starten

1. Klicken Sie auf **Registrieren**
2. Fortschritt wird live angezeigt
3. Nach Abschluss: Erfolg/Fehler/Übersprungen

---

## 📝 Dateiformat-Anforderungen

### Excel-Dateien (.xlsx, .xls, .xlsm)

Erste Zeile mit Spaltennamen:

\\\
dev_eui,name,application_id,device_profile_id,nwk_key,app_key,description,tags
0000000000000001,Sensor-001,app-uuid,profile-uuid,00112233...FF,00112233...FF,Temp Sensor,location:floor1
\\\

### CSV-Dateien (.csv)

Standard CSV mit Komma oder Semikolon:

\\\
dev_eui,name,application_id,device_profile_id,nwk_key,app_key
0000000000000001,Sensor-001,app-uuid,profile-uuid,00112233...FF,00112233...FF
\\\

### JSON-Dateien (.json)

Array von Objekten mit den gleichen Feldern

### Textdateien (.txt)

Tab- oder Space-getrennte Werte (automatisch erkannt)

---

## ⚙️ Konfiguration

### Server-Einstellungen (Browser-Speicher)

- **Server URL**: ChirpStack gRPC Server Adresse
- **API Key**: Authentifizierungs-Token
- **Tenant ID**: Tenant-Kennung (UUID)

### Duplikat-Behandlung

- **Überspringen**: Existierende Geräte nicht ändern
- **Aktualisieren**: Existierende Geräte aktualisieren
- **Fehler**: Abbrechen, wenn Gerät existiert

---

## 🛠️ Technologie-Stack

- Backend: Python 3.13+, Flask 3.x
- Kommunikation: gRPC, Protocol Buffers
- Datenverarbeitung: pandas, openpyxl
- Frontend: Bulma CSS 0.9.4, Font Awesome 6.4, JavaScript
- Distribution: PyInstaller (Windows EXE)

---

## 📦 Projektstruktur

\\\
lorawan-registration-server/
├── app.py                          # Haupt-Anwendung
├── grpc_client.py                  # ChirpStack gRPC-Client
├── file_parser.py                  # Datei-Parser
├── app.spec                        # PyInstaller-Config
├── README.md                       # Diese Datei
├── SOLUTION_SUMMARY.md             # Technische Doku
├── USER_GUIDE_KEY_MAPPING.md       # Key-Zuordnung
├── templates/                      # HTML-Vorlagen
├── static/                         # CSS, Icons
├── generated/                      # gRPC Protocol Buffers
├── dist/                           # EXE Distribution
│   └── LoRaWAN_Device_Registration/
│       ├── LoRaWAN_Device_Registration.exe
│       ├── START_APPLICATION.bat
│       ├── _internal/
│       └── logs/
├── uploads/                        # Temp Dateien
└── logs/                           # App-Logs
\\\

---

## 🔌 ChirpStack Integration

### Erforderliche Informationen

1. **Server URL**: z.B. http://192.168.1.100:8080
2. **API Key/Token**: Aus ChirpStack Admin Panel
3. **Tenant ID**: UUID aus ChirpStack Admin Panel

### Testverbindung

Button überprüft:
- Server erreichbar
- API-Authentifizierung gültig
- gRPC-Kommunikation funktioniert

---

## 🐛 Häufige Fehler und Lösungen

### Verbindung fehlgeschlagen
- **Ursache**: Server nicht erreichbar
- **Lösung**: URL und Firewall überprüfen

### Authentifizierung fehlgeschlagen
- **Ursache**: Token ungültig
- **Lösung**: Neuen Token in ChirpStack generieren

### Spalte nicht gefunden
- **Ursache**: Erforderliche Spalte fehlt
- **Lösung**: Spaltennamen überprüfen (case-sensitiv)

### Falsche Keys registriert
- **Ursache**: Falsche LoRaWAN-Version ausgewählt
- **Lösung**: Richtige Version in ChirpStack Device Profiles prüfen

### gRPC-Fehler
- **Ursache**: Ungültige Profile-ID oder fehlende Berechtigungen
- **Lösung**: Profile-IDs und Berechtigungen überprüfen

---

## 📥 Entwicklungs-Setup

\\\ash
# Virtuelle Umgebung erstellen
python -m venv venv

# Aktivieren (Windows)
venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Entwicklungsserver starten
python app.py
\\\

Anwendung verfügbar auf http://localhost:5000

### PyInstaller EXE erstellen

\\\ash
# PyInstaller installieren
pip install pyinstaller

# EXE bauen
pyinstaller app.spec

# Ergebnis: dist/LoRaWAN_Device_Registration/
\\\

---

## 📊 Versionshistorie

### v1.2.0 (Februar 2026)
- LoRaWAN Version Selector auf Registrierungsseite
- Automatische Key-Zuordnung basierend auf LoRaWAN-Version
- Verbesserte Fehlerbehandlung
- Redundanten Code entfernt
- Umfassende Dokumentation

### v1.1.0 (Februar 2026)
- gRPC-Integration mit ChirpStack
- Multi-Format Datei-Unterstützung
- Echtzeit-Fortschrittsanzeige
- Konfigurationsverlauf

### v1.0.0 (Januar 2026)
- Initiale Veröffentlichung

---

**Zuletzt aktualisiert**: Februar 20, 2026
**Version**: v1.2.0
