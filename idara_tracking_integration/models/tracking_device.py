# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TrackingDevice(models.Model):
    _name = 'tracking.device'
    _description = 'Tracking Device'
    _rec_name = 'name'

    name = fields.Char(string='Device Name', required=True)
    device_id = fields.Char(string='Device ID', required=True)
    imei = fields.Char(string='IMEI')
    config_id = fields.Many2one('tracking.config', string='Configuration', required=True)
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string='Fleet Vehicle', help='Link this device to a fleet vehicle')
    active = fields.Boolean(string='Active', default=True)
    last_update = fields.Datetime(string='Last Update')
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))
    speed = fields.Float(string='Speed (km/h)')
    address = fields.Char(string='Current Address')
    status = fields.Selection([
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('moving', 'Moving'),
        ('idle', 'Idle'),
    ], string='Status', default='offline')
    vehicle_id = fields.Char(string='Vehicle ID')
    driver_name = fields.Char(string='Driver Name')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    def refresh_location(self):
        self.ensure_one()
        # Add your location refresh logic here
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Location Refresh',
                'message': 'Location updated successfully!',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_view_fleet_vehicle(self):
        """Open linked fleet vehicle"""
        self.ensure_one()
        if not self.fleet_vehicle_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Vehicle',
                    'message': 'This device is not linked to any fleet vehicle.',
                    'type': 'warning',
                }
            }
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fleet Vehicle',
            'res_model': 'fleet.vehicle',
            'res_id': self.fleet_vehicle_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    @api.model
    def create(self, vals):
        """Override create to auto-link with fleet vehicle if needed"""
        device = super(TrackingDevice, self).create(vals)
        
        # Try to auto-link with fleet vehicle if fleet_vehicle_id is provided
        if device.fleet_vehicle_id and not device.fleet_vehicle_id.tracking_device_id:
            device.fleet_vehicle_id.tracking_device_id = device.id
        
        return device
    
    def write(self, vals):
        """Override write to sync fleet vehicle link"""
        result = super(TrackingDevice, self).write(vals)
        
        # Update fleet vehicle link if changed
        if 'fleet_vehicle_id' in vals:
            for device in self:
                if device.fleet_vehicle_id and device.fleet_vehicle_id.tracking_device_id != device:
                    device.fleet_vehicle_id.tracking_device_id = device.id
        
        return result
    
    def action_view_history(self):
        """Open device history/route viewer"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/idara_tracking/device_history?device_id={self.id}',
            'target': 'new',
        }
    
    def get_device_history(self, from_datetime, to_datetime):
        """
        Fetch device history from GPSWOX API
        
        :param from_datetime: Start datetime (string format: YYYY-MM-DD HH:MM:SS)
        :param to_datetime: End datetime (string format: YYYY-MM-DD HH:MM:SS)
        :return: Dictionary with history data or error
        """
        self.ensure_one()
        
        if not self.config_id:
            return {'status': 'error', 'message': 'No configuration linked to this device'}
        
        if not self.config_id.username or not self.config_id.password:
            return {'status': 'error', 'message': 'Configuration missing username or password'}
        
        try:
            import requests
            from datetime import datetime
            import logging
            
            _logger = logging.getLogger(__name__)
            
            # Parse datetime strings
            try:
                from_dt = datetime.strptime(from_datetime, '%Y-%m-%d %H:%M:%S')
                to_dt = datetime.strptime(to_datetime, '%Y-%m-%d %H:%M:%S')
            except:
                return {'status': 'error', 'message': 'Invalid datetime format. Use: YYYY-MM-DD HH:MM:SS'}
            
            # Step 1: Login to get user_api_hash
            login_url = self.config_id.api_url.strip()
            if not login_url.startswith('http'):
                login_url = f'https://{login_url}'
            if not login_url.endswith('/api/login'):
                login_url = f'{login_url}/api/login' if login_url.endswith('/') else f'{login_url}/api/login'
            
            login_data = {
                'email': self.config_id.username,
                'password': self.config_id.password
            }
            
            login_response = requests.post(login_url, data=login_data, timeout=30)
            
            if login_response.status_code != 200:
                return {'status': 'error', 'message': f'Login failed with status {login_response.status_code}'}
            
            login_result = login_response.json()
            
            if login_result.get('status') != 1:
                return {'status': 'error', 'message': 'Authentication failed'}
            
            user_api_hash = login_result.get('user_api_hash')
            if not user_api_hash:
                return {'status': 'error', 'message': 'Could not get API hash'}
            
            # Step 2: Get history
            history_url = self.config_id.api_url.strip()
            if not history_url.startswith('http'):
                history_url = f'https://{history_url}'
            if not history_url.endswith('/api/get_history'):
                history_url = f'{history_url}/api/get_history' if history_url.endswith('/') else f'{history_url}/api/get_history'
            
            # Format parameters
            history_params = {
                'user_api_hash': user_api_hash,
                'device_id': self.device_id,
                'from_date': from_dt.strftime('%Y-%m-%d'),
                'from_time': from_dt.strftime('%H:%M:%S'),
                'to_date': to_dt.strftime('%Y-%m-%d'),
                'to_time': to_dt.strftime('%H:%M:%S'),
                'snap_to_road': 'true',
                'lang': 'en'
            }
            
            _logger.info(f'Fetching history from {history_url} with params: {history_params}')
            
            history_response = requests.get(history_url, params=history_params, timeout=60)
            
            if history_response.status_code != 200:
                return {'status': 'error', 'message': f'Failed to get history: {history_response.status_code}'}
            
            history_data = history_response.json()
            
            # Process and return the data
            return {
                'status': 'success',
                'data': history_data
            }
            
        except Exception as e:
            import traceback
            _logger = logging.getLogger(__name__)
            _logger.error(traceback.format_exc())
            return {'status': 'error', 'message': str(e)}
