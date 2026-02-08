
from odoo import models, fields

class TrackingPosition(models.Model):
    _name = 'tracking.position'
    _description = 'Live Vehicle Position'

    vehicle_id = fields.Many2one('fleet.vehicle', required=True)
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    speed = fields.Float()
    updated_at = fields.Datetime(default=fields.Datetime.now)
