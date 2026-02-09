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
        """Fetch all devices from the tracking API"""
        self.ensure_one()
        
        # Validate configuration
        if not self.api_url:
            return self._show_error('Configuration Error', 'API URL is required. Please configure it first.')
        
        import requests
        import json
        from datetime import datetime
        import logging
        
        _logger = logging.getLogger(__name__)
        
        try:
            # Prepare API request
            headers = {'Content-Type': 'application/json'}
            
            # Add authentication
            auth = None
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            elif self.username and self.password:
                auth = (self.username, self.password)
            
            # Build URL
            url = self.api_url
            if not url.startswith('http'):
                url = f'https://{url}'
            if not url.endswith('/devices'):
                url = f'{url}/devices' if url.endswith('/') else f'{url}/devices'
            
            _logger.info(f'Fetching devices from: {url}')
            
            # Make API request
            response = requests.get(url, headers=headers, auth=auth, timeout=30)
            
            _logger.info(f'API Response Status: {response.status_code}')
            _logger.info(f'API Response Headers: {response.headers}')
            _logger.info(f'API Response Text (first 500 chars): {response.text[:500]}')
            
            # Check response status first
            if response.status_code == 401:
                return self._show_error('Authentication Error', 'Invalid API credentials. Check your API Key or Username/Password.')
            elif response.status_code == 404:
                return self._show_error('Not Found', f'API endpoint not found: {url}. Please check your API URL.')
            elif response.status_code >= 400:
                return self._show_error('API Error', f'API returned error {response.status_code}: {response.text[:200]}')
            
            # Check if response is empty
            if not response.text or response.text.strip() == '':
                return self._show_error('Empty Response', 'API returned empty response. Please check if there are any devices in your tracking system.')
            
            # Try to parse JSON
            try:
                devices_data = response.json()
            except json.JSONDecodeError as e:
                return self._show_error(
                    'Invalid JSON', 
                    f'API returned invalid JSON. Response: {response.text[:200]}... Error: {str(e)}'
                )
            
            # Process devices
            return self._process_api_devices(devices_data)
            
        except requests.exceptions.ConnectionError as e:
            return self._show_error('Connection Error', f'Could not connect to API at {self.api_url}. Check your internet connection and API URL. Error: {str(e)[:100]}')
        except requests.exceptions.Timeout:
            return self._show_error('Timeout Error', f'API request timed out after 30 seconds. The server at {self.api_url} is not responding.')
        except requests.exceptions.RequestException as e:
            return self._show_error('Request Error', f'Failed to make API request: {str(e)[:200]}')
        except Exception as e:
            _logger.exception('Unexpected error in fetch_devices_from_api')
            return self._show_error('Unexpected Error', f'An unexpected error occurred: {str(e)[:200]}')
    
    def create_demo_devices(self):
        """Create demo devices for testing - separate button"""
        return self._create_demo_devices()
    
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
