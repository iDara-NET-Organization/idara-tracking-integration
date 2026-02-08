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
        # Add your API connection test logic here
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Connection Test',
                'message': 'Connection successful!',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def fetch_devices_from_api(self):
        """Fetch all devices from the tracking API"""
        self.ensure_one()
        from datetime import datetime
        
        # Option 1: Create demo devices (for testing)
        # Remove this and uncomment Option 2 when you have a real API
        return self._create_demo_devices()
        
        # Option 2: Real API integration (uncomment when ready)
        # import requests
        # import json
        # 
        # try:
        #     # Prepare API request
        #     headers = {
        #         'Authorization': f'Bearer {self.api_key}',
        #         'Content-Type': 'application/json'
        #     }
        #     
        #     url = f'{self.api_url}/devices'
        #     
        #     # Make API request
        #     response = requests.get(url, headers=headers, timeout=30)
        #     
        #     # Check if response is empty
        #     if not response.text:
        #         raise ValueError('API returned empty response')
        #     
        #     # Check response status
        #     response.raise_for_status()
        #     
        #     # Parse JSON
        #     try:
        #         devices_data = response.json()
        #     except json.JSONDecodeError:
        #         raise ValueError(f'Invalid JSON response: {response.text[:200]}')
        #     
        #     # Process devices
        #     return self._process_api_devices(devices_data)
        #     
        # except requests.exceptions.ConnectionError:
        #     return self._show_error('Connection Error', 'Could not connect to API. Check your API URL.')
        # except requests.exceptions.Timeout:
        #     return self._show_error('Timeout Error', 'API request timed out after 30 seconds.')
        # except requests.exceptions.HTTPError as e:
        #     return self._show_error('HTTP Error', f'API returned error: {e.response.status_code}')
        # except ValueError as e:
        #     return self._show_error('Data Error', str(e))
        # except Exception as e:
        #     return self._show_error('Unexpected Error', f'An error occurred: {str(e)}')
    
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
        
        for device_info in devices_data.get('devices', []):
            existing_device = self.env['tracking.device'].search([
                ('device_id', '=', device_info.get('id')),
                ('config_id', '=', self.id)
            ], limit=1)
            
            vals = {
                'name': device_info.get('name', 'Unknown Device'),
                'device_id': device_info.get('id'),
                'imei': device_info.get('imei'),
                'config_id': self.id,
                'latitude': device_info.get('latitude', 0.0),
                'longitude': device_info.get('longitude', 0.0),
                'speed': device_info.get('speed', 0.0),
                'address': device_info.get('address', ''),
                'status': device_info.get('status', 'offline'),
                'vehicle_id': device_info.get('vehicle_id', ''),
                'driver_name': device_info.get('driver_name', ''),
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
                'message': f'Created: {created_count}, Updated: {updated_count}',
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
