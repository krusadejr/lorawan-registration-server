"""
gRPC Client for ChirpStack Device Registration
Handles all gRPC communication with the ChirpStack server
"""

import grpc
from generated.api import device_pb2, device_pb2_grpc
from generated.common import common_pb2
import re


class ChirpStackClient:
    """ChirpStack gRPC Client"""
    
    def __init__(self, server_url, api_key):
        """
        Initialize the gRPC client
        
        Args:
            server_url (str): ChirpStack server URL (e.g., 'localhost:8080')
            api_key (str): API key for authentication
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Clean the server URL - remove http://, https://, and trailing slashes
        self.server_url = self._clean_server_url(server_url)
        # Clean the API key - remove extra whitespace
        self.api_key = api_key.strip() if api_key else ""
        
        logger.info(f"ChirpStackClient initialized: server_url='{self.server_url}', api_key_length={len(self.api_key)}, api_key_prefix={'***' + self.api_key[:10] if len(self.api_key) >= 10 else 'TOO_SHORT_OR_EMPTY'}")
        
        self.channel = None
        self.stub = None
    
    def _clean_server_url(self, url):
        """
        Clean server URL for gRPC connection
        Removes http://, https://, and trailing slashes
        
        Args:
            url (str): Original URL
            
        Returns:
            str: Cleaned URL (e.g., 'localhost:8080')
        """
        # Remove http:// or https://
        url = url.replace('http://', '').replace('https://', '')
        # Remove trailing slashes
        url = url.rstrip('/')
        return url
        
    def connect(self):
        """Establish connection to ChirpStack server"""
        try:
            # Create insecure channel (use secure channel in production)
            self.channel = grpc.insecure_channel(self.server_url)
            self.stub = device_pb2_grpc.DeviceServiceStub(self.channel)
            
            # Actually test the connection by making a simple call with a timeout
            # Try to get a device that doesn't exist - we just want to verify connectivity
            try:
                request = device_pb2.GetDeviceRequest(dev_eui="0000000000000000")
                # Set a short timeout to fail fast
                self.stub.Get(request, metadata=self._get_metadata(), timeout=3.0)
            except grpc.RpcError as e:
                # UNAUTHENTICATED means bad API token - this is a FAILURE
                if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                    return False, "Authentication failed: API token is invalid or missing. Check API_CODE in Einstellungen (Settings)."
                # PERMISSION_DENIED also means auth problem
                elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
                    return False, "Permission denied: API token does not have required permissions."
                # NOT_FOUND or INVALID_ARGUMENT means server is reachable and auth is OK
                elif e.code() in [grpc.StatusCode.NOT_FOUND, grpc.StatusCode.INVALID_ARGUMENT]:
                    return True, "Connected successfully (server is reachable and authenticated)"
                # UNAVAILABLE, DEADLINE_EXCEEDED, etc. means connection failed
                elif e.code() in [grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED]:
                    return False, f"Server not reachable: {e.code()}: {e.details()}"
                else:
                    # Other errors - still means we reached the server
                    return True, f"Connected (server responded with: {e.code()})"
            
            return True, "Connected successfully"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    def close(self):
        """Close the gRPC channel"""
        if self.channel:
            self.channel.close()
    
    def _get_metadata(self):
        """Get authentication metadata for gRPC calls"""
        import logging
        logger = logging.getLogger(__name__)
        metadata = [('authorization', f'Bearer {self.api_key}')]
        logger.debug(f"Generated metadata with api_key length: {len(self.api_key)}")
        return metadata
    
    def _validate_uuid(self, value, field_name):
        """
        Validate that a string is a valid UUID
        
        Args:
            value (str): Value to validate
            field_name (str): Name of the field for error messages
            
        Returns:
            tuple: (valid: bool, message: str)
        """
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        
        if not value:
            return False, f"{field_name} is empty"
        
        if not uuid_pattern.match(value.strip()):
            return False, f"{field_name} is not a valid UUID. Got: '{value}'. Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        
        return True, "Valid UUID"
    
    def create_device(self, dev_eui, name, application_id, device_profile_id, 
                     description="", is_disabled=False, skip_fcnt_check=False,
                     tags=None, variables=None):
        """
        Create a new device in ChirpStack
        
        Args:
            dev_eui (str): Device EUI (16 hex characters)
            name (str): Device name
            application_id (str): Application ID (UUID)
            device_profile_id (str): Device Profile ID (UUID)
            description (str): Device description
            is_disabled (bool): Whether device is disabled
            skip_fcnt_check (bool): Skip frame counter check
            tags (dict): Device tags
            variables (dict): Device variables
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Validate UUIDs before making the gRPC call
            valid_app, app_msg = self._validate_uuid(application_id, "Application ID")
            if not valid_app:
                return False, app_msg
            
            valid_profile, profile_msg = self._validate_uuid(device_profile_id, "Device Profile ID")
            if not valid_profile:
                return False, profile_msg
            
            # Create device object
            device = device_pb2.Device(
                dev_eui=dev_eui,
                name=name,
                application_id=application_id,
                device_profile_id=device_profile_id,
                description=description,
                is_disabled=is_disabled,
                skip_fcnt_check=skip_fcnt_check
            )
            
            # Add tags if provided
            if tags:
                for key, value in tags.items():
                    device.tags[key] = value
            
            # Add variables if provided
            if variables:
                for key, value in variables.items():
                    device.variables[key] = value
            
            # Create request
            request = device_pb2.CreateDeviceRequest(device=device)
            
            # Make gRPC call
            self.stub.Create(request, metadata=self._get_metadata())
            
            return True, f"Device {dev_eui} created successfully"
            
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                error_msg = "Authentication failed: API token is invalid or missing. Please check your API_CODE in Einstellungen (Settings)."
            elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
                error_msg = "Permission denied: API token does not have permission to create devices."
            elif e.code() == grpc.StatusCode.ALREADY_EXISTS:
                error_msg = "Device already exists in ChirpStack."
            elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                error_msg = f"Invalid data: {e.details()}"
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                error_msg = "ChirpStack server is unavailable. Check if server is running."
            else:
                error_msg = f"gRPC Error [{e.code().name}]: {e.details()}"
            return False, error_msg
        except Exception as e:
            return False, f"Error creating device: {str(e)}"
    
    def create_device_keys(self, dev_eui, nwk_key, app_key):
        """
        Create device keys in ChirpStack
        
        Args:
            dev_eui (str): Device EUI
            nwk_key (str): Network key (32 hex characters)
            app_key (str): Application key (32 hex characters)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Create device keys object
            device_keys = device_pb2.DeviceKeys(
                dev_eui=dev_eui,
                nwk_key=nwk_key,
                app_key=app_key
            )
            
            # Create request
            request = device_pb2.CreateDeviceKeysRequest(device_keys=device_keys)
            
            # Make gRPC call
            self.stub.CreateKeys(request, metadata=self._get_metadata())
            
            return True, f"Keys for device {dev_eui} created successfully"
            
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                error_msg = "Authentication failed: API token is invalid. Check API_CODE in Einstellungen."
            elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
                error_msg = "Permission denied: API token lacks permission to set device keys."
            elif e.code() == grpc.StatusCode.NOT_FOUND:
                error_msg = f"Device {dev_eui} not found in ChirpStack."
            elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                error_msg = f"Invalid keys format: {e.details()}"
            else:
                error_msg = f"gRPC Error [{e.code().name}]: {e.details()}"
            return False, error_msg
        except Exception as e:
            return False, f"Error creating device keys: {str(e)}"
    
    def get_device(self, dev_eui):
        """
        Get device information from ChirpStack
        
        Args:
            dev_eui (str): Device EUI
            
        Returns:
            tuple: (success: bool, device_data: dict or error_message: str)
        """
        try:
            request = device_pb2.GetDeviceRequest(dev_eui=dev_eui)
            response = self.stub.Get(request, metadata=self._get_metadata())
            
            device_data = {
                'dev_eui': response.device.dev_eui,
                'name': response.device.name,
                'description': response.device.description,
                'application_id': response.device.application_id,
                'device_profile_id': response.device.device_profile_id,
                'is_disabled': response.device.is_disabled,
                'skip_fcnt_check': response.device.skip_fcnt_check,
                'tags': dict(response.device.tags),
                'variables': dict(response.device.variables)
            }
            
            return True, device_data
            
        except grpc.RpcError as e:
            # If device not found, return False but not as an error
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return False, "Device not found"
            error_msg = f"gRPC Error: {e.code()}: {e.details()}"
            return False, error_msg
        except Exception as e:
            return False, f"Error getting device: {str(e)}"
    
    def device_exists(self, dev_eui):
        """
        Check if a device exists in ChirpStack
        
        Args:
            dev_eui (str): Device EUI
            
        Returns:
            bool: True if device exists, False otherwise
        """
        success, _ = self.get_device(dev_eui)
        return success
    
    def delete_device(self, dev_eui):
        """
        Delete a device from ChirpStack
        
        Args:
            dev_eui (str): Device EUI
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            request = device_pb2.DeleteDeviceRequest(dev_eui=dev_eui)
            self.stub.Delete(request, metadata=self._get_metadata())
            
            return True, f"Device {dev_eui} deleted successfully"
            
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                error_msg = "Authentication failed: API token is invalid. Check API_CODE in Einstellungen."
            elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
                error_msg = "Permission denied: API token lacks permission to delete devices."
            elif e.code() == grpc.StatusCode.NOT_FOUND:
                error_msg = f"Device {dev_eui} not found (may already be deleted)."
            else:
                error_msg = f"gRPC Error [{e.code().name}]: {e.details()}"
            return False, error_msg
        except Exception as e:
            return False, f"Error deleting device: {str(e)}"
    
    def list_devices(self, application_id="", limit=100, offset=0, search=""):
        """
        List devices from ChirpStack
        
        Args:
            application_id (str): Filter by application ID (optional)
            limit (int): Maximum number of devices to return
            offset (int): Offset for pagination
            search (str): Search query for device name/dev_eui
            
        Returns:
            tuple: (success: bool, data: dict or error_message: str)
                   data contains: {'total_count': int, 'devices': list}
        """
        try:
            # Build request parameters
            request_params = {
                'limit': limit,
                'offset': offset
            }
            
            # Add optional fields only if provided
            if application_id:
                request_params['application_id'] = application_id
            
            if search:
                request_params['search'] = search
            
            # Debug logging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Creating ListDevicesRequest with params: {request_params}")
            
            # Create request with all parameters at once
            try:
                request = device_pb2.ListDevicesRequest(**request_params)
                logger.info(f"Request created successfully. Request: {request}")
            except Exception as req_error:
                logger.error(f"Failed to create request: {req_error}")
                return False, f"Failed to create request: {str(req_error)}"
            
            response = self.stub.List(request, metadata=self._get_metadata())
            
            # Convert response to dict
            devices = []
            for item in response.result:
                device = {
                    'dev_eui': item.dev_eui,
                    'name': item.name,
                    'description': item.description,
                    'device_profile_id': item.device_profile_id,
                    'device_profile_name': item.device_profile_name
                }
                devices.append(device)
            
            result = {
                'total_count': response.total_count,
                'devices': devices
            }
            
            return True, result
            
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                error_msg = "Authentication failed: API token is invalid. Check API_CODE in Einstellungen."
            elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
                error_msg = "Permission denied: API token lacks permission to list devices."
            elif e.code() == grpc.StatusCode.NOT_FOUND:
                error_msg = f"Application {application_id} not found in ChirpStack."
            elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                error_msg = f"Invalid application_id format: {e.details()}"
            else:
                error_msg = f"gRPC Error [{e.code().name}]: {e.details()}"
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"gRPC error in list_devices: code={e.code()}, details={e.details()}")
            return False, error_msg
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Non-gRPC exception in list_devices: {type(e).__name__}: {str(e)}", exc_info=True)
            return False, f"Error listing devices: {type(e).__name__}: {str(e)}"
        except Exception as e:
            return False, f"Error listing devices: {str(e)}"
    
    def test_connection(self):
        """
        Test the connection to ChirpStack server
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Try to make a simple call (list devices with limit 1)
            request = device_pb2.ListDevicesRequest(limit=1)
            self.stub.List(request, metadata=self._get_metadata(), timeout=5)
            return True, "Connection successful"
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                return False, "Authentication failed. Check your API key."
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                return False, "Server unavailable. Check server URL and port."
            else:
                return False, f"gRPC Error: {e.code()}: {e.details()}"
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"


def validate_dev_eui(dev_eui):
    """
    Validate DevEUI format
    
    Args:
        dev_eui (str): Device EUI to validate
        
    Returns:
        tuple: (valid: bool, message: str)
    """
    if not dev_eui:
        return False, "DevEUI cannot be empty"
    
    # Remove any spaces or dashes
    clean_eui = dev_eui.replace(' ', '').replace('-', '').upper()
    
    # Check length (should be 16 hex characters)
    if len(clean_eui) != 16:
        return False, f"DevEUI must be 16 hex characters, got {len(clean_eui)}"
    
    # Check if all characters are hex
    try:
        int(clean_eui, 16)
    except ValueError:
        return False, "DevEUI must contain only hexadecimal characters (0-9, A-F)"
    
    return True, clean_eui


def validate_key(key, key_name="Key"):
    """
    Validate encryption key format
    
    Args:
        key (str): Key to validate
        key_name (str): Name of the key (for error messages)
        
    Returns:
        tuple: (valid: bool, message_or_clean_key: str)
    """
    if not key:
        return False, f"{key_name} cannot be empty"
    
    # Remove any spaces or dashes
    clean_key = key.replace(' ', '').replace('-', '').upper()
    
    # Check length (should be 32 hex characters)
    if len(clean_key) != 32:
        return False, f"{key_name} must be 32 hex characters, got {len(clean_key)}"
    
    # Check if all characters are hex
    try:
        int(clean_key, 16)
    except ValueError:
        return False, f"{key_name} must contain only hexadecimal characters (0-9, A-F)"
    
    return True, clean_key
