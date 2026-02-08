
{
    'name': 'iDARA Live Tracking Map',
    'version': '1.0',
    'category': 'Fleet',
    'depends': ['fleet', 'web'],
    'data': ['views/live_map_action.xml'],
    'assets': {
        'web.assets_backend': [
            'idara_tracking_integration/static/src/js/live_map.js',
            'idara_tracking_integration/static/src/xml/live_map.xml'
        ]
    },
    'installable': True
}
