# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json

class TrackingController(http.Controller):

    @http.route('/tracking/device/location/<int:device_id>', type='json', auth='user')
    def get_device_location(self, device_id):
        """Get device location data for map display"""
        device = request.env['tracking.device'].browse(device_id)
        if not device.exists():
            return {'error': 'Device not found'}
        
        return {
            'id': device.id,
            'name': device.name,
            'latitude': device.last_latitude,
            'longitude': device.last_longitude,
            'speed': device.last_speed,
            'heading': device.last_heading,
            'status': device.status,
            'last_update': device.last_update.isoformat() if device.last_update else None,
        }

    @http.route('/tracking/devices/locations', type='json', auth='user')
    def get_all_devices_locations(self):
        """Get all active devices locations for live map"""
        devices = request.env['tracking.device'].search([
            ('active', '=', True),
            ('last_latitude', '!=', 0),
            ('last_longitude', '!=', 0)
        ])
        
        return [{
            'id': device.id,
            'name': device.name,
            'vehicle_name': device.vehicle_name or '',
            'latitude': device.last_latitude,
            'longitude': device.last_longitude,
            'speed': device.last_speed,
            'heading': device.last_heading,
            'status': device.status,
            'ignition': device.ignition_status,
            'last_update': device.last_update.isoformat() if device.last_update else None,
        } for device in devices]

    @http.route('/tracking/device/route/<int:device_id>', type='json', auth='user')
    def get_device_route(self, device_id, hours=24):
        """Get device route history"""
        from datetime import datetime, timedelta
        
        device = request.env['tracking.device'].browse(device_id)
        if not device.exists():
            return {'error': 'Device not found'}
        
        # Get locations from last X hours
        since = datetime.now() - timedelta(hours=hours)
        locations = request.env['tracking.location'].search([
            ('device_id', '=', device_id),
            ('position_time', '>=', since)
        ], order='position_time asc')
        
        return [{
            'latitude': loc.latitude,
            'longitude': loc.longitude,
            'speed': loc.speed,
            'time': loc.position_time.isoformat(),
        } for loc in locations]
