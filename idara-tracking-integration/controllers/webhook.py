from odoo import http
from odoo.http import request

class IDARATrackingWebhook(http.Controller):

    @http.route('/tracking/webhook', type='json', auth='public', methods=['POST'], csrf=False)
    def receive(self, **payload):
        return {'status': 'ok'}
