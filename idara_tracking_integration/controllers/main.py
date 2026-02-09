# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json


class TrackingMapController(http.Controller):

    @http.route('/idara_tracking/map', type='http', auth='user', website=False)
    def tracking_map(self, **kwargs):
        """Display interactive map with all devices"""
        devices = request.env['tracking.device'].search([])
        
        devices_data = []
        for device in devices:
            devices_data.append({
                'id': device.id,
                'name': device.name,
                'device_id': device.device_id,
                'latitude': device.latitude,
                'longitude': device.longitude,
                'speed': device.speed,
                'status': device.status,
                'driver_name': device.driver_name or '',
                'vehicle_id': device.vehicle_id or '',
                'address': device.address or '',
                'last_update': str(device.last_update) if device.last_update else '',
            })
        
        # Get Google Maps API key from configuration
        config = request.env['tracking.config'].search([], limit=1)
        google_maps_key = config.google_maps_api_key if config else ''
        
        return request.render('idara_tracking_integration.tracking_map_template', {
            'devices': json.dumps(devices_data),
            'google_maps_key': google_maps_key,
            'device_count': len(devices_data),
        })
    
    @http.route('/idara_tracking/devices/json', type='json', auth='user')
    def get_devices_json(self, **kwargs):
        """API endpoint to get devices as JSON"""
        devices = request.env['tracking.device'].search([])
        
        devices_data = []
        for device in devices:
            devices_data.append({
                'id': device.id,
                'name': device.name,
                'device_id': device.device_id,
                'latitude': device.latitude,
                'longitude': device.longitude,
                'speed': device.speed,
                'status': device.status,
                'driver_name': device.driver_name or '',
                'vehicle_id': device.vehicle_id or '',
                'address': device.address or '',
                'last_update': str(device.last_update) if device.last_update else '',
            })
        
        return {'devices': devices_data}
