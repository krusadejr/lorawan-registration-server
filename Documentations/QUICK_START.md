# Quick Start Guide

## Starting the Application

Simply double-click on **`start_app.bat`** to launch the web application.

The application will:
1. Activate the Python virtual environment automatically
2. Start the Flask web server
3. Open on `http://localhost:5000`

**Note:** Keep the terminal window open while using the application. To stop the server, press `Ctrl+C` in the terminal window.

## First Time Setup

If this is your first time running the application:

1. Make sure Python 3.x is installed
2. Install dependencies (one-time only):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

After that, just use `start_app.bat` for easy startup!

## Troubleshooting

**If you see "Could not activate virtual environment":**
- Run the first-time setup commands above
- Make sure the `venv` folder exists

**If you see port errors:**
- Make sure port 5000 is not already in use
- Close any other instance of the application
