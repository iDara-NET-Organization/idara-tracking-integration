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
