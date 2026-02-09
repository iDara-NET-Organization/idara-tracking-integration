# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json


class TrackingMapController(http.Controller):

    @http.route('/idara_tracking/map', type='http', auth='user', website=true)
    def tracking_map(self, **kwargs):
        """Display interactive map with all devices"""
        # Fetch all active devices
        devices = request.env['tracking.device'].sudo().search([('active', '=', True)])
        
        devices_data = []
        for device in devices:
            # Only add devices with valid coordinates
            if device.latitude and device.longitude:
                devices_data.append({
                    'id': device.id,
                    'name': device.name or device.device_id or 'Unknown',
                    'device_id': device.device_id or '',
                    'latitude': float(device.latitude),
                    'longitude': float(device.longitude),
                    'speed': float(device.speed) if device.speed else 0.0,
                    'status': device.status or 'offline',
                    'driver_name': device.driver_name or '',
                    'vehicle_id': device.vehicle_id or '',
                    'address': device.address or '',
                    'last_update': str(device.last_update) if device.last_update else '',
                })
        
        # Get configuration
        config = request.env['tracking.config'].sudo().search([('active', '=', True)], limit=1)
        google_maps_key = config.google_maps_api_key if config else ''
        refresh_interval = config.auto_refresh_interval if config else 30
        map_provider = config.map_provider if config else 'osm'
        timezone_offset = config.timezone_offset if config else 3
        
        return request.render('idara_tracking_integration.tracking_map_template', {
            'devices_json': json.dumps(devices_data),
            'google_maps_key': google_maps_key,
            'device_count': len(devices_data),
            'refresh_interval': refresh_interval * 1000,
            'map_provider': map_provider,
            'timezone_offset': timezone_offset,
        })
    
    @http.route('/idara_tracking/devices/json', type='json', auth='user')
    def get_devices_json(self, **kwargs):
        """API endpoint to get devices as JSON for live updates"""
        devices = request.env['tracking.device'].sudo().search([('active', '=', True)])
        
        devices_data = []
        for device in devices:
            if device.latitude and device.longitude:
                devices_data.append({
                    'id': device.id,
                    'name': device.name or device.device_id or 'Unknown',
                    'device_id': device.device_id or '',
                    'latitude': float(device.latitude),
                    'longitude': float(device.longitude),
                    'speed': float(device.speed) if device.speed else 0.0,
                    'status': device.status or 'offline',
                    'driver_name': device.driver_name or '',
                    'vehicle_id': device.vehicle_id or '',
                    'address': device.address or '',
                    'last_update': str(device.last_update) if device.last_update else '',
                })
        
        # Return devices directly as array (not wrapped in object)
        return devices_data
    
    @http.route('/idara_tracking/device_history', type='http', auth='user', website=False)
    def device_history_viewer(self, device_id=None, **kwargs):
        """Display device history/route viewer page"""
        # Get all active devices for dropdown
        devices = request.env['tracking.device'].sudo().search([('active', '=', True)])
        
        # Get selected device
        selected_device = None
        if device_id:
            selected_device = request.env['tracking.device'].sudo().browse(int(device_id))
        
        # Get Google Maps API key
        config = request.env['tracking.config'].sudo().search([('active', '=', True)], limit=1)
        google_maps_key = config.google_maps_api_key if config else ''
        
        return request.render('idara_tracking_integration.device_history_template', {
            'devices': devices,
            'selected_device': selected_device,
            'google_maps_key': google_maps_key,
        })
    
    @http.route('/idara_tracking/get_device_history', type='json', auth='user')
    def get_device_history(self, device_id, from_datetime, to_datetime, **kwargs):
        """API endpoint to get device history data"""
        try:
            device = request.env['tracking.device'].sudo().browse(int(device_id))
            
            if not device.exists():
                return {'status': 'error', 'message': 'Device not found'}
            
            # Get history from GPSWOX API
            result = device.get_device_history(from_datetime, to_datetime)
            
            return result
            
        except Exception as e:
            import traceback
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(traceback.format_exc())
            return {'status': 'error', 'message': str(e)}

