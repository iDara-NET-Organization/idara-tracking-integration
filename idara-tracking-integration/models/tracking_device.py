# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TrackingDevice(models.Model):
    _name = 'tracking.device'
    _description = 'AVL Tracking Device'
    _rec_name = 'name'
    _order = 'name'

    # Basic Information
    name = fields.Char(string='Device Name', required=True, index=True)
    device_id = fields.Char(string='Device ID', required=True, index=True)
    imei = fields.Char(string='IMEI', index=True)
    device_model = fields.Char(string='Device Model')
    active = fields.Boolean(string='Active', default=True)
    
    # Configuration
    config_id = fields.Many2one('tracking.config', string='Configuration', required=True)
    
    # Current Status
    last_latitude = fields.Float(string='Last Latitude', digits=(10, 7))
    last_longitude = fields.Float(string='Last Longitude', digits=(10, 7))
    last_speed = fields.Float(string='Last Speed (km/h)')
    last_altitude = fields.Float(string='Last Altitude (m)')
    last_heading = fields.Float(string='Last Heading (degrees)')
    last_update = fields.Datetime(string='Last Update')
    last_position_time = fields.Datetime(string='Last Position Time')
    
    # Vehicle Information
    vehicle_name = fields.Char(string='Vehicle Name')
    plate_number = fields.Char(string='Plate Number')
    driver_name = fields.Char(string='Driver Name')
    
    # Status and Alerts
    status = fields.Selection([
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('moving', 'Moving'),
        ('stopped', 'Stopped'),
        ('idle', 'Idle')
    ], string='Status', default='offline')
    
    ignition_status = fields.Boolean(string='Ignition')
    power_status = fields.Selection([
        ('normal', 'Normal'),
        ('low', 'Low Battery'),
        ('charging', 'Charging'),
        ('disconnected', 'Power Disconnected')
    ], string='Power Status', default='normal')
    
    # Alerts
    has_alert = fields.Boolean(string='Has Alert', default=False)
    alert_type = fields.Char(string='Alert Type')
    
    # Statistics
    total_distance = fields.Float(string='Total Distance (km)', readonly=True)
    total_running_time = fields.Float(string='Total Running Time (hours)', readonly=True)
    
    # Relations
    location_ids = fields.One2many('tracking.location', 'device_id', string='Location History')
    location_count = fields.Integer(string='Location Records', compute='_compute_location_count', store=True)
    
    @api.depends('location_ids')
    def _compute_location_count(self):
        for record in self:
            record.location_count = len(record.location_ids)
    
    def action_view_on_map(self):
        """Open device location on map"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Device Location',
            'res_model': 'tracking.device',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }
    
    def action_view_locations(self):
        """View location history"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Location History',
            'res_model': 'tracking.location',
            'view_mode': 'tree,form',
            'domain': [('device_id', '=', self.id)],
            'context': {'default_device_id': self.id},
        }
    
    def action_sync_device(self):
        """Sync specific device"""
        self.ensure_one()
        api = self.env['tracking.api'].create({})
        return api.sync_device_location(self)
