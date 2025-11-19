"""
File Parser for Device Data
Handles parsing of Excel, TXT, CSV, and JSON files containing device information
"""

import pandas as pd
import json
import csv
import io


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


def detect_delimiter(filepath, sample_size=5):
    """
    Detect the delimiter in a CSV/TXT file using csv.Sniffer
    
    Args:
        filepath (str): Path to file
        sample_size (int): Number of lines to sample for detection
        
    Returns:
        tuple: (delimiter, confidence, error_message)
            delimiter: detected delimiter character or None
            confidence: 'high', 'medium', 'low', or None
            error_message: error description if detection failed
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Read first few lines for detection
            sample_lines = []
            for i, line in enumerate(f):
                if i >= sample_size:
                    break
                sample_lines.append(line)
            
            if not sample_lines:
                return None, None, "Datei ist leer"
            
            sample = ''.join(sample_lines)
            
            # Try using csv.Sniffer
            try:
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample, delimiters=',;\t| ').delimiter
                
                # Calculate confidence based on consistency
                delimiter_counts = []
                for line in sample_lines:
                    count = line.count(delimiter)
                    delimiter_counts.append(count)
                
                # Check if delimiter appears consistently
                if len(set(delimiter_counts)) == 1 and delimiter_counts[0] > 0:
                    confidence = 'high'
                elif max(delimiter_counts) > 0 and min(delimiter_counts) >= max(delimiter_counts) * 0.8:
                    confidence = 'medium'
                else:
                    confidence = 'low'
                
                return delimiter, confidence, None
                
            except csv.Error as e:
                # Sniffer failed, try manual detection
                common_delimiters = [',', ';', '\t', '|', ' ']
                delimiter_scores = {}
                
                for delim in common_delimiters:
                    counts = [line.count(delim) for line in sample_lines if line.strip()]
                    if counts and max(counts) > 0:
                        # Score based on consistency and frequency
                        avg_count = sum(counts) / len(counts)
                        consistency = 1 - (max(counts) - min(counts)) / (max(counts) + 1)
                        delimiter_scores[delim] = avg_count * consistency
                
                if delimiter_scores:
                    best_delim = max(delimiter_scores, key=delimiter_scores.get)
                    score = delimiter_scores[best_delim]
                    
                    if score > 2:
                        confidence = 'medium'
                    else:
                        confidence = 'low'
                    
                    return best_delim, confidence, None
                else:
                    return None, None, "Kein Trennzeichen erkannt"
    
    except Exception as e:
        return None, None, f"Fehler beim Erkennen: {str(e)}"


def parse_csv_txt_with_delimiter(filepath, delimiter):
    """
    Parse CSV/TXT file with specified delimiter
    
    Args:
        filepath (str): Path to file
        delimiter (str): Delimiter character to use
        
    Returns:
        dict: Parsed data structure
    """
    try:
        # Try to read with pandas
        df = pd.read_csv(filepath, delimiter=delimiter, encoding='utf-8')
        
        # Check if we got meaningful data
        if df.empty or len(df.columns) == 1:
            return {
                'success': False,
                'message': 'Datei konnte nicht korrekt geparst werden. Möglicherweise ist das Trennzeichen falsch.',
                'file_type': 'csv',
                'sheets': [],
                'data': {}
            }
        
        return {
            'success': True,
            'message': f'Datei erfolgreich gelesen ({len(df)} Zeilen, {len(df.columns)} Spalten)',
            'file_type': 'csv',
            'sheets': ['Data'],
            'data': {'Data': df}
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Fehler beim Lesen der Datei: {str(e)}',
            'file_type': 'csv',
            'sheets': [],
            'data': {}
        }


def parse_csv_file(filepath):
    """
    Parse CSV file with automatic delimiter detection
    
    Args:
        filepath (str): Path to CSV file
        
    Returns:
        dict: Parsed data structure with delimiter detection info
    """
    # Try to detect delimiter
    delimiter, confidence, error_msg = detect_delimiter(filepath)
    
    delimiter_name_map = {
        ',': 'Komma (,)',
        ';': 'Semikolon (;)',
        '\t': 'Tab (\\t)',
        '|': 'Pipe (|)',
        ' ': 'Leerzeichen'
    }
    
    if delimiter and confidence in ['high', 'medium']:
        # Try to parse with detected delimiter
        result = parse_csv_txt_with_delimiter(filepath, delimiter)
        
        if result['success']:
            delim_name = delimiter_name_map.get(delimiter, repr(delimiter))
            result['message'] = f"CSV-Datei erfolgreich gelesen mit Trennzeichen {delim_name} ({len(result['data']['Data'])} Zeilen)"
            return result
    
    # Detection failed or low confidence - ask user
    delimiter_info = {
        'detected_delimiter': delimiter,
        'confidence': confidence,
        'error_message': error_msg,
        'delimiter_name': delimiter_name_map.get(delimiter, repr(delimiter)) if delimiter else None
    }
    
    return {
        'success': False,
        'needs_delimiter': True,
        'delimiter_info': delimiter_info,
        'message': 'Trennzeichen konnte nicht automatisch erkannt werden',
        'file_type': 'csv',
        'sheets': [],
        'data': {}
    }


def parse_txt_file(filepath):
    """
    Parse TXT file - tries JSON lines format first, then CSV format
    
    Args:
        filepath (str): Path to TXT file
        
    Returns:
        dict: Parsed data structure
    """
    # First, try to detect if it's a JSON lines format
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line and (first_line.startswith('{') or first_line.startswith('[')):
                # Looks like JSON, try JSON parsing
                f.seek(0)
                devices = []
                device_keys = []
                
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
                            
                    except json.JSONDecodeError:
                        # Not valid JSON, break and try CSV format
                        break
                
                # If we successfully parsed JSON data
                if devices or device_keys:
                    result_data = {}
                    
                    if devices:
                        df_devices = pd.DataFrame(devices)
                        result_data['Devices'] = df_devices
                    
                    if device_keys:
                        df_keys = pd.DataFrame(device_keys)
                        result_data['Device_Keys'] = df_keys
                    
                    return {
                        'success': True,
                        'message': f'TXT-Datei erfolgreich gelesen ({len(devices)} Geräte, {len(device_keys)} Schlüssel)',
                        'file_type': 'txt',
                        'sheets': list(result_data.keys()),
                        'data': result_data
                    }
    
    except Exception:
        pass  # Fall through to CSV parsing
    
    # Not JSON format, try CSV-like parsing with delimiter detection
    delimiter, confidence, error_msg = detect_delimiter(filepath)
    
    delimiter_name_map = {
        ',': 'Komma (,)',
        ';': 'Semikolon (;)',
        '\t': 'Tab (\\t)',
        '|': 'Pipe (|)',
        ' ': 'Leerzeichen'
    }
    
    if delimiter and confidence in ['high', 'medium']:
        # Try to parse with detected delimiter
        result = parse_csv_txt_with_delimiter(filepath, delimiter)
        
        if result['success']:
            delim_name = delimiter_name_map.get(delimiter, repr(delimiter))
            result['message'] = f"TXT-Datei erfolgreich gelesen mit Trennzeichen {delim_name} ({len(result['data']['Data'])} Zeilen)"
            result['file_type'] = 'txt'
            return result
    
    # Detection failed or low confidence - ask user
    delimiter_info = {
        'detected_delimiter': delimiter,
        'confidence': confidence,
        'error_message': error_msg,
        'delimiter_name': delimiter_name_map.get(delimiter, repr(delimiter)) if delimiter else None
    }
    
    return {
        'success': False,
        'needs_delimiter': True,
        'delimiter_info': delimiter_info,
        'message': 'Trennzeichen konnte nicht automatisch erkannt werden',
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
    elif ext == 'csv':
        return parse_csv_file(filepath)
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
