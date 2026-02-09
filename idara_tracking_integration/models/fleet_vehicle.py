# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    tracking_device_id = fields.Many2one(
        'tracking.device', 
        string='Tracking Device',
        help='GPS tracking device assigned to this vehicle'
    )
    device_status = fields.Selection(
        related='tracking_device_id.status',
        string='Device Status',
        readonly=True
    )
    current_location = fields.Char(
        related='tracking_device_id.address',
        string='Current Location',
        readonly=True
    )
    last_known_speed = fields.Float(
        related='tracking_device_id.speed',
        string='Last Speed (km/h)',
        readonly=True
    )
    device_latitude = fields.Float(
        related='tracking_device_id.latitude',
        string='Latitude',
        readonly=True
    )
    device_longitude = fields.Float(
        related='tracking_device_id.longitude',
        string='Longitude',
        readonly=True
    )
    device_last_update = fields.Datetime(
        related='tracking_device_id.last_update',
        string='Last GPS Update',
        readonly=True
    )
    
    def action_view_on_map(self):
        """Open device location on map"""
        self.ensure_one()
        if not self.tracking_device_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Device',
                    'message': 'This vehicle has no tracking device assigned.',
                    'type': 'warning',
                }
            }
        
        # Redirect to map view filtered for this device
        return {
            'type': 'ir.actions.act_url',
            'url': f'/idara_tracking/map?device_id={self.tracking_device_id.id}',
            'target': 'new',
        }
    
    def action_refresh_location(self):
        """Refresh device location"""
        self.ensure_one()
        if self.tracking_device_id:
            return self.tracking_device_id.refresh_location()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'No Device',
                'message': 'This vehicle has no tracking device assigned.',
                'type': 'warning',
            }
        }
