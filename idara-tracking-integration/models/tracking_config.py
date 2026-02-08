# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TrackingConfig(models.Model):
    _name = 'tracking.config'
    _description = 'Tracking API Configuration'
    _rec_name = 'name'

    name = fields.Char(string='Configuration Name', required=True, default='Idara Tracking Config')
    api_url = fields.Char(
        string='API Base URL',
        required=True,
        default='https://tracking.idara.net/api'
    )
    api_key = fields.Char(string='API Key', required=True)
    api_hash = fields.Char(string='API Hash/Token', required=True)
    user_api_hash = fields.Char(string='User API Hash')
    active = fields.Boolean(string='Active', default=True)
    sync_interval = fields.Integer(
        string='Sync Interval (minutes)',
        default=5,
        help='How often to sync device locations (in minutes)'
    )
    last_sync = fields.Datetime(string='Last Synchronization', readonly=True)
    connection_status = fields.Selection([
        ('not_tested', 'Not Tested'),
        ('success', 'Connected'),
        ('failed', 'Connection Failed')
    ], string='Connection Status', default='not_tested', readonly=True)
    error_message = fields.Text(string='Last Error', readonly=True)

    @api.constrains('sync_interval')
    def _check_sync_interval(self):
        for record in self:
            if record.sync_interval < 1:
                raise ValidationError('Sync interval must be at least 1 minute.')

    def action_test_connection(self):
        """Test API connection"""
        self.ensure_one()
        api = self.env['tracking.api'].create({})
        result = api.test_connection(self)
        
        if result.get('success'):
            self.write({
                'connection_status': 'success',
                'error_message': False
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': 'Connection successful!',
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            self.write({
                'connection_status': 'failed',
                'error_message': result.get('error', 'Unknown error')
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Connection Failed',
                    'message': result.get('error', 'Unknown error'),
                    'type': 'danger',
                    'sticky': True,
                }
            }

    def action_sync_devices(self):
        """Manually sync devices"""
        self.ensure_one()
        api = self.env['tracking.api'].create({})
        return api.sync_all_devices(self)

    def action_sync_locations(self):
        """Manually sync locations"""
        self.ensure_one()
        api = self.env['tracking.api'].create({})
        return api.sync_all_locations(self)
