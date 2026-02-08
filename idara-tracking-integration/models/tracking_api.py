# -*- coding: utf-8 -*-

import requests
import json
import logging
from datetime import datetime
from odoo import models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class TrackingAPI(models.TransientModel):
    _name = 'tracking.api'
    _description = 'Tracking API Service'

    def _get_headers(self, config):
        """Generate API headers"""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def _make_request(self, config, endpoint, method='GET', data=None, params=None):
        """Make API request"""
        try:
            url = f"{config.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
            
            headers = self._get_headers(config)
            
            # Add authentication parameters
            if params is None:
                params = {}
            params.update({
                'user_api_hash': config.user_api_hash or config.api_hash,
                'lang': 'en'
            })
            
            _logger.info(f"Making {method} request to: {url}")
            
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, params=params, json=data, timeout=30)
            else:
                raise UserError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            return {
                'success': True,
                'data': response.json(),
                'status_code': response.status_code
            }
            
        except requests.exceptions.Timeout:
            error_msg = "API request timed out"
            _logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except requests.exceptions.ConnectionError:
            error_msg = "Failed to connect to API server"
            _logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error: {e.response.status_code} - {e.response.text}"
            _logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            _logger.error(error_msg)
            return {'success': False, 'error': error_msg}

    def test_connection(self, config):
        """Test API connection"""
        result = self._make_request(config, '/get_devices')
        return result

    def get_devices(self, config):
        """Get all devices from API"""
        result = self._make_request(config, '/get_devices')
        
        if result.get('success'):
            data = result.get('data', {})
            # Handle different response structures
            if isinstance(data, list):
                return {'success': True, 'devices': data}
            elif isinstance(data, dict):
                devices = data.get('data', []) or data.get('devices', [])
                return {'success': True, 'devices': devices}
        
        return result

    def get_device_location(self, config, device_id):
        """Get specific device location"""
        params = {'device_id': device_id}
        result = self._make_request(config, '/get_device_data', params=params)
        return result

    def sync_all_devices(self, config):
        """Sync all devices from API"""
        result = self.get_devices(config)
        
        if not result.get('success'):
            raise UserError(f"Failed to fetch devices: {result.get('error')}")
        
        devices = result.get('devices', [])
        Device = self.env['tracking.device']
        
        created_count = 0
        updated_count = 0
        
        for device_data in devices:
            device_id = str(device_data.get('id') or device_data.get('device_id'))
            
            existing_device = Device.search([
                ('device_id', '=', device_id),
                ('config_id', '=', config.id)
            ], limit=1)
            
            vals = self._prepare_device_vals(config, device_data)
            
            if existing_device:
                existing_device.write(vals)
                updated_count += 1
            else:
                Device.create(vals)
                created_count += 1
        
        config.write({'last_sync': fields.Datetime.now()})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Devices Synchronized',
                'message': f'Created: {created_count}, Updated: {updated_count}',
                'type': 'success',
                'sticky': False,
            }
        }

    def sync_all_locations(self, config):
        """Sync locations for all active devices"""
        Device = self.env['tracking.device']
        devices = Device.search([
            ('config_id', '=', config.id),
            ('active', '=', True)
        ])
        
        success_count = 0
        error_count = 0
        
        for device in devices:
            try:
                self.sync_device_location(device)
                success_count += 1
            except Exception as e:
                _logger.error(f"Failed to sync device {device.name}: {str(e)}")
                error_count += 1
        
        config.write({'last_sync': fields.Datetime.now()})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Locations Synchronized',
                'message': f'Success: {success_count}, Errors: {error_count}',
                'type': 'success' if error_count == 0 else 'warning',
                'sticky': False,
            }
        }

    def sync_device_location(self, device):
        """Sync location for specific device"""
        result = self.get_device_location(device.config_id, device.device_id)
        
        if not result.get('success'):
            raise UserError(f"Failed to fetch location: {result.get('error')}")
        
        data = result.get('data', {})
        if isinstance(data, dict):
            location_data = data.get('data') or data
        else:
            location_data = data
        
        # Update device current location
        device_vals = {
            'last_latitude': float(location_data.get('lat') or location_data.get('latitude', 0)),
            'last_longitude': float(location_data.get('lng') or location_data.get('longitude', 0)),
            'last_speed': float(location_data.get('speed', 0)),
            'last_altitude': float(location_data.get('altitude', 0)),
            'last_heading': float(location_data.get('course') or location_data.get('heading', 0)),
            'last_update': fields.Datetime.now(),
        }
        
        # Parse position time
        position_time_str = location_data.get('dt_tracker') or location_data.get('time')
        if position_time_str:
            try:
                device_vals['last_position_time'] = datetime.strptime(position_time_str, '%Y-%m-%d %H:%M:%S')
            except:
                pass
        
        # Update status
        if location_data.get('ignition'):
            device_vals['ignition_status'] = bool(int(location_data.get('ignition', 0)))
        
        if float(location_data.get('speed', 0)) > 5:
            device_vals['status'] = 'moving'
        else:
            device_vals['status'] = 'stopped'
        
        device.write(device_vals)
        
        # Create location history record
        Location = self.env['tracking.location']
        location_vals = {
            'device_id': device.id,
            'latitude': device_vals['last_latitude'],
            'longitude': device_vals['last_longitude'],
            'speed': device_vals['last_speed'],
            'altitude': device_vals['last_altitude'],
            'heading': device_vals['last_heading'],
            'position_time': device_vals.get('last_position_time', fields.Datetime.now()),
            'ignition': device_vals.get('ignition_status', False),
            'movement_status': 'moving' if float(location_data.get('speed', 0)) > 5 else 'stopped',
            'raw_data': json.dumps(location_data),
        }
        
        Location.create(location_vals)
        
        return True

    def _prepare_device_vals(self, config, device_data):
        """Prepare device values from API data"""
        return {
            'config_id': config.id,
            'device_id': str(device_data.get('id') or device_data.get('device_id')),
            'name': device_data.get('name') or device_data.get('label', 'Unknown Device'),
            'imei': device_data.get('imei'),
            'device_model': device_data.get('model') or device_data.get('device_model'),
            'vehicle_name': device_data.get('plate_number') or device_data.get('vehicle_name'),
            'plate_number': device_data.get('plate_number'),
        }
