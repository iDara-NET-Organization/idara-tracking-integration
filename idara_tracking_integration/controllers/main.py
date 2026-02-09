# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json


class TrackingMapController(http.Controller):

    @http.route('/idara_tracking/map', type='http', auth='user', website=False)
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
        
        # Get Google Maps API key from configuration
        config = request.env['tracking.config'].sudo().search([('active', '=', True)], limit=1)
        google_maps_key = config.google_maps_api_key if config else ''
        
        return request.render('idara_tracking_integration.tracking_map_template', {
            'devices': json.dumps(devices_data),
            'google_maps_key': google_maps_key,
            'device_count': len(devices_data),
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
        
        return {'devices': devices_data, 'count': len(devices_data)}

