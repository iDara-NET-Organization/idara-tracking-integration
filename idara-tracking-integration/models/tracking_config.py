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
        import requests
        import json
        from datetime import datetime
        
        try:
            # Prepare API request
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Example API endpoint - adjust to your actual API
            url = f'{self.api_url}/devices'
            
            # Make API request
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            devices_data = response.json()
            
            # Process devices
            created_count = 0
            updated_count = 0
            
            for device_info in devices_data.get('devices', []):
                # Check if device already exists
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
            
        except requests.exceptions.RequestException as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'API Error',
                    'message': f'Failed to fetch devices: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': f'Unexpected error: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }
