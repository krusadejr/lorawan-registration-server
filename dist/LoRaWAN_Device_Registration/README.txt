====================================================================
  LoRaWAN Device Registration Application - Standalone Version
====================================================================

VERSION: 1.0.0
DATE: November 17, 2025

====================================================================
QUICK START / SCHNELLSTART
====================================================================

ENGLISH:
1. Double-click "START_APPLICATION.bat" (NOT the .exe file!)
2. Wait 10-15 seconds for the server to start
3. Open your web browser and go to: http://localhost:5000
4. Configure your ChirpStack server settings
5. Upload and register your devices!

HINWEIS: Wenn Windows eine Sicherheitsmeldung anzeigt, klicken Sie auf "Trotzdem ausführen"
(If Windows shows a security dialog, click through it)

--------------------------------------------------------------------

DEUTSCH:
1. Doppelklick auf "START_APPLICATION.bat" (NICHT auf die .exe Datei!)
2. Warten Sie 10-15 Sekunden, bis der Server startet
3. Öffnen Sie Ihren Webbrowser und gehen Sie zu: http://localhost:5000
4. Konfigurieren Sie Ihre ChirpStack-Server-Einstellungen
5. Laden Sie Ihre Geräte hoch und registrieren Sie sie!

HINWEIS: Wenn Windows eine Sicherheitsmeldung anzeigt, klicken Sie auf "Trotzdem ausführen"

====================================================================
SYSTEM REQUIREMENTS / SYSTEMANFORDERUNGEN
====================================================================

- Windows 10 or later / Windows 10 oder neuer
- ChirpStack server accessible via network / ChirpStack-Server über Netzwerk erreichbar
- Port 5000 must be available / Port 5000 muss verfügbar sein
- Minimum 500 MB free disk space / Mindestens 500 MB freier Speicherplatz

====================================================================
FEATURES / FUNKTIONEN
====================================================================

✓ Upload Excel, JSON, or TXT files / Excel-, JSON- oder TXT-Dateien hochladen
✓ Flexible column mapping / Flexible Spaltenzuordnung
✓ Bulk device registration / Massenregistrierung von Geräten
✓ Per-device profile configuration / Gerätespezifische Profilkonfiguration
✓ Device management / Geräteverwaltung
✓ Real-time progress tracking / Echtzeit-Fortschrittsverfolgung

====================================================================
IMPORTANT NOTES / WICHTIGE HINWEISE
====================================================================

⚠ The first startup may take 10-15 seconds while files are extracted
   Der erste Start kann 10-15 Sekunden dauern, während Dateien extrahiert werden

⚠ Keep the console window open - closing it will stop the application
   Lassen Sie das Konsolenfenster offen - das Schließen stoppt die Anwendung

⚠ To stop the application, press CTRL+C in the console window or close it
   Um die Anwendung zu stoppen, drücken Sie STRG+C im Konsolenfenster oder schließen Sie es

⚠ Your antivirus may flag this as unknown software - this is a false positive
   Ihr Antivirusprogramm könnte dies als unbekannte Software markieren - das ist ein Fehlalarm

====================================================================
TROUBLESHOOTING / FEHLERBEHEBUNG
====================================================================

Problem: Application won't start / Anwendung startet nicht
Solution: Check if port 5000 is already in use by another application
Lösung: Überprüfen Sie, ob Port 5000 bereits von einer anderen Anwendung verwendet wird

Problem: "Application is not trusted" warning / "Anwendung ist nicht vertrauenswürdig" Warnung
Solution: Click "More info" → "Run anyway" (this is a false positive)
Lösung: Klicken Sie auf "Weitere Informationen" → "Trotzdem ausführen" (dies ist ein Fehlalarm)

Problem: Can't connect to ChirpStack / Keine Verbindung zu ChirpStack
Solution: Verify your ChirpStack server URL (use port 8080 for gRPC API)
Lösung: Überprüfen Sie Ihre ChirpStack-Server-URL (verwenden Sie Port 8080 für die gRPC-API)

Problem: Slow startup / Langsamer Start
Solution: This is normal for the first run - subsequent starts will be faster
Lösung: Dies ist beim ersten Start normal - nachfolgende Starts sind schneller

====================================================================
CONFIGURATION / KONFIGURATION
====================================================================

Required Settings in Web Interface / Erforderliche Einstellungen in der Web-Oberfläche:

1. ChirpStack Server URL (e.g., localhost:8080)
2. API Key (JWT token from ChirpStack)
3. Tenant ID (UUID from ChirpStack)

These are saved between sessions / Diese werden zwischen den Sitzungen gespeichert

====================================================================
FILE FORMATS SUPPORTED / UNTERSTÜTZTE DATEIFORMATE
====================================================================

✓ Excel: .xlsx, .xls, .xlsm
✓ JSON: .json
✓ Text: .txt (tab or comma-separated / Tab- oder Komma-getrennt)

Required Fields / Erforderliche Felder:
- DevEUI (16 hex characters / 16 Hexadezimalzeichen)
- Name
- Application_ID (UUID)
- Device_Profile_ID (UUID)
- NwkKey (32 hex characters / 32 Hexadezimalzeichen)

Optional Fields / Optionale Felder:
- AppKey (32 hex characters / 32 Hexadezimalzeichen)
- Description

====================================================================
SUPPORT / UNTERSTÜTZUNG
====================================================================

For issues, questions, or contributions:
Für Probleme, Fragen oder Beiträge:

GitHub: https://github.com/krusadejr/lorawan-registration-server
Documentation: See README.md in the repository
Dokumentation: Siehe README.md im Repository

====================================================================
LICENSE / LIZENZ
====================================================================

This application is provided as-is for ChirpStack device management.
Diese Anwendung wird wie besehen für die ChirpStack-Geräteverwaltung bereitgestellt.

====================================================================
                    © 2025 - LoRaWAN Device Registration
====================================================================
