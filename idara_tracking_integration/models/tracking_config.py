# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TrackingConfig(models.Model):
    _name = 'tracking.config'
    _description = 'Tracking Configuration'
    _rec_name = 'name'

    name = fields.Char(string='Configuration Name', required=True)
    api_key = fields.Char(string='API Key')
    api_url = fields.Char(string='API URL', default='https://api.tracking.example.com')
    username = fields.Char(string='Username')
    password = fields.Char(string='Password')
    google_maps_api_key = fields.Char(string='Google Maps API Key', help='Your Google Maps JavaScript API key for map visualization')
    auto_refresh_interval = fields.Integer(string='Map Auto Refresh (seconds)', default=30, help='How often to refresh device locations on the map (in seconds)')
    active = fields.Boolean(string='Active', default=True)
    device_ids = fields.One2many('tracking.device', 'config_id', string='Devices')
    device_count = fields.Integer(string='Device Count', compute='_compute_device_count')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    @api.depends('device_ids')
    def _compute_device_count(self):
        for record in self:
            record.device_count = len(record.device_ids)
    
    def action_view_devices(self):
        self.ensure_one()
        return {
            'name': 'Devices',
            'type': 'ir.actions.act_window',
            'res_model': 'tracking.device',
            'view_mode': 'tree,form',
            'domain': [('config_id', '=', self.id)],
            'context': {'default_config_id': self.id}
        }
    
    def test_connection(self):
        self.ensure_one()
        
        if not self.api_url:
            return self._show_error('Configuration Error', 'API URL is required')
        
        import requests
        import logging
        
        _logger = logging.getLogger(__name__)
        
        try:
            headers = {'Content-Type': 'application/json'}
            auth = None
            
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            elif self.username and self.password:
                auth = (self.username, self.password)
            
            url = self.api_url
            if not url.startswith('http'):
                url = f'https://{url}'
            
            _logger.info(f'Testing connection to: {url}')
            
            response = requests.get(url, headers=headers, auth=auth, timeout=10)
            
            if response.status_code == 200:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Connection Successful',
                        'message': f'Successfully connected to {url}',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            elif response.status_code == 401:
                return self._show_error('Authentication Failed', 'Invalid credentials. Check your API Key or Username/Password.')
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Connection Warning',
                        'message': f'Connected but got status {response.status_code}. Check API documentation.',
                        'type': 'warning',
                        'sticky': True,
                    }
                }
                
        except requests.exceptions.ConnectionError:
            return self._show_error('Connection Failed', f'Cannot reach {self.api_url}. Check URL and internet connection.')
        except requests.exceptions.Timeout:
            return self._show_error('Timeout', 'Connection timed out after 10 seconds.')
        except Exception as e:
            return self._show_error('Error', f'Test failed: {str(e)[:200]}')
    
    def fetch_devices_from_api(self):
        """Fetch all devices from the tracking API - GPSWOX Compatible"""
        self.ensure_one()
        
        # Validate configuration
        if not self.api_url:
            return self._show_error('Configuration Error', 'API URL is required.')
        
        if not self.username or not self.password:
            return self._show_error('Configuration Error', 'Username and Password are required for GPSWOX API.')
        
        try:
            import requests
            import json
            from datetime import datetime
            import logging
            
            _logger = logging.getLogger(__name__)
            
            # Step 1: Login to get user_api_hash
            login_url = self.api_url.strip()
            if not login_url.startswith('http'):
                login_url = f'https://{login_url}'
            if not login_url.endswith('/api/login'):
                login_url = f'{login_url}/api/login' if login_url.endswith('/') else f'{login_url}/api/login'
            
            _logger.info(f'Logging in to GPSWOX API: {login_url}')
            
            login_data = {
                'email': self.username,
                'password': self.password
            }
            
            login_response = requests.post(login_url, data=login_data, timeout=30)
            
            _logger.info(f'Login Response Status: {login_response.status_code}')
            _logger.info(f'Login Response: {login_response.text[:500]}')
            
            if login_response.status_code != 200:
                return self._show_error(
                    'Login Failed',
                    f'Could not login to GPSWOX. Status: {login_response.status_code}\nResponse: {login_response.text[:200]}'
                )
            
            try:
                login_result = login_response.json()
            except:
                return self._show_error('Invalid Login Response', f'Login response is not JSON: {login_response.text[:200]}')
            
            # Check login status
            if login_result.get('status') != 1:
                return self._show_error(
                    'Authentication Failed',
                    f'GPSWOX login failed. Please check your username and password.\nResponse: {login_result}'
                )
            
            user_api_hash = login_result.get('user_api_hash')
            if not user_api_hash:
                return self._show_error('API Hash Missing', f'Could not get user_api_hash from login response: {login_result}')
            
            _logger.info(f'Successfully logged in. Got user_api_hash')
            
            # DEBUGGING: Show login response to user
            debug_login = {
                'status': login_result.get('status'),
                'user_api_hash': user_api_hash[:20] + '...' if user_api_hash else None,
                'full_response_keys': list(login_result.keys())
            }
            _logger.info(f'Login response details: {debug_login}')
            
            # Step 2: Get ALL devices (GPSWOX returns groups with items)
            devices_url = self.api_url.strip()
            if not devices_url.startswith('http'):
                devices_url = f'https://{devices_url}'
            if not devices_url.endswith('/api/get_devices'):
                devices_url = f'{devices_url}/api/get_devices' if devices_url.endswith('/') else f'{devices_url}/api/get_devices'
            
            _logger.info(f'Fetching devices from: {devices_url}')
            
            # GPSWOX returns groups, so we just need one call (no pagination needed)
            devices_params = {'user_api_hash': user_api_hash}
            
            devices_response = requests.get(devices_url, params=devices_params, timeout=30)
            
            _logger.info(f'Response Status: {devices_response.status_code}')
            
            if devices_response.status_code != 200:
                return self._show_error(
                    'Failed to Get Devices',
                    f'Could not fetch devices. Status: {devices_response.status_code}\nResponse: {devices_response.text[:200]}'
                )
            
            try:
                groups_data = devices_response.json()
            except:
                return self._show_error('Invalid Devices Response', f'Devices response is not JSON: {devices_response.text[:500]}')
            
            # Process all devices from all groups
            return self._process_gpswox_devices(groups_data)
            
        except ImportError as e:
            return self._show_error(
                'Missing Library',
                f'Python requests library not installed: {str(e)}'
            )
        except requests.exceptions.ConnectionError as e:
            return self._show_error(
                'Connection Error', 
                f'Cannot connect to {self.api_url}\nError: {str(e)[:200]}'
            )
        except requests.exceptions.Timeout:
            return self._show_error(
                'Timeout', 
                f'Request timed out. Server not responding.'
            )
        except Exception as e:
            import traceback
            _logger.error(traceback.format_exc())
            return self._show_error(
                'Unexpected Error',
                f'{type(e).__name__}: {str(e)[:300]}'
            )
    
        """Process GPSWOX devices response"""
        from datetime import datetime
        import logging
        
        _logger = logging.getLogger(__name__)
        
        created_count = 0
        updated_count = 0
        
        # GPSWOX returns list of devices directly or in 'items' key
        if isinstance(devices_data, list):
            devices_list = devices_data
        elif isinstance(devices_data, dict):
            devices_list = devices_data.get('items', devices_data.get('data', []))
        else:
            return self._show_error('Invalid Format', f'Unexpected devices data format: {type(devices_data)}')
        
        if not devices_list:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Devices Found',
                    'message': 'GPSWOX API returned no devices. Please add devices in your GPSWOX panel first.',
                    'type': 'warning',
                    'sticky': True,
                }
            }
        
        _logger.info(f'Processing {len(devices_list)} devices from GPSWOX')
        
        for device_info in devices_list:
            try:
                # Log raw device data for debugging
                _logger.info(f'Raw device data: {device_info}')
                
                # GPSWOX device fields - try multiple field names
                device_id = str(device_info.get('imei') or device_info.get('id') or device_info.get('device_id', ''))
                if not device_id:
                    _logger.warning(f'Skipping device without ID: {device_info}')
                    continue
                
                # Extract name - GPSWOX uses 'name' field
                device_name = (device_info.get('name') or 
                              device_info.get('device_name') or 
                              device_info.get('label') or 
                              f'Device {device_id}')
                
                _logger.info(f'Processing device: ID={device_id}, Name={device_name}')
                
                existing_device = self.env['tracking.device'].search([
                    ('device_id', '=', device_id),
                    ('config_id', '=', self.id)
                ], limit=1)
                
                # Extract position data - GPSWOX uses 'lat' and 'lng'
                lat = float(device_info.get('lat') or device_info.get('latitude') or 0)
                lng = float(device_info.get('lng') or device_info.get('longitude') or 0)
                
                # Extract speed
                speed = float(device_info.get('speed') or 0)
                
                # Extract status
                status_raw = device_info.get('status') or device_info.get('online')
                
                vals = {
                    'name': device_name,
                    'device_id': device_id,
                    'imei': str(device_info.get('imei') or device_id),
                    'config_id': self.id,
                    'latitude': lat,
                    'longitude': lng,
                    'speed': speed,
                    'address': device_info.get('address') or '',
                    'status': self._map_gpswox_status(status_raw),
                    'vehicle_id': device_info.get('plate_number') or device_info.get('vehicle_plate') or '',
                    'driver_name': device_info.get('driver_name') or device_info.get('driver') or '',
                    'last_update': datetime.now(),
                }
                
                _logger.info(f'Device values to save: {vals}')
                
                if existing_device:
                    existing_device.write(vals)
                    updated_count += 1
                    _logger.info(f'Updated existing device: {device_name}')
                else:
                    self.env['tracking.device'].create(vals)
                    created_count += 1
                    _logger.info(f'Created new device: {device_name}')
                    
            except Exception as e:
                _logger.warning(f'Failed to process device: {e}')
                continue
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'GPSWOX Devices Synced',
                'message': f'Total: {created_count + updated_count} devices\nCreated: {created_count} | Updated: {updated_count}',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def _map_gpswox_status(self, gpswox_status):
        """Map GPSWOX status to our status values"""
        if not gpswox_status:
            return 'offline'
        
        status_map = {
            'online': 'online',
            'offline': 'offline',
            'moving': 'moving',
            'stopped': 'idle',
        }
        
        return status_map.get(str(gpswox_status).lower(), 'offline')
        """Fetch all devices from the tracking API"""
        self.ensure_one()
        
        # Validate configuration
        if not self.api_url:
            return self._show_error('Configuration Error', 'API URL is required. Please configure it first.')
        
        try:
            import requests
            import json
            from datetime import datetime
            import logging
            
            _logger = logging.getLogger(__name__)
            
            # Prepare API request
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            auth = None
            
            # Add authentication
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                _logger.info(f'Using Bearer token authentication')
            elif self.username and self.password:
                auth = (self.username, self.password)
                _logger.info(f'Using Basic authentication with username: {self.username}')
            else:
                _logger.warning('No authentication configured')
            
            # Build URL
            url = self.api_url.strip()
            if not url.startswith('http'):
                url = f'https://{url}'
            if not url.endswith('/devices'):
                url = f'{url}/devices' if url.endswith('/') else f'{url}/devices'
            
            _logger.info(f'Fetching devices from: {url}')
            _logger.info(f'Headers: {headers}')
            
            # Make API request
            response = requests.get(url, headers=headers, auth=auth, timeout=30, verify=True)
            
            _logger.info(f'Response Status: {response.status_code}')
            _logger.info(f'Response Headers: {dict(response.headers)}')
            _logger.info(f'Response Content-Type: {response.headers.get("Content-Type", "Unknown")}')
            _logger.info(f'Response Length: {len(response.content)} bytes')
            _logger.info(f'Response Text (first 1000 chars): {response.text[:1000]}')
            
            # Check response status
            if response.status_code == 401:
                return self._show_error(
                    'Authentication Error', 
                    'Invalid credentials (401). Please check your API Key or Username/Password.'
                )
            elif response.status_code == 403:
                return self._show_error(
                    'Access Forbidden', 
                    'Access denied (403). Your credentials may not have permission to access devices.'
                )
            elif response.status_code == 404:
                return self._show_error(
                    'Not Found', 
                    f'API endpoint not found (404). URL attempted: {url}\n\nPlease verify your API URL is correct.'
                )
            elif response.status_code >= 500:
                return self._show_error(
                    'Server Error', 
                    f'API server error ({response.status_code}). The tracking server is having issues. Response: {response.text[:200]}'
                )
            elif response.status_code != 200:
                return self._show_error(
                    f'HTTP Error {response.status_code}', 
                    f'API returned error. Response: {response.text[:300]}'
                )
            
            # Check if response is empty
            if not response.content or len(response.content) == 0:
                return self._show_error(
                    'Empty Response', 
                    'API returned completely empty response. This might mean:\n1. No devices registered\n2. API endpoint incorrect\n3. Server issue'
                )
            
            # Check content type
            content_type = response.headers.get('Content-Type', '')
            if 'json' not in content_type.lower():
                return self._show_error(
                    'Invalid Content Type',
                    f'API returned {content_type} instead of JSON. Response preview: {response.text[:200]}'
                )
            
            # Try to parse JSON
            try:
                devices_data = response.json()
                _logger.info(f'Parsed JSON successfully. Type: {type(devices_data)}')
                _logger.info(f'JSON keys: {devices_data.keys() if isinstance(devices_data, dict) else "Not a dict"}')
            except json.JSONDecodeError as e:
                return self._show_error(
                    'Invalid JSON', 
                    f'API response is not valid JSON.\n\nError: {str(e)}\n\nResponse preview: {response.text[:500]}\n\nPlease check your API documentation.'
                )
            except Exception as e:
                return self._show_error(
                    'Parse Error',
                    f'Could not parse response: {str(e)}\n\nResponse: {response.text[:500]}'
                )
            
            # Process devices
            return self._process_api_devices(devices_data)
            
        except ImportError as e:
            return self._show_error(
                'Missing Library',
                f'Python requests library not installed: {str(e)}\n\nPlease install it: pip install requests --break-system-packages'
            )
        except requests.exceptions.SSLError as e:
            return self._show_error(
                'SSL Error',
                f'SSL certificate verification failed. This might be a self-signed certificate.\n\nError: {str(e)[:200]}'
            )
        except requests.exceptions.ConnectionError as e:
            return self._show_error(
                'Connection Error', 
                f'Cannot connect to {self.api_url}\n\nPossible reasons:\n1. URL is incorrect\n2. Server is down\n3. Network/firewall blocking\n\nError: {str(e)[:200]}'
            )
        except requests.exceptions.Timeout:
            return self._show_error(
                'Timeout', 
                f'Request timed out after 30 seconds.\n\nThe server at {self.api_url} is not responding. Please check if the server is online.'
            )
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            _logger.error(f'Unexpected error: {error_trace}')
            return self._show_error(
                'Unexpected Error',
                f'An unexpected error occurred:\n\n{str(e)}\n\nType: {type(e).__name__}\n\nPlease check the Odoo logs for full details.'
            )
    
    def create_demo_devices(self):
        """Create demo devices for testing - separate button"""
        return self._create_demo_devices()
    
    def view_api_response(self):
        """Debug: View raw API response"""
        self.ensure_one()
        
        if not self.username or not self.password:
            return self._show_error('Missing Credentials', 'Please enter username and password first.')
        
        try:
            import requests
            import json
            
            # Login
            login_url = f"{self.api_url.strip()}/api/login"
            login_data = {'email': self.username, 'password': self.password}
            login_response = requests.post(login_url, data=login_data, timeout=30)
            
            if login_response.status_code != 200:
                return self._show_error('Login Failed', f'Status: {login_response.status_code}\n\n{login_response.text}')
            
            login_result = login_response.json()
            user_api_hash = login_result.get('user_api_hash')
            
            # Get devices (first page only for debugging)
            devices_url = f"{self.api_url.strip()}/api/get_devices"
            devices_params = {'user_api_hash': user_api_hash, 'page': 1, 'limit': 5}
            devices_response = requests.get(devices_url, params=devices_params, timeout=30)
            
            if devices_response.status_code != 200:
                return self._show_error('Get Devices Failed', f'Status: {devices_response.status_code}\n\n{devices_response.text}')
            
            devices_data = devices_response.json()
            
            # Format the response nicely
            response_text = f"""
=== GPSWOX API RESPONSE DEBUG ===

LOGIN RESPONSE:
{json.dumps(login_result, indent=2, ensure_ascii=False)}

---

DEVICES RESPONSE (First 5 devices):
{json.dumps(devices_data, indent=2, ensure_ascii=False)}

---

ANALYSIS:
- Response Type: {type(devices_data).__name__}
- Top Level Keys: {list(devices_data.keys()) if isinstance(devices_data, dict) else 'Not a dict'}
- Number of Devices: {len(devices_data.get('items', devices_data)) if isinstance(devices_data, dict) else len(devices_data) if isinstance(devices_data, list) else 0}

FIRST DEVICE FIELDS:
"""
            
            # Get first device
            if isinstance(devices_data, dict) and 'items' in devices_data and len(devices_data['items']) > 0:
                first_device = devices_data['items'][0]
                response_text += json.dumps(first_device, indent=2, ensure_ascii=False)
            elif isinstance(devices_data, list) and len(devices_data) > 0:
                first_device = devices_data[0]
                response_text += json.dumps(first_device, indent=2, ensure_ascii=False)
            else:
                response_text += "No devices found"
            
            # Create a temporary text file to show the response
            import tempfile
            import base64
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(response_text)
                temp_path = f.name
            
            with open(temp_path, 'rb') as f:
                file_content = base64.b64encode(f.read()).decode()
            
            # Create attachment
            attachment = self.env['ir.attachment'].create({
                'name': f'GPSWOX_API_Response_{fields.Datetime.now()}.txt',
                'type': 'binary',
                'datas': file_content,
                'res_model': self._name,
                'res_id': self.id,
                'mimetype': 'text/plain',
            })
            
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }
            
        except Exception as e:
            import traceback
            return self._show_error('Error', f'{str(e)}\n\n{traceback.format_exc()}')
        """Delete all devices for this configuration"""
        self.ensure_one()
        
        device_count = len(self.device_ids)
        
        if device_count == 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Devices',
                    'message': 'No devices found to delete.',
                    'type': 'info',
                    'sticky': False,
                }
            }
        
        self.device_ids.unlink()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Devices Deleted',
                'message': f'Successfully deleted {device_count} device(s).',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def _create_demo_devices(self):
        """Create demo devices for testing"""
        from datetime import datetime
        
        demo_devices = [
            {
                'name': 'Vehicle 1 - Riyadh',
                'device_id': 'DEV001',
                'imei': '123456789012345',
                'latitude': 24.7136,
                'longitude': 46.6753,
                'speed': 45.5,
                'status': 'moving',
                'address': 'King Fahd Road, Riyadh, Saudi Arabia',
                'vehicle_id': 'VEH-001',
                'driver_name': 'Ahmad Al-Rashid',
            },
            {
                'name': 'Vehicle 2 - Jeddah',
                'device_id': 'DEV002',
                'imei': '234567890123456',
                'latitude': 21.4225,
                'longitude': 39.8262,
                'speed': 0,
                'status': 'idle',
                'address': 'Palestine Street, Jeddah, Saudi Arabia',
                'vehicle_id': 'VEH-002',
                'driver_name': 'Mohammed Hassan',
            },
            {
                'name': 'Vehicle 3 - Dammam',
                'device_id': 'DEV003',
                'imei': '345678901234567',
                'latitude': 26.4207,
                'longitude': 50.0888,
                'speed': 62.3,
                'status': 'online',
                'address': 'Dhahran Highway, Dammam, Saudi Arabia',
                'vehicle_id': 'VEH-003',
                'driver_name': 'Khalid Ahmed',
            },
            {
                'name': 'Vehicle 4 - Abu Dhabi',
                'device_id': 'DEV004',
                'imei': '456789012345678',
                'latitude': 24.4539,
                'longitude': 54.3773,
                'speed': 0,
                'status': 'offline',
                'address': 'Sheikh Zayed Road, Abu Dhabi, UAE',
                'vehicle_id': 'VEH-004',
                'driver_name': 'Abdullah Saeed',
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for device_info in demo_devices:
            existing_device = self.env['tracking.device'].search([
                ('device_id', '=', device_info['device_id']),
                ('config_id', '=', self.id)
            ], limit=1)
            
            vals = {
                'name': device_info['name'],
                'device_id': device_info['device_id'],
                'imei': device_info['imei'],
                'config_id': self.id,
                'latitude': device_info['latitude'],
                'longitude': device_info['longitude'],
                'speed': device_info['speed'],
                'address': device_info['address'],
                'status': device_info['status'],
                'vehicle_id': device_info['vehicle_id'],
                'driver_name': device_info['driver_name'],
                'last_update': datetime.now(),
            }
            
            if existing_device:
                existing_device.write(vals)
                updated_count += 1
            else:
                self.env['tracking.device'].create(vals)
                created_count += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Demo Devices Created',
                'message': f'Created: {created_count}, Updated: {updated_count} demo devices',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def _process_api_devices(self, devices_data):
        """Process devices from API response"""
        from datetime import datetime
        
        created_count = 0
        updated_count = 0
        
        # Support different API response formats
        if isinstance(devices_data, list):
            # Direct list of devices
            devices_list = devices_data
        elif isinstance(devices_data, dict):
            # Dictionary with 'devices' key or other possible keys
            devices_list = (devices_data.get('devices') or 
                          devices_data.get('data') or 
                          devices_data.get('items') or 
                          devices_data.get('results') or
                          [devices_data])  # Single device object
        else:
            raise ValueError(f'Unexpected API response format: {type(devices_data)}')
        
        if not devices_list:
            return self._show_error('No Devices', 'API returned no devices')
        
        for device_info in devices_list:
            # Handle different field naming conventions
            device_id = (device_info.get('id') or 
                        device_info.get('device_id') or 
                        device_info.get('deviceId') or 
                        device_info.get('uniqueId'))
            
            if not device_id:
                continue  # Skip devices without ID
            
            existing_device = self.env['tracking.device'].search([
                ('device_id', '=', str(device_id)),
                ('config_id', '=', self.id)
            ], limit=1)
            
            # Extract coordinates
            lat = (device_info.get('latitude') or 
                  device_info.get('lat') or 
                  device_info.get('position', {}).get('latitude') or 
                  0.0)
            
            lng = (device_info.get('longitude') or 
                  device_info.get('lng') or 
                  device_info.get('lon') or 
                  device_info.get('position', {}).get('longitude') or 
                  0.0)
            
            vals = {
                'name': device_info.get('name') or device_info.get('label') or f'Device {device_id}',
                'device_id': str(device_id),
                'imei': device_info.get('imei') or device_info.get('uniqueId') or '',
                'config_id': self.id,
                'latitude': float(lat) if lat else 0.0,
                'longitude': float(lng) if lng else 0.0,
                'speed': float(device_info.get('speed', 0) or 0),
                'address': device_info.get('address') or device_info.get('location') or '',
                'status': device_info.get('status') or device_info.get('state') or 'offline',
                'vehicle_id': device_info.get('vehicle_id') or device_info.get('vehicleId') or '',
                'driver_name': device_info.get('driver_name') or device_info.get('driver') or '',
                'last_update': datetime.now(),
            }
            
            if existing_device:
                existing_device.write(vals)
                updated_count += 1
            else:
                self.env['tracking.device'].create(vals)
                created_count += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Devices Fetched Successfully',
                'message': f'Total: {created_count + updated_count} devices (Created: {created_count}, Updated: {updated_count})',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def _show_error(self, title, message):
        """Show error notification"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'type': 'danger',
                'sticky': True,
            }
        }
