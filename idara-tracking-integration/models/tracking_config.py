from odoo import models, fields

class TrackingConfig(models.Model):
    _name = 'tracking.config'
    _description = 'Tracking Server Configuration'

    name = fields.Char(default='Tracking Server')
    base_url = fields.Char(required=True)
    api_key = fields.Char()
    active = fields.Boolean(default=True)
