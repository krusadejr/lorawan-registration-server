# LoRaWAN Device Registration Server

Eine Flask-Webanwendung zur Massenregistrierung von LoRaWAN-Geräten auf einem ChirpStack-Server mit gRPC-API.

## Schnellstart

Keine Python-Installation erforderlich! Laden Sie die vorkonfigurierte Windows-Anwendung aus der [Releases](https://github.com/krusadejr/lorawan-registration-server/releases) Seite herunter.

### Für Endbenutzer
1. Laden Sie `LoRaWAN_Device_Registration.zip` aus der neuesten Version herunter
2. Extrahieren und führen Sie `START_APPLICATION.bat` aus
3. Öffnen Sie http://localhost:5000
4. Konfigurieren Sie die ChirpStack-Einstellungen und beginnen Sie mit der Registrierung von Geräten

### Für Entwickler
Weitere Informationen finden Sie unter [Documentations/README.md](Documentations/README.md).

---

## Dokumentation

Die gesamte Dokumentation ist im Ordner `Documentations/` organisiert:

- [README.md](Documentations/README.md) - Vollständige Projektdokumentation
- [QUICK_START.md](Documentations/QUICK_START.md) - Schnellreferenz
- [FOLDER_STRUCTURE.md](Documentations/FOLDER_STRUCTURE.md) - Projektstruktur Erklärung
- [IMPLEMENTATION_PLAN.md](Documentations/IMPLEMENTATION_PLAN.md) - Technische Implementierungsdetails
- [OPTIMIZATIONS.md](Documentations/OPTIMIZATIONS.md) - Performance-Optimierungsnoten

---

## Funktionen

- Unterstützung mehrerer Dateiformate (Excel, CSV, JSON, TXT)
- Automatische CSV-Trennzeichen-Erkennung
- Flexible Spaltenzuordnung
- Massenregistrierung von Geräten mit Echtzeitfortschritt
- Konfigurationsverlauf mit Autovervollständigung
- Modernes dunkles Design mit responsiver Benutzeroberfläche

---

## Technologie-Stack

- Backend: Python 3.13.4, Flask
- Kommunikation: gRPC, Protocol Buffers
- Datenverarbeitung: pandas, openpyxl
- Frontend: Bulma CSS, JavaScript
- Distribution: PyInstaller (eigenständige Anwendung)

---

## Projektstruktur

```
.
├── app.py                 # Haupt-Flask-Anwendung
├── file_parser.py         # Multi-Format-Datei-Analyse
├── grpc_client.py         # ChirpStack gRPC-Client
├── Documentations/        # Gesamte Projektdokumentation
├── templates/             # HTML-Vorlagen
├── static/                # CSS, Icons, Stile
├── generated/             # gRPC-Protokoll-Buffer
├── PRIVATE/               # Lokale Dateien (nicht verfolgbar)
└── dist/                  # Eigenständige ausführbare Datei
```

Weitere Informationen zur Ordnerstruktur finden Sie unter [FOLDER_STRUCTURE.md](Documentations/FOLDER_STRUCTURE.md).

---

## Entwicklungs-Setup

```bash
# Virtuelle Umgebung erstellen
python -m venv venv

# Aktivieren (Windows)
venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Entwicklungsserver ausführen
python app.py
```

Weitere Details finden Sie unter [Documentations/README.md](Documentations/README.md).

---

## Repository-Struktur

- **main** Branch - Produktionsreifer Code
- **PRIVATE/** Ordner - Lokale Entwicklungsdateien (nicht verfolgbar)
- **Documentations/** - Gesamte Projektdokumentation

---

## Autor

Ayush Kumar

---

## Anmerkung

Dieses Projekt wurde als Abschlussarbeit des Master-Studiengangs Wirtschaftsinformatik an der Technischen Hochschule Brandenburg entwickelt.

---

Zuletzt aktualisiert: Februar 9, 2026
