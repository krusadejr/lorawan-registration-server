# Excel File Preview Web Application

A simple Flask web application that allows users to upload Excel files and preview their contents. Built with Python Flask and Bulma CSS framework.

## Features

- Upload Excel files (.xlsx, .xls)
- Preview Excel data in a clean, responsive table
- Modern UI using Bulma CSS framework
- Easy to deploy and customize

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
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

### 4. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

1. Open your browser and navigate to `http://localhost:5000`
2. Click on "Choose file" to select an Excel file (.xlsx or .xls)
3. Click "Upload and Preview" button
4. View the preview of your Excel data in a table format

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
