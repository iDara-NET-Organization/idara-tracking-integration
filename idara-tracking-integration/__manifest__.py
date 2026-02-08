# -*- coding: utf-8 -*-
{
    'name': 'Idara Tracking Integration',
    'version': '1.0.0',
    'category': 'Operations',
    'summary': 'GPS Tracking and Fleet Management Integration',
    'description': """
        Idara Tracking Integration Module
        ==================================
        
        This module provides comprehensive GPS tracking and fleet management capabilities:
        
        * Device Management
        * Real-time Location Tracking
        * Geofencing
        * Route History
        * Alerts and Notifications
        * Integration with tracking devices
    """,
    'author': 'Idara Net',
    'website': 'https://idaranet.com',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/tracking_device_views.xml',
        'views/tracking_config_views.xml',
        'views/tracking_location_views.xml',
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
