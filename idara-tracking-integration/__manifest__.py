# -*- coding: utf-8 -*-
{
    'name': 'Idara Tracking Integration',
    'version': '1.0.0',
    'category': 'Fleet Management',
    'summary': 'AVL Tracking Integration with Live Map Visualization',
    'description': """
        AVL Tracking Integration Module
        ================================
        
        Features:
        ---------
        * Connect to tracking.idara.net API
        * Retrieve real-time device locations
        * Display devices on interactive live map
        * Track device status and alerts
        * Historical route visualization
        * Device management and configuration
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'web'],
    'data': [
        'security/tracking_security.xml',
        'security/ir.model.access.csv',
        'views/tracking_config_views.xml',
        'views/tracking_device_views.xml',
        'views/tracking_location_views.xml',
        'views/tracking_menu.xml',
        'data/tracking_cron.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'idara-tracking-integration/static/src/js/tracking_map_widget.js',
            'idara-tracking-integration/static/src/xml/tracking_map_widget.xml',
            'idara-tracking-integration/static/src/css/tracking_map.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
