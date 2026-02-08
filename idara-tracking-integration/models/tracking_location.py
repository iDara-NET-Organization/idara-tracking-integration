# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TrackingLocation(models.Model):
    _name = 'tracking.location'
    _description = 'Device Location History'
    _order = 'position_time desc'
    _rec_name = 'display_name'

    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)
    
    # Relations
    device_id = fields.Many2one('tracking.device', string='Device', required=True, ondelete='cascade', index=True)
    config_id = fields.Many2one('tracking.config', string='Configuration', related='device_id.config_id', store=True)
    
    # Location Data
    latitude = fields.Float(string='Latitude', required=True, digits=(10, 7))
    longitude = fields.Float(string='Longitude', required=True, digits=(10, 7))
    altitude = fields.Float(string='Altitude (m)')
    speed = fields.Float(string='Speed (km/h)')
    heading = fields.Float(string='Heading (degrees)')
    accuracy = fields.Float(string='GPS Accuracy (m)')
    
    # Timing
    position_time = fields.Datetime(string='Position Time', required=True, index=True)
    server_time = fields.Datetime(string='Server Time', default=fields.Datetime.now)
    
    # Vehicle Status
    ignition = fields.Boolean(string='Ignition')
    movement_status = fields.Selection([
        ('moving', 'Moving'),
        ('stopped', 'Stopped'),
        ('idle', 'Idle')
    ], string='Movement Status')
    
    # Address (if reverse geocoded)
    address = fields.Char(string='Address')
    
    # Additional Data
    satellites = fields.Integer(string='Satellites')
    battery_level = fields.Float(string='Battery Level (%)')
    fuel_level = fields.Float(string='Fuel Level (%)')
    
    # Raw Data
    raw_data = fields.Text(string='Raw API Response')
    
    @api.depends('device_id.name', 'position_time')
    def _compute_display_name(self):
        for record in self:
            if record.device_id and record.position_time:
                record.display_name = f"{record.device_id.name} - {record.position_time}"
            else:
                record.display_name = "New Location"
    
    def action_view_on_map(self):
        """View this location on map"""
        self.ensure_one()
        # Open in external map service
        if self.latitude and self.longitude:
            url = f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
