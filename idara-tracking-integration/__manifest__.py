
{
    "name": "iDARA Tracking Integration",
    "version": "16.0.1.0.0",
    "category": "Fleet",
    "summary": "Free GPS tracking integration for Odoo Fleet",
    "author": "iDaraNet",
    "website": "https://idara.net",
    "license": "LGPL-3",
    "depends": ["base", "fleet", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/tracking_position_views.xml"
    ],
    "images": ["static/description/cover.png"],
    "installable": True,
    "application": False
}
