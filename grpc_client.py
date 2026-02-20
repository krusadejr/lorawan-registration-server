"""
gRPC Client for ChirpStack Device Registration
Handles all gRPC communication with the ChirpStack server
"""

import grpc
from generated.api import device_pb2, device_pb2_grpc
from generated.common import common_pb2
import re
import requests
import json


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
                # NOT_FOUND, UNAUTHENTICATED, PERMISSION_DENIED or INVALID_ARGUMENT means server is reachable (connection OK)
                if e.code() in [grpc.StatusCode.NOT_FOUND, grpc.StatusCode.UNAUTHENTICATED,
                               grpc.StatusCode.PERMISSION_DENIED, grpc.StatusCode.INVALID_ARGUMENT]:
                    return True, "Connected successfully (server is reachable)"
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
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"create_device gRPC error for {dev_eui}: code={e.code()}, details='{e.details()}', application_id={application_id}, device_profile_id={device_profile_id}")
            
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                error_msg = f"Authentication failed: Application ID '{application_id}' or Device Profile ID '{device_profile_id}' not found on ChirpStack server, or API token lacks permission. Please verify these IDs exist in your ChirpStack tenant."
            elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
                error_msg = f"Permission denied: API token does not have permission to create devices in Application '{application_id}'."
            elif e.code() == grpc.StatusCode.ALREADY_EXISTS:
                error_msg = "Device already exists in ChirpStack."
            elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                error_msg = f"Invalid data: {e.details()}"
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                error_msg = "ChirpStack server is unavailable. Check if server is running."
            elif e.code() == grpc.StatusCode.NOT_FOUND:
                error_msg = f"Application ID '{application_id}' or Device Profile ID '{device_profile_id}' not found on ChirpStack server."
            else:
                error_msg = f"gRPC Error [{e.code().name}]: {e.details()}"
            return False, error_msg
        except Exception as e:
            return False, f"Error creating device: {str(e)}"
    
    def create_device_keys(self, dev_eui, nwk_key, app_key, is_otaa=True, lorawan_version=None):
        """
        Create device keys in ChirpStack (version-aware)
        
        NOTE: ChirpStack protobuf field semantics differ between LoRaWAN versions:
        - LoRaWAN 1.0.x OTAA: Use nwk_key field for the Root Application Key (AppKey)
        - LoRaWAN 1.1.x: Use app_key field for the Application Root Key
        
        Args:
            dev_eui (str): Device EUI
            nwk_key (str): Network key (32 hex characters) 
            app_key (str): Application key (32 hex characters)
            is_otaa (bool): Whether device uses OTAA. Used as fallback if lorawan_version not provided.
            lorawan_version (dict): LoRaWAN version info from get_lorawan_version_from_profile_id()
                                  Format: {'version': '1.0.3', 'is_1_0_x': True, 'is_1_1_x': False, ...}
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # Determine version-aware field mapping
            if lorawan_version:
                # Use actual device profile version
                if lorawan_version['is_1_0_x']:
                    # LoRaWAN 1.0.x: AppKey goes to nwk_key field
                    proto_nwk_key = app_key
                    proto_app_key = ""
                    logger.info(f"[gRPC] create_device_keys (LoRaWAN {lorawan_version['version']} OTAA) - dev_eui={dev_eui}, nwk_key={app_key} (OTAA AppKey)")
                elif lorawan_version['is_1_1_x']:
                    # LoRaWAN 1.1.x: Standard field mapping
                    proto_nwk_key = nwk_key
                    proto_app_key = app_key
                    logger.info(f"[gRPC] create_device_keys (LoRaWAN {lorawan_version['version']}) - dev_eui={dev_eui}, nwk_key={nwk_key}, app_key={app_key}")
                else:
                    # Unknown version - use safe default
                    logger.warning(f"[gRPC] Unknown LoRaWAN version, using default mapping: {lorawan_version}")
                    proto_nwk_key = nwk_key
                    proto_app_key = app_key
            else:
                # Fallback: Use is_otaa flag
                if is_otaa:
                    proto_nwk_key = app_key
                    proto_app_key = ""
                    logger.info(f"[gRPC] create_device_keys (OTAA, version unknown) - dev_eui={dev_eui}, nwk_key={app_key}")
                else:
                    proto_nwk_key = nwk_key
                    proto_app_key = app_key
                    logger.info(f"[gRPC] create_device_keys (ABP/1.1.x fallback) - dev_eui={dev_eui}, nwk_key={nwk_key}, app_key={app_key}")
            
            # Create device keys object
            device_keys = device_pb2.DeviceKeys(
                dev_eui=dev_eui,
                nwk_key=proto_nwk_key,
                app_key=proto_app_key
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
    
    def update_device(self, dev_eui, name=None, description=None, tags=None, 
                     is_disabled=None, skip_fcnt_check=None, variables=None):
        """
        Update an existing device in ChirpStack
        
        Args:
            dev_eui (str): Device EUI
            name (str, optional): New device name
            description (str, optional): New device description
            tags (dict, optional): New tags (will be merged with existing tags)
            is_disabled (bool, optional): Disable/enable device
            skip_fcnt_check (bool, optional): Skip frame counter check
            variables (dict, optional): New variables (will be merged with existing)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # First, get the existing device
            success, device_data = self.get_device(dev_eui)
            if not success:
                return False, f"Could not retrieve device {dev_eui}: {device_data}"
            
            # Create device object with updated values
            device = device_pb2.Device(
                dev_eui=device_data['dev_eui'],
                name=name if name is not None else device_data['name'],
                description=description if description is not None else device_data['description'],
                application_id=device_data['application_id'],
                device_profile_id=device_data['device_profile_id'],
                is_disabled=is_disabled if is_disabled is not None else device_data['is_disabled'],
                skip_fcnt_check=skip_fcnt_check if skip_fcnt_check is not None else device_data['skip_fcnt_check']
            )
            
            # Merge tags: start with existing, override with new
            merged_tags = dict(device_data.get('tags', {}))
            if tags:
                merged_tags.update(tags)
            
            # Add merged tags to device
            for key, value in merged_tags.items():
                device.tags[key] = str(value)
            
            # Merge variables: start with existing, override with new
            merged_variables = dict(device_data.get('variables', {}))
            if variables:
                merged_variables.update(variables)
            
            # Add merged variables to device
            for key, value in merged_variables.items():
                device.variables[key] = str(value)
            
            # Create update request
            request = device_pb2.UpdateDeviceRequest(device=device)
            
            # Make gRPC call
            self.stub.Update(request, metadata=self._get_metadata())
            
            return True, f"Device {dev_eui} updated successfully"
            
        except grpc.RpcError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"update_device gRPC error for {dev_eui}: code={e.code()}, details='{e.details()}'")
            
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                error_msg = "Authentication failed: API token is invalid."
            elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
                error_msg = "Permission denied: API token lacks permission to update devices."
            elif e.code() == grpc.StatusCode.NOT_FOUND:
                error_msg = f"Device {dev_eui} not found on ChirpStack."
            elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                error_msg = f"Invalid data: {e.details()}"
            else:
                error_msg = f"gRPC Error [{e.code().name}]: {e.details()}"
            return False, error_msg
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Exception in update_device: {type(e).__name__}: {str(e)}", exc_info=True)
            return False, f"Error updating device: {str(e)}"
    
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
                    'device_profile_name': item.device_profile_name,
                    'tags': dict(item.tags)
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
    @staticmethod
    def parse_mac_version(mac_version_enum):
        """
        Parse MAC version enum to human-readable string
        
        Args:
            mac_version_enum (int): Enum value from common.MacVersion
            
        Returns:
            dict: {'version': '1.0.3', 'major': 1, 'minor': 0, 'patch': 3}
        """
        mac_version_map = {
            0: {'version': '1.0.0', 'major': 1, 'minor': 0, 'patch': 0},
            1: {'version': '1.0.1', 'major': 1, 'minor': 0, 'patch': 1},
            2: {'version': '1.0.2', 'major': 1, 'minor': 0, 'patch': 2},
            3: {'version': '1.0.3', 'major': 1, 'minor': 0, 'patch': 3},
            4: {'version': '1.0.4', 'major': 1, 'minor': 0, 'patch': 4},
            5: {'version': '1.1.0', 'major': 1, 'minor': 1, 'patch': 0},
        }
        return mac_version_map.get(mac_version_enum, {'version': 'UNKNOWN', 'major': -1, 'minor': -1, 'patch': -1})
    
    def get_device_profiles_via_rest(self, tenant_id=None):
        """
        Get list of device profiles using REST API (simpler than gRPC)
        This includes LoRaWAN version information
        
        Args:
            tenant_id (str): Optional tenant ID to filter profiles
            
        Returns:
            tuple: (success: bool, profiles: list or error: str)
        """
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # Construct REST API endpoint
            base_url = f"http://{self.server_url}"
            url = f"{base_url}/api/device-profiles"
            if tenant_id:
                url += f"?tenant_id={tenant_id}"
            
            headers = {
                "Grpc-Metadata-authorization": self.api_key,
                "Content-Type": "application/json"
            }
            
            logger.info(f"[REST] Fetching device profiles from {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            profiles = []
            
            for profile in data.get('result', []):
                mac_version = self.parse_mac_version(profile.get('mac_version', 0))
                profiles.append({
                    'id': profile.get('id', ''),
                    'name': profile.get('name', ''),
                    'mac_version': mac_version,
                    'lorawan_version': f"{mac_version['major']}.{mac_version['minor']}.{mac_version['patch']}",
                    'supports_otaa': profile.get('supports_otaa', False),
                    'supports_abp': profile.get('supports_abp', False),
                    'raw_data': profile
                })
            
            logger.info(f"[REST] Found {len(profiles)} device profiles")
            return True, profiles
            
        except requests.exceptions.RequestException as e:
            error_msg = f"REST API error: {e}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error fetching device profiles: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_lorawan_version_from_profile_id(self, device_profile_id, tenant_id=None):
        """
        Get LoRaWAN version for a specific device profile
        
        Args:
            device_profile_id (str): UUID of device profile
            tenant_id (str): Optional tenant ID
            
        Returns:
            dict: {'version': '1.0.3', 'major': 1, 'minor': 0, 'patch': 3, 'is_1_0_x': True}
        """
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            success, profiles = self.get_device_profiles_via_rest(tenant_id)
            if not success:
                logger.error(f"Could not fetch device profiles: {profiles}")
                return None
            
            for profile in profiles:
                if profile['id'] == device_profile_id:
                    mac_v = profile['mac_version']
                    return {
                        'version': mac_v['version'],
                        'major': mac_v['major'],
                        'minor': mac_v['minor'],
                        'patch': mac_v['patch'],
                        'is_1_0_x': mac_v['major'] == 1 and mac_v['minor'] == 0,
                        'is_1_1_x': mac_v['major'] == 1 and mac_v['minor'] == 1,
                        'name': profile['name'],
                        'supports_otaa': profile['supports_otaa'],
                        'supports_abp': profile['supports_abp']
                    }
            
            logger.warning(f"Device profile {device_profile_id} not found in list")
            return None
            
        except Exception as e:
            logger.error(f"Error getting LoRaWAN version: {str(e)}")
            return None