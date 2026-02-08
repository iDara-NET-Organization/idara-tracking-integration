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
