# -*- coding: utf-8 -*-
{
    'name': 'Idara Tracking Integration',
    'version': '3.0.0',
    'category': 'Operations',
    'summary': 'GPS Tracking with Multi-Map Support & Timezone (Odoo 15-19)',
    'description': """
        Idara Tracking Integration Module
        ==================================
        
        Compatible with Odoo 15, 16, 17, 18, and 19
        
        This module provides comprehensive GPS tracking and fleet management capabilities:
        
        * Device Management
        * Real-time Location Tracking with Live Map View
        * Interactive Route History Viewer
        * Historical Route Playback with Timeline
        * Geofencing
        * Alerts and Notifications
        * Integration with GPSWOX tracking platform
        * Fleet Vehicle Integration
        
        Version Compatibility:
        - Odoo 15.0 ✓
        - Odoo 16.0 ✓
        - Odoo 17.0 ✓
        - Odoo 18.0 ✓
        - Odoo 19.0 ✓
    """,
    'author': 'Idara Net',
    'website': 'https://idaranet.com',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'fleet'],
    'data': [
        'security/ir.model.access.csv',
        'views/templates/tracking_map_template.xml',
        'views/templates/device_history_template.xml',
        'views/tracking_device_views.xml',
        'views/tracking_config_views.xml',
        'views/fleet_vehicle_views.xml',
        'views/tracking_location_views.xml',
        'views/device_history_views.xml',
        'views/tracking_menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'idara_tracking_integration/static/src/img/logo.png',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
