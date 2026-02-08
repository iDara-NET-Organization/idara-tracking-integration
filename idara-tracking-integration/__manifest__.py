{
    "name": "iDARA Tracking Integration",
    "version": "16.0.1.0.0",
    "category": "Fleet",
    "summary": "Free GPS tracking integration for Odoo Fleet",
    "description": "Free integration between Odoo Fleet and self-hosted GPS tracking servers (GPSWOX based).",
    "author": "iDaraNet",
    "website": "https://idara.net",
    "license": "LGPL-3",
    "depends": ["base", "fleet", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/tracking_config_views.xml"
    ],
    "images": ["static/description/cover.png"],
    "installable": True,
    "application": False
}
