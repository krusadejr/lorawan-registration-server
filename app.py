import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, stream_with_context, send_file
import pandas as pd
from werkzeug.utils import secure_filename
import uuid
import json
import logging
from datetime import datetime
from file_parser import parse_file, get_column_info
import time
import io

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Configuration
UPLOAD_FOLDER = 'uploads'
LOG_FOLDER = 'logs'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'xlsm', 'txt', 'json'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

# Setup logging
log_filename = os.path.join(LOG_FOLDER, f'app_{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()  # Also print to console
    ]
)
logger = logging.getLogger(__name__)
logger.info("="*80)
logger.info("Application started")
logger.info("="*80)

# Global variables to store server configuration
SERVER_URL = None               # ChirpStack server URL
API_CODE = None                 # API key for authentication
TENANT_ID = None                # Tenant ID
DEFAULT_DEVICE_PROFILE_ID = None  # Default Device Profile ID (UUID)


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page with file upload form."""
    global SERVER_URL, API_CODE, TENANT_ID, DEFAULT_DEVICE_PROFILE_ID
    return render_template('index.html', 
                         server_url=SERVER_URL,
                         api_code=API_CODE,
                         tenant_id=TENANT_ID,
                         device_profile_id=DEFAULT_DEVICE_PROFILE_ID)


@app.route('/server-config')
def server_config():
    """Server configuration page."""
    global SERVER_URL, API_CODE, TENANT_ID, DEFAULT_DEVICE_PROFILE_ID
    return render_template('server_config.html', 
                         server_url=SERVER_URL, 
                         api_code=API_CODE,
                         tenant_id=TENANT_ID,
                         device_profile_id=DEFAULT_DEVICE_PROFILE_ID)


@app.route('/save-server-config', methods=['POST'])
def save_server_config():
    """Save server configuration to global variables."""
    global SERVER_URL, API_CODE, TENANT_ID, DEFAULT_DEVICE_PROFILE_ID
    
    server_url = request.form.get('server_url', '').strip()
    api_code = request.form.get('api_code', '').strip()
    tenant_id = request.form.get('tenant_id', '').strip()
    device_profile_id = request.form.get('device_profile_id', '').strip()
    
    if not any([server_url, api_code, tenant_id, device_profile_id]):
        flash('Bitte geben Sie mindestens einen Wert ein', 'danger')
        return redirect(url_for('server_config'))
    
    saved_vars = []
    
    if server_url:
        SERVER_URL = server_url
        saved_vars.append('SERVER_URL')
    
    if api_code:
        API_CODE = api_code
        saved_vars.append('API_CODE')
    
    if tenant_id:
        TENANT_ID = tenant_id
        saved_vars.append('TENANT_ID')
    
    if device_profile_id:
        DEFAULT_DEVICE_PROFILE_ID = device_profile_id
        saved_vars.append('DEFAULT_DEVICE_PROFILE_ID')
    
    flash(f'Server-Konfiguration erfolgreich gespeichert: {", ".join(saved_vars)}', 'success')
    
    # Redirect to index with a prompt to upload file
    flash('✓ Server konfiguriert! Sie können jetzt Geräte-Dateien hochladen.', 'info')
    return redirect(url_for('index'))


@app.route('/test-connection')
def test_connection():
    """Test connection to ChirpStack server."""
    global SERVER_URL, API_CODE
    
    logger.info("="*80)
    logger.info("TEST CONNECTION REQUEST")
    logger.info("="*80)
    
    # Check if server is configured
    if not SERVER_URL or not API_CODE:
        logger.warning("Server not configured")
        return render_template('test_connection.html', 
                             configured=False,
                             server_url=SERVER_URL,
                             api_code=API_CODE)
    
    logger.info(f"Testing connection to: {SERVER_URL}")
    
    # Try to connect
    connection_result = {
        'success': False,
        'message': '',
        'details': []
    }
    
    try:
        from grpc_client import ChirpStackClient
        
        # Create client
        client = ChirpStackClient(SERVER_URL, API_CODE)
        connection_result['details'].append('✓ Client erstellt')
        
        # Test connection
        connected, conn_msg = client.connect()
        connection_result['details'].append(f'Verbindungsversuch: {conn_msg}')
        
        if connected:
            connection_result['success'] = True
            connection_result['message'] = 'Erfolgreich mit ChirpStack verbunden!'
            logger.info("Connection test successful")
        else:
            connection_result['message'] = f'Verbindung fehlgeschlagen: {conn_msg}'
            logger.error(f"Connection test failed: {conn_msg}")
        
        # Close connection
        client.close()
        
    except ImportError as e:
        connection_result['message'] = f'gRPC Client konnte nicht geladen werden: {str(e)}'
        connection_result['details'].append(f'✗ Import-Fehler: {str(e)}')
        logger.error(f"Import error: {e}")
    except Exception as e:
        connection_result['message'] = f'Fehler beim Verbindungstest: {str(e)}'
        connection_result['details'].append(f'✗ Fehler: {str(e)}')
        logger.error(f"Connection test error: {e}", exc_info=True)
    
    return render_template('test_connection.html',
                         configured=True,
                         server_url=SERVER_URL,
                         api_code=API_CODE,
                         result=connection_result)


@app.route('/help')
def help_page():
    """Help page with instructions for getting ChirpStack IDs."""
    return render_template('help.html')


@app.route('/download-template')
def download_template():
    """Download Excel template with correct column headers."""
    logger.info("Template download requested")
    
    global DEFAULT_DEVICE_PROFILE_ID
    
    # Create template DataFrame with example data
    template_data = {
        'dev_eui': ['0004A30B001A2B3C', '0004A30B001A2B3D'],
        'name': ['Example Device 1', 'Example Device 2'],
        'application_id': ['79538b65-4bf1-47cb-80bb-5019090adadb', '79538b65-4bf1-47cb-80bb-5019090adadb'],
        'device_profile_id': [
            DEFAULT_DEVICE_PROFILE_ID if DEFAULT_DEVICE_PROFILE_ID else '728e257b-1f8e-4826-8929-6dd18adfd97e',
            DEFAULT_DEVICE_PROFILE_ID if DEFAULT_DEVICE_PROFILE_ID else '728e257b-1f8e-4826-8929-6dd18adfd97e'
        ],
        'nwk_key': ['00112233445566778899AABBCCDDEEF0', 'FFEEDDCCBBAA99887766554433221100'],
        'app_key': ['FFEEDDCCBBAA99887766554433221100', '00112233445566778899AABBCCDDEEF0'],
        'description': ['Temperature sensor in warehouse A', 'Humidity sensor in warehouse B']
    }
    
    df = pd.DataFrame(template_data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Devices', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Devices']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='device_registration_template.xlsx'
    )


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and parse data."""
    logger.info("="*80)
    logger.info("UPLOAD FILE REQUEST")
    logger.info("="*80)
    
    # Check if file is present in request
    if 'file' not in request.files:
        logger.warning("No file in request")
        flash('Keine Datei in der Anfrage', 'danger')
        return redirect(url_for('index'))
    
    file = request.files['file']
    logger.info(f"File received: {file.filename}")
    
    # Check if user selected a file
    if file.filename == '':
        logger.warning("Empty filename")
        flash('Keine Datei ausgewählt', 'danger')
        return redirect(url_for('index'))
    
    # Check if file is allowed
    if file and allowed_file(file.filename):
        # Generate unique filename to avoid conflicts
        unique_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{unique_id}.{file_extension}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        logger.info(f"Saving file to: {filepath}")
        file.save(filepath)
        
        try:
            # Parse file using our parser
            logger.info(f"Parsing file with extension: {file_extension}")
            parse_result = parse_file(filepath, file_extension)
            
            logger.info(f"Parse result success: {parse_result['success']}")
            logger.info(f"Parse result message: {parse_result['message']}")
            
            if not parse_result['success']:
                flash(parse_result['message'], 'danger')
                if os.path.exists(filepath):
                    os.remove(filepath)
                return redirect(url_for('index'))
            
            logger.info(f"Number of sheets: {len(parse_result['sheets'])}")
            logger.info(f"Sheet names: {parse_result['sheets']}")
            
            # Store in session - only metadata, not the actual data
            session['filepath'] = filepath
            session['original_filename'] = original_filename
            session['file_type'] = parse_result['file_type']
            session['sheet_names'] = list(parse_result['sheets'])  # Ensure it's a list
            
            # Save parsed data to a temporary JSON file instead of session
            parsed_data_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_parsed.json")
            session_data = {}
            for sheet_name, df in parse_result['data'].items():
                session_data[sheet_name] = df.to_dict(orient='records')
                logger.info(f"Sheet '{sheet_name}': {len(df)} rows, {len(df.columns)} columns")
            
            logger.info(f"Writing parsed data to: {parsed_data_file}")
            with open(parsed_data_file, 'w') as f:
                json.dump(session_data, f)
            
            session['parsed_data_file'] = parsed_data_file
            
            # Log session state
            logger.info(f"Session stored - sheet_names: {session.get('sheet_names')}")
            logger.info(f"Session stored - parsed_data_file: {parsed_data_file}")
            logger.info(f"Session stored - filepath: {filepath}")
            logger.info(f"File exists check: {os.path.exists(parsed_data_file)}")
            
            flash(parse_result['message'], 'success')
            
            # Redirect to sheet selection page
            logger.info("Redirecting to select_sheet")
            return redirect(url_for('select_sheet'))
        
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}", exc_info=True)
            flash(f'Fehler beim Verarbeiten der Datei: {str(e)}', 'danger')
            # Clean up file if error occurs
            if os.path.exists(filepath):
                os.remove(filepath)
            return redirect(url_for('index'))
    
    else:
        logger.warning(f"Invalid file type: {file.filename}")
        flash('Ungültiger Dateityp. Bitte laden Sie eine gültige Datei hoch (.xlsx, .xls, .xlsm, .txt, .json)', 'danger')
        return redirect(url_for('index'))


@app.route('/select-sheet')
def select_sheet():
    """Sheet selection page."""
    logger.info("="*80)
    logger.info("SELECT SHEET REQUEST")
    logger.info("="*80)
    
    sheet_names = session.get('sheet_names', [])
    original_filename = session.get('original_filename', '')
    file_type = session.get('file_type', '')
    parsed_data_file = session.get('parsed_data_file', '')
    
    logger.info(f"Session sheet_names: {sheet_names}")
    logger.info(f"Session original_filename: {original_filename}")
    logger.info(f"Session file_type: {file_type}")
    logger.info(f"Session parsed_data_file: {parsed_data_file}")
    logger.info(f"All session keys: {list(session.keys())}")
    
    if parsed_data_file:
        file_exists = os.path.exists(parsed_data_file)
        logger.info(f"Parsed data file exists: {file_exists}")
    else:
        logger.warning("No parsed_data_file in session")
    
    if not sheet_names or not parsed_data_file or not os.path.exists(parsed_data_file):
        logger.error("Missing data - redirecting to index")
        logger.error(f"  sheet_names empty: {not sheet_names}")
        logger.error(f"  parsed_data_file empty: {not parsed_data_file}")
        logger.error(f"  file exists: {os.path.exists(parsed_data_file) if parsed_data_file else False}")
        flash('Keine Daten gefunden. Bitte laden Sie die Datei erneut hoch.', 'danger')
        return redirect(url_for('index'))
    
    # Read parsed data from file
    logger.info(f"Reading parsed data from: {parsed_data_file}")
    with open(parsed_data_file, 'r') as f:
        parsed_data = json.load(f)
    
    logger.info(f"Parsed data contains sheets: {list(parsed_data.keys())}")
    
    # Get preview data for each sheet
    sheet_previews = {}
    
    for sheet_name in sheet_names:
        if sheet_name in parsed_data:
            df = pd.DataFrame(parsed_data[sheet_name])
            logger.info(f"Creating preview for sheet '{sheet_name}': {len(df)} rows, {len(df.columns)} cols")
            sheet_previews[sheet_name] = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'preview_html': df.head(5).to_html(
                    classes='table is-bordered is-striped is-hoverable is-fullwidth',
                    index=False,
                    na_rep='N/A'
                )
            }
        else:
            logger.warning(f"Sheet '{sheet_name}' not found in parsed data")
    
    return render_template('select_sheet.html',
                         filename=original_filename,
                         file_type=file_type,
                         sheet_names=sheet_names,
                         sheet_previews=sheet_previews)


@app.route('/column-mapping', methods=['POST'])
def column_mapping():
    """Handle column mapping for device registration."""
    logger.info("="*80)
    logger.info("COLUMN MAPPING REQUEST")
    logger.info("="*80)
    
    selected_sheet = request.form.get('selected_sheet')
    logger.info(f"Selected sheet from form: {selected_sheet}")
    
    if not selected_sheet:
        logger.warning("No sheet selected")
        flash('Bitte wählen Sie ein Sheet aus', 'danger')
        return redirect(url_for('index'))
    
    # Store selected sheet in session
    session['selected_sheet'] = selected_sheet
    logger.info(f"Stored selected_sheet in session: {selected_sheet}")
    
    # Get the parsed data file from session
    parsed_data_file = session.get('parsed_data_file', '')
    original_filename = session.get('original_filename', '')
    logger.info(f"Parsed data file from session: {parsed_data_file}")
    
    if not parsed_data_file or not os.path.exists(parsed_data_file):
        logger.error("Parsed data file not found")
        flash('Keine Daten gefunden. Bitte laden Sie die Datei erneut hoch.', 'danger')
        return redirect(url_for('index'))
    
    # Read parsed data from file
    logger.info("Reading parsed data from file")
    with open(parsed_data_file, 'r') as f:
        parsed_data = json.load(f)
    
    logger.info(f"Available sheets in parsed data: {list(parsed_data.keys())}")
    
    # Get the selected sheet data
    if selected_sheet not in parsed_data:
        logger.error(f"Selected sheet '{selected_sheet}' not found in parsed data")
        flash('Sheet nicht gefunden', 'danger')
        return redirect(url_for('index'))
    
    # Get column names and preview
    df = pd.DataFrame(parsed_data[selected_sheet])
    columns = list(df.columns)
    logger.info(f"Sheet columns: {columns}")
    logger.info(f"Sheet has {len(df)} rows")
    
    # Generate preview HTML
    preview_html = df.head(5).to_html(
        classes='table is-bordered is-striped is-hoverable is-fullwidth',
        index=False,
        na_rep='N/A'
    )
    
    logger.info("Rendering column_mapping.html template")
    return render_template('column_mapping.html',
                         filename=original_filename,
                         selected_sheet=selected_sheet,
                         columns=columns,
                         row_count=len(df),
                         preview_html=preview_html)


@app.route('/process-mapping', methods=['POST'])
def process_mapping():
    """Process the column mapping and prepare for device registration."""
    logger.info("="*80)
    logger.info("PROCESS MAPPING REQUEST")
    logger.info("="*80)
    
    # Get column mappings from form
    column_mapping = {
        'dev_eui': request.form.get('dev_eui'),
        'name': request.form.get('name'),
        'application_id': request.form.get('application_id'),
        'device_profile_id': request.form.get('device_profile_id'),
        'nwk_key': request.form.get('nwk_key'),
        'app_key': request.form.get('app_key', ''),  # Optional
        'description': request.form.get('description', '')  # Optional
    }
    
    logger.info(f"Column mapping received: {column_mapping}")
    
    # Validate required fields
    required_fields = ['dev_eui', 'name', 'application_id', 'device_profile_id', 'nwk_key']
    missing_fields = [field for field in required_fields if not column_mapping[field]]
    
    if missing_fields:
        logger.error(f"Missing required fields: {missing_fields}")
        flash(f'Bitte ordnen Sie alle erforderlichen Felder zu: {", ".join(missing_fields)}', 'danger')
        return redirect(url_for('column_mapping'))
    
    # Store mapping in session
    session['column_mapping'] = column_mapping
    logger.info("Column mapping stored in session")
    
    # Redirect to registration preview page
    logger.info("Redirecting to registration preview")
    return redirect(url_for('registration_preview'))


@app.route('/registration-preview')
def registration_preview():
    """Show preview of devices to be registered."""
    logger.info("="*80)
    logger.info("REGISTRATION PREVIEW REQUEST")
    logger.info("="*80)
    
    # Get all required data from session
    parsed_data_file = session.get('parsed_data_file', '')
    selected_sheet = session.get('selected_sheet', '')
    column_mapping = session.get('column_mapping', {})
    original_filename = session.get('original_filename', '')
    
    logger.info(f"Selected sheet: {selected_sheet}")
    logger.info(f"Column mapping: {column_mapping}")
    
    # Validate we have all necessary data
    if not parsed_data_file or not selected_sheet or not column_mapping:
        logger.error("Missing required session data")
        flash('Session-Daten fehlen. Bitte starten Sie den Prozess erneut.', 'danger')
        return redirect(url_for('index'))
    
    if not os.path.exists(parsed_data_file):
        logger.error(f"Parsed data file not found: {parsed_data_file}")
        flash('Datei nicht gefunden. Bitte laden Sie die Datei erneut hoch.', 'danger')
        return redirect(url_for('index'))
    
    # Read parsed data
    with open(parsed_data_file, 'r') as f:
        parsed_data = json.load(f)
    
    if selected_sheet not in parsed_data:
        logger.error(f"Sheet '{selected_sheet}' not found in parsed data")
        flash('Sheet nicht gefunden.', 'danger')
        return redirect(url_for('index'))
    
    # Load data into DataFrame
    df = pd.DataFrame(parsed_data[selected_sheet])
    logger.info(f"Loaded {len(df)} devices from sheet")
    
    # Map columns to device fields
    mapped_devices = []
    for idx, row in df.iterrows():
        device = {
            'dev_eui': str(row[column_mapping['dev_eui']]) if column_mapping['dev_eui'] else '',
            'name': str(row[column_mapping['name']]) if column_mapping['name'] else '',
            'application_id': str(row[column_mapping['application_id']]) if column_mapping['application_id'] else '',
            'device_profile_id': str(row[column_mapping['device_profile_id']]) if column_mapping['device_profile_id'] else '',
            'nwk_key': str(row[column_mapping['nwk_key']]) if column_mapping['nwk_key'] else '',
            'app_key': str(row[column_mapping['app_key']]) if column_mapping.get('app_key') and column_mapping['app_key'] else '',
            'description': str(row[column_mapping['description']]) if column_mapping.get('description') and column_mapping['description'] else ''
        }
        mapped_devices.append(device)
    
    logger.info(f"Mapped {len(mapped_devices)} devices successfully")
    
    # Create preview DataFrame
    preview_df = pd.DataFrame(mapped_devices)
    preview_html = preview_df.head(10).to_html(
        classes='table is-bordered is-striped is-hoverable is-fullwidth',
        index=False,
        na_rep='N/A'
    )
    
    # Check server configuration
    server_configured = bool(SERVER_URL and API_CODE and TENANT_ID)
    logger.info(f"Server configured: {server_configured}")
    
    return render_template('registration_preview.html',
                         filename=original_filename,
                         device_count=len(mapped_devices),
                         preview_html=preview_html,
                         server_configured=server_configured,
                         server_url=SERVER_URL,
                         tenant_id=TENANT_ID)


@app.route('/start-registration', methods=['POST'])
def start_registration():
    """Start registration process - shows progress page"""
    # Store duplicate action in session
    duplicate_action = request.form.get('duplicate_action', 'skip')
    session['duplicate_action'] = duplicate_action
    
    return render_template('registration_progress.html', duplicate_action=duplicate_action)


@app.route('/register-devices-stream', methods=['POST'])
def register_devices_stream():
    """Stream device registration progress in real-time using SSE."""
    
    def generate():
        """Generator function for Server-Sent Events"""
        try:
            # Get duplicate action from session (set in start_registration)
            duplicate_action = session.get('duplicate_action', 'skip')
            logger.info(f"Streaming registration with duplicate_action: {duplicate_action}")
            
            # Get data from session
            parsed_data_file = session.get('parsed_data_file', '')
            selected_sheet = session.get('selected_sheet', '')
            column_mapping = session.get('column_mapping', {})
            
            if not parsed_data_file or not os.path.exists(parsed_data_file):
                yield f"data: {json.dumps({'error': 'Session data missing'})}\n\n"
                return
            
            # Read parsed data
            with open(parsed_data_file, 'r') as f:
                parsed_data = json.load(f)
            
            df = pd.DataFrame(parsed_data[selected_sheet])
            
            # Map columns to device fields
            devices_to_register = []
            for idx, row in df.iterrows():
                device = {
                    'dev_eui': str(row[column_mapping['dev_eui']]).strip(),
                    'name': str(row[column_mapping['name']]).strip(),
                    'application_id': str(row[column_mapping['application_id']]).strip(),
                    'device_profile_id': str(row[column_mapping['device_profile_id']]).strip(),
                    'nwk_key': str(row[column_mapping['nwk_key']]).strip(),
                    'app_key': str(row[column_mapping['app_key']]).strip() if column_mapping.get('app_key') and column_mapping['app_key'] else '',
                    'description': str(row[column_mapping['description']]).strip() if column_mapping.get('description') and column_mapping['description'] else ''
                }
                devices_to_register.append(device)
            
            total = len(devices_to_register)
            
            # Send initial status
            yield f"data: {json.dumps({'status': 'starting', 'total': total, 'current': 0})}\n\n"
            
            # Create gRPC client
            from grpc_client import ChirpStackClient
            client = ChirpStackClient(SERVER_URL, API_CODE)
            connected, conn_msg = client.connect()
            
            if not connected:
                yield f"data: {json.dumps({'error': f'Connection failed: {conn_msg}'})}\n\n"
                return
            
            results = {'successful': [], 'failed': []}
            
            # Register each device
            for idx, device in enumerate(devices_to_register, 1):
                try:
                    # Check if device exists
                    device_exists = client.device_exists(device['dev_eui'])
                    
                    logger.info(f"Device {device['dev_eui']}: exists={device_exists}, duplicate_action={duplicate_action}")
                    
                    if device_exists:
                        if duplicate_action == 'skip':
                            logger.info(f"Skipping existing device {device['dev_eui']}")
                            results['failed'].append({
                                'dev_eui': device['dev_eui'],
                                'name': device['name'],
                                'error': 'Gerät existiert bereits (übersprungen)'
                            })
                            yield f"data: {json.dumps({'status': 'processing', 'current': idx, 'total': total, 'device': device['name'], 'result': 'skipped', 'message': 'Bereits vorhanden'})}\n\n"
                            continue
                        elif duplicate_action == 'replace':
                            logger.info(f"Attempting to replace device {device['dev_eui']}")
                            deleted, del_msg = client.delete_device(device['dev_eui'])
                            logger.info(f"Delete result: deleted={deleted}, msg={del_msg}")
                            if not deleted:
                                results['failed'].append({
                                    'dev_eui': device['dev_eui'],
                                    'name': device['name'],
                                    'error': f'Fehler beim Löschen: {del_msg}'
                                })
                                yield f"data: {json.dumps({'status': 'processing', 'current': idx, 'total': total, 'device': device['name'], 'result': 'failed', 'message': 'Löschen fehlgeschlagen'})}\n\n"
                                continue
                            else:
                                logger.info(f"Device {device['dev_eui']} deleted successfully, proceeding with creation")
                    
                    # Create device
                    device_created, create_msg = client.create_device(
                        dev_eui=device['dev_eui'],
                        name=device['name'],
                        application_id=device['application_id'],
                        device_profile_id=device['device_profile_id'],
                        description=device['description']
                    )
                    
                    if not device_created:
                        results['failed'].append({
                            'dev_eui': device['dev_eui'],
                            'name': device['name'],
                            'error': create_msg
                        })
                        yield f"data: {json.dumps({'status': 'processing', 'current': idx, 'total': total, 'device': device['name'], 'result': 'failed', 'message': create_msg[:50]})}\n\n"
                        continue
                    
                    # Set device keys
                    keys_set, keys_msg = client.create_device_keys(
                        dev_eui=device['dev_eui'],
                        nwk_key=device['nwk_key'],
                        app_key=device['app_key'] if device['app_key'] else None
                    )
                    
                    if not keys_set:
                        results['successful'].append({
                            'dev_eui': device['dev_eui'],
                            'name': device['name'],
                            'warning': f'Device created but keys not set: {keys_msg}'
                        })
                        yield f"data: {json.dumps({'status': 'processing', 'current': idx, 'total': total, 'device': device['name'], 'result': 'warning', 'message': 'Keys nicht gesetzt'})}\n\n"
                    else:
                        results['successful'].append({
                            'dev_eui': device['dev_eui'],
                            'name': device['name']
                        })
                        yield f"data: {json.dumps({'status': 'processing', 'current': idx, 'total': total, 'device': device['name'], 'result': 'success', 'message': 'Erfolgreich'})}\n\n"
                
                except Exception as e:
                    results['failed'].append({
                        'dev_eui': device['dev_eui'],
                        'name': device['name'],
                        'error': str(e)
                    })
                    yield f"data: {json.dumps({'status': 'processing', 'current': idx, 'total': total, 'device': device['name'], 'result': 'failed', 'message': str(e)[:50]})}\n\n"
            
            # Store results in session
            session['registration_results'] = results
            
            # Send completion
            yield f"data: {json.dumps({'status': 'complete', 'successful': len(results['successful']), 'failed': len(results['failed'])})}\n\n"
            
            client.close()
            
        except Exception as e:
            logger.error(f"Streaming error: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@app.route('/register-devices', methods=['POST'])
def register_devices():
    """Execute device registration via gRPC."""
    logger.info("="*80)
    logger.info("REGISTER DEVICES REQUEST - STARTING")
    logger.info("="*80)
    
    # Check server configuration
    if not SERVER_URL or not API_CODE or not TENANT_ID:
        logger.error("Server not configured")
        flash('Server ist nicht konfiguriert. Bitte konfigurieren Sie zuerst die Server-Verbindung.', 'danger')
        return redirect(url_for('server_config'))
    
    # Get all required data from session
    parsed_data_file = session.get('parsed_data_file', '')
    selected_sheet = session.get('selected_sheet', '')
    column_mapping = session.get('column_mapping', {})
    
    if not parsed_data_file or not selected_sheet or not column_mapping:
        logger.error("Missing session data")
        flash('Session-Daten fehlen. Bitte starten Sie den Prozess erneut.', 'danger')
        return redirect(url_for('index'))
    
    if not os.path.exists(parsed_data_file):
        logger.error(f"Parsed data file not found: {parsed_data_file}")
        flash('Datei nicht gefunden.', 'danger')
        return redirect(url_for('index'))
    
    # Read parsed data
    with open(parsed_data_file, 'r') as f:
        parsed_data = json.load(f)
    
    df = pd.DataFrame(parsed_data[selected_sheet])
    logger.info(f"Starting registration for {len(df)} devices")
    
    # Get duplicate handling action
    duplicate_action = request.form.get('duplicate_action', 'skip')  # 'skip' or 'replace'
    logger.info(f"Duplicate action: {duplicate_action}")
    
    # Map columns to device fields
    devices_to_register = []
    for idx, row in df.iterrows():
        device = {
            'dev_eui': str(row[column_mapping['dev_eui']]).strip(),
            'name': str(row[column_mapping['name']]).strip(),
            'application_id': str(row[column_mapping['application_id']]).strip(),
            'device_profile_id': str(row[column_mapping['device_profile_id']]).strip(),
            'nwk_key': str(row[column_mapping['nwk_key']]).strip(),
            'app_key': str(row[column_mapping['app_key']]).strip() if column_mapping.get('app_key') and column_mapping['app_key'] else '',
            'description': str(row[column_mapping['description']]).strip() if column_mapping.get('description') and column_mapping['description'] else ''
        }
        devices_to_register.append(device)
    
    # Initialize results tracking
    results = {
        'total': len(devices_to_register),
        'successful': [],
        'failed': []
    }
    
    # Import gRPC client
    try:
        from grpc_client import ChirpStackClient
        logger.info("Imported ChirpStackClient successfully")
    except ImportError as e:
        logger.error(f"Failed to import ChirpStackClient: {e}")
        flash('Fehler beim Laden des gRPC Clients.', 'danger')
        return redirect(url_for('registration_preview'))
    
    # Create gRPC client
    try:
        logger.info(f"Creating ChirpStack client for {SERVER_URL}")
        client = ChirpStackClient(SERVER_URL, API_CODE)
        logger.info("ChirpStack client created successfully")
        
        # Connect to ChirpStack
        connected, conn_msg = client.connect()
        if not connected:
            logger.error(f"Failed to connect to ChirpStack: {conn_msg}")
            flash(f'Fehler beim Verbinden mit ChirpStack: {conn_msg}', 'danger')
            return redirect(url_for('registration_preview'))
        logger.info(f"Connected to ChirpStack: {conn_msg}")
        
    except Exception as e:
        logger.error(f"Failed to create ChirpStack client: {e}", exc_info=True)
        flash(f'Fehler beim Verbinden mit ChirpStack: {str(e)}', 'danger')
        return redirect(url_for('registration_preview'))
    
    # Register each device
    for idx, device in enumerate(devices_to_register, 1):
        logger.info(f"Registering device {idx}/{len(devices_to_register)}: {device['name']} ({device['dev_eui']})")
        
        try:
            # Check if device already exists
            device_exists = client.device_exists(device['dev_eui'])
            
            if device_exists:
                logger.info(f"Device {device['dev_eui']} already exists")
                
                if duplicate_action == 'skip':
                    # Skip this device
                    logger.warning(f"Skipping existing device {device['dev_eui']}")
                    results['failed'].append({
                        'dev_eui': device['dev_eui'],
                        'name': device['name'],
                        'error': 'Gerät existiert bereits (übersprungen)'
                    })
                    continue
                    
                elif duplicate_action == 'replace':
                    # Delete existing device first
                    logger.info(f"Deleting existing device {device['dev_eui']} for replacement")
                    deleted, del_msg = client.delete_device(device['dev_eui'])
                    if not deleted:
                        logger.error(f"Failed to delete existing device {device['dev_eui']}: {del_msg}")
                        results['failed'].append({
                            'dev_eui': device['dev_eui'],
                            'name': device['name'],
                            'error': f'Fehler beim Löschen des existierenden Geräts: {del_msg}'
                        })
                        continue
                    logger.info(f"Existing device {device['dev_eui']} deleted successfully")
            
            # Create device
            device_created, create_msg = client.create_device(
                dev_eui=device['dev_eui'],
                name=device['name'],
                application_id=device['application_id'],
                device_profile_id=device['device_profile_id'],
                description=device['description']
            )
            
            if not device_created:
                logger.error(f"Failed to create device {device['name']}: {create_msg}")
                results['failed'].append({
                    'dev_eui': device['dev_eui'],
                    'name': device['name'],
                    'error': create_msg
                })
                continue
            
            logger.info(f"Device {device['name']} created successfully: {create_msg}")
            
            # Set device keys
            keys_set, keys_msg = client.create_device_keys(
                dev_eui=device['dev_eui'],
                nwk_key=device['nwk_key'],
                app_key=device['app_key'] if device['app_key'] else None
            )
            
            if not keys_set:
                logger.warning(f"Failed to set keys for device {device['name']}: {keys_msg}")
                results['successful'].append({
                    'dev_eui': device['dev_eui'],
                    'name': device['name'],
                    'warning': f'Device created but keys not set: {keys_msg}'
                })
            else:
                logger.info(f"Keys set successfully for device {device['name']}: {keys_msg}")
                results['successful'].append({
                    'dev_eui': device['dev_eui'],
                    'name': device['name']
                })
        
        except Exception as e:
            logger.error(f"Error registering device {device['name']}: {e}", exc_info=True)
            results['failed'].append({
                'dev_eui': device['dev_eui'],
                'name': device['name'],
                'error': str(e)
            })
    
    # Store results in session for display
    session['registration_results'] = results
    
    logger.info("="*80)
    logger.info(f"REGISTRATION COMPLETE - Success: {len(results['successful'])}, Failed: {len(results['failed'])}")
    logger.info("="*80)
    
    return redirect(url_for('registration_results'))


@app.route('/registration-results')
def registration_results():
    """Display registration results."""
    logger.info("="*80)
    logger.info("REGISTRATION RESULTS PAGE")
    logger.info("="*80)
    
    results = session.get('registration_results', {})
    
    if not results:
        logger.warning("No registration results found in session")
        flash('Keine Registrierungsergebnisse gefunden.', 'warning')
        return redirect(url_for('index'))
    
    logger.info(f"Displaying results: {results.get('total', 0)} total, {len(results.get('successful', []))} successful, {len(results.get('failed', []))} failed")
    
    return render_template('registration_results.html', 
                         results=results,
                         now=datetime.now())


@app.route('/change_sheet', methods=['POST'])
def change_sheet():
    """Handle sheet change request."""
    sheet_name = request.form.get('sheet_name')
    filepath = session.get('filepath')
    original_filename = session.get('original_filename')
    sheet_names = session.get('sheet_names', [])
    
    if not filepath or not os.path.exists(filepath):
        flash('Datei nicht gefunden. Bitte laden Sie die Datei erneut hoch.', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Read selected sheet
        df = pd.read_excel(filepath, sheet_name=sheet_name)
        
        # Convert DataFrame to HTML table
        # Get first 100 rows for preview
        preview_df = df.head(100)
        
        # Convert to HTML with custom classes
        table_html = preview_df.to_html(
            classes='table is-bordered is-striped is-hoverable is-fullwidth',
            index=False,
            na_rep='N/A'
        )
        
        # Get file info
        file_info = {
            'filename': original_filename,
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'current_sheet': sheet_name,
            'sheet_names': sheet_names
        }
        
        return render_template('preview.html', 
                             table_html=table_html, 
                             file_info=file_info)
    
    except Exception as e:
        flash(f'Fehler beim Lesen des Blattes: {str(e)}', 'danger')
        return redirect(url_for('index'))


@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Clean up uploaded file and return to home."""
    filepath = session.get('filepath')
    if filepath and os.path.exists(filepath):
        os.remove(filepath)
    session.clear()
    return redirect(url_for('index'))


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    flash('Datei ist zu groß. Maximale Größe beträgt 16MB', 'danger')
    return redirect(url_for('index'))


# ============================================================================
# DEVICE MANAGEMENT ROUTES
# ============================================================================

@app.route('/device-management')
def device_management():
    """Device management page - view and delete devices."""
    global SERVER_URL, API_CODE
    
    logger.info("="*80)
    logger.info("DEVICE MANAGEMENT PAGE")
    logger.info("="*80)
    
    # Check if server is configured
    if not SERVER_URL or not API_CODE:
        flash('Bitte konfigurieren Sie zuerst den Server', 'warning')
        return redirect(url_for('server_config'))
    
    return render_template('device_management.html',
                         server_url=SERVER_URL)


@app.route('/api/list-devices', methods=['POST'])
def api_list_devices():
    """API endpoint to list devices."""
    global SERVER_URL, API_CODE
    
    try:
        # Get parameters from request
        application_id = request.form.get('application_id', '').strip()
        search = request.form.get('search', '').strip()
        limit = int(request.form.get('limit', 1000))
        offset = int(request.form.get('offset', 0))
        
        logger.info(f"=== LIST DEVICES REQUEST ===")
        logger.info(f"Application ID: '{application_id}'")
        logger.info(f"Search: '{search}'")
        logger.info(f"Limit: {limit}, Offset: {offset}")
        logger.info(f"Server URL: {SERVER_URL}")
        logger.info(f"API Key configured: {bool(API_CODE)}")
        
        # Validate application_id is provided
        if not application_id:
            logger.warning("Application ID is required but was not provided")
            return {'success': False, 'message': 'Application ID ist erforderlich'}, 400
        
        # Create gRPC client
        from grpc_client import ChirpStackClient
        client = ChirpStackClient(SERVER_URL, API_CODE)
        logger.info(f"gRPC client created")
        
        # Connect
        logger.info(f"Attempting to connect to ChirpStack...")
        connected, conn_msg = client.connect()
        if not connected:
            logger.error(f"Connection failed: {conn_msg}")
            return {'success': False, 'message': f'Connection failed: {conn_msg}'}, 500
        logger.info(f"Connected successfully: {conn_msg}")
        
        # List devices
        logger.info(f"Calling list_devices with application_id='{application_id}'...")
        success, result = client.list_devices(
            application_id=application_id,
            limit=limit,
            offset=offset,
            search=search
        )
        
        client.close()
        
        if success:
            logger.info(f"✓ Successfully retrieved {len(result['devices'])} devices (total: {result['total_count']})")
            return {'success': True, 'data': result}
        else:
            logger.error(f"✗ Failed to list devices. Error: {result}")
            return {'success': False, 'message': f'ChirpStack error: {result}'}, 500
            
    except Exception as e:
        logger.error(f"✗ Exception in api_list_devices: {type(e).__name__}: {str(e)}", exc_info=True)
        return {'success': False, 'message': str(e)}, 500


@app.route('/api/delete-devices-stream', methods=['POST'])
def api_delete_devices_stream():
    """Stream device deletion progress using SSE."""
    
    def generate():
        """Generator function for Server-Sent Events"""
        try:
            # Get device EUIs from request
            dev_euis = request.form.get('dev_euis', '')
            if not dev_euis:
                yield f"data: {json.dumps({'error': 'No devices specified'})}\n\n"
                return
            
            # Parse comma-separated dev_euis
            dev_eui_list = [eui.strip() for eui in dev_euis.split(',') if eui.strip()]
            total = len(dev_eui_list)
            
            logger.info(f"Bulk delete requested for {total} devices")
            
            # Send initial status
            yield f"data: {json.dumps({'status': 'starting', 'total': total, 'current': 0})}\n\n"
            
            # Create gRPC client
            from grpc_client import ChirpStackClient
            client = ChirpStackClient(SERVER_URL, API_CODE)
            connected, conn_msg = client.connect()
            
            if not connected:
                yield f"data: {json.dumps({'error': f'Connection failed: {conn_msg}'})}\n\n"
                return
            
            results = {'successful': [], 'failed': []}
            
            # Delete each device
            for idx, dev_eui in enumerate(dev_eui_list, 1):
                try:
                    logger.info(f"Deleting device {idx}/{total}: {dev_eui}")
                    
                    deleted, del_msg = client.delete_device(dev_eui)
                    
                    if deleted:
                        results['successful'].append({
                            'dev_eui': dev_eui
                        })
                        yield f"data: {json.dumps({'status': 'processing', 'current': idx, 'total': total, 'device': dev_eui, 'result': 'success'})}\n\n"
                    else:
                        results['failed'].append({
                            'dev_eui': dev_eui,
                            'error': del_msg
                        })
                        yield f"data: {json.dumps({'status': 'processing', 'current': idx, 'total': total, 'device': dev_eui, 'result': 'failed', 'message': del_msg})}\n\n"
                    
                    time.sleep(0.1)  # Small delay to avoid overwhelming the server
                    
                except Exception as e:
                    logger.error(f"Error deleting device {dev_eui}: {e}")
                    results['failed'].append({
                        'dev_eui': dev_eui,
                        'error': str(e)
                    })
                    yield f"data: {json.dumps({'status': 'processing', 'current': idx, 'total': total, 'device': dev_eui, 'result': 'failed', 'message': str(e)})}\n\n"
            
            # Close connection
            client.close()
            
            # Send completion
            logger.info(f"Bulk delete completed: {len(results['successful'])} successful, {len(results['failed'])} failed")
            yield f"data: {json.dumps({'status': 'complete', 'results': results})}\n\n"
            
        except Exception as e:
            logger.error(f"Error in delete stream: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), content_type='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
