{
    "name": "iDARA Tracking Integration",
    "version": "16.0.1.0.0",
    "category": "Fleet",
    "summary": "Real-time GPS tracking integration with Odoo Fleet",
    "author": "iDaraNet",
    "website": "https://idara.net",
    "license": "OPL-1",
    "price": 199,
    "currency": "USD",
    "depends": ["base", "fleet", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/tracking_config_views.xml",
        "views/tracking_device_views.xml",
        "views/tracking_position_views.xml"
    ],
    "installable": True,
    "application": False
}