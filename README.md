# LoRaWAN Device Registration Server

A Flask web application for bulk registration of LoRaWAN devices to ChirpStack server using gRPC API.

## 🚀 Quick Start

**No Python installation required!** Download the ready-to-use Windows executable from the [Releases](https://github.com/krusadejr/lorawan-registration-server/releases) page.

### For End Users
1. Download `LoRaWAN_Device_Registration.zip` from the latest release
2. Extract and run `START_APPLICATION.bat`
3. Open http://localhost:5000
4. Configure ChirpStack settings and start registering devices!

### For Developers
See [Documentations/README.md](Documentations/README.md) for detailed setup instructions.

---

## 📚 Documentation

All documentation is organized in the `Documentations/` folder:

- **[README.md](Documentations/README.md)** - Full project documentation (English/German)
- **[QUICK_START.md](Documentations/QUICK_START.md)** - Quick reference guide
- **[FOLDER_STRUCTURE.md](Documentations/FOLDER_STRUCTURE.md)** - Project structure explanation
- **[IMPLEMENTATION_PLAN.md](Documentations/IMPLEMENTATION_PLAN.md)** - Technical implementation details
- **[OPTIMIZATIONS.md](Documentations/OPTIMIZATIONS.md)** - Performance optimization notes

---

## ✨ Features

- Multi-format file support (Excel, CSV, JSON, TXT)
- Automatic CSV delimiter detection
- Flexible column mapping
- Bulk device registration with real-time progress
- Configuration history with autocomplete
- Modern dark UI with responsive design

---

## 🛠️ Technology Stack

- **Backend**: Python 3.13.4, Flask
- **Communication**: gRPC, Protocol Buffers
- **Data Processing**: pandas, openpyxl
- **Frontend**: Bulma CSS, JavaScript
- **Distribution**: PyInstaller (standalone executable)

---

## 📁 Project Structure

```
.
├── app.py                 # Main Flask application
├── file_parser.py         # Multi-format file parsing
├── grpc_client.py         # ChirpStack gRPC client
├── Documentations/        # All project documentation
├── templates/             # HTML templates
├── static/                # CSS, icons, styles
├── generated/             # gRPC protocol buffers
├── PRIVATE/               # Local-only files (not tracked)
└── dist/                  # Standalone executable
```

For detailed folder information, see [FOLDER_STRUCTURE.md](Documentations/FOLDER_STRUCTURE.md).

---

## 🔧 Development Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

For more details, see [Documentations/README.md](Documentations/README.md).

---

## 📊 Repository Structure

- **main** branch - Production-ready code
- **PRIVATE/** folder - Local development files (not tracked)
- **Documentations/** - All project documentation

---

## 📝 License

[Specify license type]

---

## 👤 Author

[Your Name/Organization]

---

**Last Updated**: January 21, 2026
