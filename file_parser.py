"""
File Parser for Device Data
Handles parsing of Excel, TXT, and JSON files containing device information
"""

import pandas as pd
import json


def parse_excel_file(filepath):
    """
    Parse Excel file and return sheet information
    
    Args:
        filepath (str): Path to Excel file
        
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'file_type': str,
            'sheets': list of sheet names,
            'data': dict of {sheet_name: DataFrame}
        }
    """
    try:
        # Read all sheets
        excel_file = pd.ExcelFile(filepath)
        sheet_names = excel_file.sheet_names
        
        # Read data from all sheets
        sheets_data = {}
        for sheet_name in sheet_names:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            sheets_data[sheet_name] = df
        
        return {
            'success': True,
            'message': f'Excel-Datei erfolgreich gelesen ({len(sheet_names)} Blatt/Blätter)',
            'file_type': 'excel',
            'sheets': sheet_names,
            'data': sheets_data
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Fehler beim Lesen der Excel-Datei: {str(e)}',
            'file_type': 'excel',
            'sheets': [],
            'data': {}
        }


def parse_txt_file(filepath):
    """
    Parse TXT file (expects JSON lines format like the example files)
    
    Args:
        filepath (str): Path to TXT file
        
    Returns:
        dict: Parsed data structure
    """
    try:
        devices = []
        device_keys = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    data = json.loads(line)
                    
                    # Check if it's a device entry
                    if 'device' in data:
                        devices.append(data['device'])
                    # Check if it's a device_keys entry
                    elif 'device_keys' in data:
                        device_keys.append(data['device_keys'])
                    else:
                        # Unknown format, add as-is
                        devices.append(data)
                        
                except json.JSONDecodeError as e:
                    return {
                        'success': False,
                        'message': f'JSON-Fehler in Zeile {line_num}: {str(e)}',
                        'file_type': 'txt',
                        'sheets': [],
                        'data': {}
                    }
        
        # Convert to DataFrame
        result_data = {}
        
        if devices:
            df_devices = pd.DataFrame(devices)
            result_data['Devices'] = df_devices
        
        if device_keys:
            df_keys = pd.DataFrame(device_keys)
            result_data['Device_Keys'] = df_keys
        
        if not result_data:
            return {
                'success': False,
                'message': 'Keine Gerätedaten in der Datei gefunden',
                'file_type': 'txt',
                'sheets': [],
                'data': {}
            }
        
        return {
            'success': True,
            'message': f'TXT-Datei erfolgreich gelesen ({len(devices)} Geräte, {len(device_keys)} Schlüssel)',
            'file_type': 'txt',
            'sheets': list(result_data.keys()),
            'data': result_data
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Fehler beim Lesen der TXT-Datei: {str(e)}',
            'file_type': 'txt',
            'sheets': [],
            'data': {}
        }


def parse_json_file(filepath):
    """
    Parse JSON file
    
    Args:
        filepath (str): Path to JSON file
        
    Returns:
        dict: Parsed data structure
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        result_data = {}
        
        # If it's a list of devices
        if isinstance(data, list):
            df = pd.DataFrame(data)
            result_data['Data'] = df
        
        # If it's a dict with keys
        elif isinstance(data, dict):
            # Check for 'devices' key
            if 'devices' in data:
                df = pd.DataFrame(data['devices'])
                result_data['Devices'] = df
            
            # Check for 'device_keys' key
            if 'device_keys' in data:
                df_keys = pd.DataFrame(data['device_keys'])
                result_data['Device_Keys'] = df_keys
            
            # If no specific keys, treat the whole dict as one record
            if not result_data:
                df = pd.DataFrame([data])
                result_data['Data'] = df
        
        else:
            return {
                'success': False,
                'message': 'Unbekanntes JSON-Format',
                'file_type': 'json',
                'sheets': [],
                'data': {}
            }
        
        return {
            'success': True,
            'message': f'JSON-Datei erfolgreich gelesen',
            'file_type': 'json',
            'sheets': list(result_data.keys()),
            'data': result_data
        }
        
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'message': f'Ungültiges JSON-Format: {str(e)}',
            'file_type': 'json',
            'sheets': [],
            'data': {}
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Fehler beim Lesen der JSON-Datei: {str(e)}',
            'file_type': 'json',
            'sheets': [],
            'data': {}
        }


def parse_file(filepath, file_extension):
    """
    Parse file based on extension
    
    Args:
        filepath (str): Path to file
        file_extension (str): File extension (without dot)
        
    Returns:
        dict: Parsed data structure
    """
    ext = file_extension.lower()
    
    if ext in ['xlsx', 'xls', 'xlsm']:
        return parse_excel_file(filepath)
    elif ext == 'txt':
        return parse_txt_file(filepath)
    elif ext == 'json':
        return parse_json_file(filepath)
    else:
        return {
            'success': False,
            'message': f'Nicht unterstütztes Dateiformat: {ext}',
            'file_type': ext,
            'sheets': [],
            'data': {}
        }


def get_column_info(dataframe):
    """
    Get information about DataFrame columns
    
    Args:
        dataframe: pandas DataFrame
        
    Returns:
        list: List of dicts with column information
    """
    columns_info = []
    
    for col in dataframe.columns:
        # Get sample values (first 3 non-null values)
        sample_values = dataframe[col].dropna().head(3).tolist()
        sample_str = ', '.join([str(v)[:50] for v in sample_values])
        
        columns_info.append({
            'name': col,
            'dtype': str(dataframe[col].dtype),
            'null_count': int(dataframe[col].isnull().sum()),
            'total_count': len(dataframe),
            'sample_values': sample_str
        })
    
    return columns_info


def validate_device_data(row):
    """
    Validate if a row has minimum required device data
    
    Args:
        row: DataFrame row
        
    Returns:
        tuple: (is_valid, missing_fields)
    """
    required_fields = ['dev_eui']
    missing = []
    
    for field in required_fields:
        if field not in row or pd.isna(row[field]) or str(row[field]).strip() == '':
            missing.append(field)
    
    return len(missing) == 0, missing
