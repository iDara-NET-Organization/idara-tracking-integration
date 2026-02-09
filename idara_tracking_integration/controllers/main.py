# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request, Response
import json


class TrackingMapController(http.Controller):

    @http.route('/idara_tracking/map', type='http', auth='user', csrf=False)
    def tracking_map(self, **kwargs):
        """Display interactive map with all devices"""
        # Fetch all active devices
        devices = request.env['tracking.device'].sudo().search([('active', '=', True)])
        
        devices_data = []
        for device in devices:
            # Only add devices with valid coordinates
            if device.latitude and device.longitude:
                devices_data.append({
                    'id': device.id,
                    'name': device.name or device.device_id or 'Unknown',
                    'device_id': device.device_id or '',
                    'latitude': float(device.latitude),
                    'longitude': float(device.longitude),
                    'speed': float(device.speed) if device.speed else 0.0,
                    'status': device.status or 'offline',
                    'driver_name': device.driver_name or '-',
                    'vehicle_id': device.vehicle_id or '',
                    'address': device.address or '-',
                    'last_update': str(device.last_update) if device.last_update else '',
                })
        
        # Get configuration
        config = request.env['tracking.config'].sudo().search([('active', '=', True)], limit=1)
        refresh_interval = config.auto_refresh_interval if config else 30
        timezone_offset = config.timezone_offset if config else 3
        
        # Convert to JSON strings
        devices_json = json.dumps(devices_data)
        device_count = len(devices_data)
        
        # Generate HTML directly
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Live Device Tracking</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; overflow: hidden; }}
        #header {{
            background: linear-gradient(135deg, #dc3545, #c82333);
            color: white; padding: 15px 20px; height: 70px;
            display: flex; align-items: center; justify-content: space-between;
        }}
        #map {{ height: calc(100vh - 70px); width: 100vw; }}
        .device-count {{ background: #28a745; color: white; padding: 8px 15px; border-radius: 15px; font-weight: bold; }}
        .device-label {{
            background: white; padding: 4px 8px; border-radius: 3px;
            font-size: 11px; font-weight: bold; box-shadow: 0 1px 4px rgba(0,0,0,0.3);
            margin-top: -8px; white-space: nowrap;
        }}
        .leaflet-marker-icon {{ transition: all 0.8s ease-in-out !important; }}
    </style>
</head>
<body>
    <div id="header">
        <div style="display:flex;align-items:center">
            <img src="/idara_tracking_integration/static/src/img/logo.png" style="height:45px;margin-right:15px"/>
            <span style="font-size:22px">🗺️ Live Device Tracking</span>
        </div>
        <span class="device-count" id="device-count">{device_count} Devices</span>
    </div>
    <div id="map"></div>
    
    <script type="text/javascript">
        var DEVICES = {devices_json};
        var TZ_OFFSET = {timezone_offset};
        var REFRESH_MS = {refresh_interval * 1000};
        
        var map, markers = {{}};
        
        console.log('✅ Loaded', DEVICES.length, 'devices');
        
        function getCol(s) {{
            return s === 'online' ? '#28a745' : s === 'moving' ? '#007bff' : s === 'idle' ? '#ffc107' : '#dc3545';
        }}
        
        function getBdg(s) {{
            return s === 'online' ? '🟢 Online' : s === 'moving' ? '🔵 Moving' : s === 'idle' ? '🟡 Idle' : '🔴 Offline';
        }}
        
        function adjTime(t) {{
            if (!t) return 'N/A';
            try {{
                var d = new Date(t + 'Z');
                d.setHours(d.getHours() + TZ_OFFSET);
                return d.toLocaleString();
            }} catch(e) {{ return t; }}
        }}
        
        function init() {{
            if (typeof L === 'undefined') {{
                console.log('⏳ Waiting for Leaflet...');
                setTimeout(init, 500);
                return;
            }}
            
            console.log('🗺️ Initializing map...');
            map = L.map('map').setView([24.7136, 46.6753], 6);
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '© OpenStreetMap'
            }}).addTo(map);
            
            var bounds = L.latLngBounds();
            DEVICES.forEach(function(d) {{
                var m = addMarker(d);
                if (m) bounds.extend(m.getLatLng());
            }});
            
            if (DEVICES.length > 0) map.fitBounds(bounds, {{padding: [50, 50]}});
            console.log('✅ Map ready!');
            
            if (REFRESH_MS > 0) setInterval(refresh, REFRESH_MS);
        }}
        
        function addMarker(d) {{
            var lat = parseFloat(d.latitude), lng = parseFloat(d.longitude);
            if (!lat || !lng) return null;
            
            var col = getCol(d.status), nm = d.name || d.device_id || 'Unknown';
            
            var m = L.marker([lat, lng], {{
                icon: L.divIcon({{
                    className: '',
                    html: '<div style="position:relative"><div style="background:' + col + ';width:24px;height:24px;border-radius:50%;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.4)"></div><div class="device-label">' + nm + '</div></div>',
                    iconSize: [120, 40],
                    iconAnchor: [60, 32]
                }})
            }}).addTo(map);
            
            m.bindPopup(
                '<div style="min-width:220px;font-family:Arial">' +
                '<h3 style="margin:0 0 12px 0;color:#dc3545;font-size:16px">📍 ' + nm + '</h3>' +
                '<p style="margin:6px 0;font-size:13px"><b>Device ID:</b> ' + (d.device_id || 'N/A') + '</p>' +
                '<p style="margin:6px 0;font-size:13px"><b>Status:</b> ' + getBdg(d.status) + '</p>' +
                '<p style="margin:6px 0;font-size:13px"><b>Speed:</b> ' + (d.speed || 0) + ' km/h</p>' +
                '<p style="margin:6px 0;font-size:13px"><b>Driver:</b> ' + (d.driver_name || 'N/A') + '</p>' +
                '<p style="margin:6px 0;font-size:13px"><b>Vehicle:</b> ' + (d.vehicle_id || 'N/A') + '</p>' +
                '<p style="margin:6px 0;font-size:13px"><b>Location:</b> ' + (d.address || 'Unknown') + '</p>' +
                '<p style="margin:6px 0;font-size:11px;color:#666">Last: ' + adjTime(d.last_update) + '</p>' +
                '</div>'
            );
            
            markers[d.id] = m;
            return m;
        }}
        
        function refresh() {{
            fetch('/idara_tracking/devices/json', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{jsonrpc: '2.0', method: 'call', params: {{}}, id: Date.now()}})
            }})
            .then(function(r) {{ return r.json(); }})
            .then(function(data) {{
                var devices = data.result;
                if (!devices || !Array.isArray(devices)) return;
                
                document.getElementById('device-count').textContent = devices.length + ' Devices';
                devices.forEach(function(d) {{
                    var m = markers[d.id];
                    if (m) {{
                        m.setLatLng([parseFloat(d.latitude), parseFloat(d.longitude)]);
                        var col = getCol(d.status), nm = d.name || d.device_id || 'Unknown';
                        m.setIcon(L.divIcon({{
                            className: '',
                            html: '<div style="position:relative"><div style="background:' + col + ';width:24px;height:24px;border-radius:50%;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.4)"></div><div class="device-label">' + nm + '</div></div>',
                            iconSize: [120, 40],
                            iconAnchor: [60, 32]
                        }}));
                    }} else {{ addMarker(d); }}
                }});
            }})
            .catch(function(e) {{
                console.error('Refresh error:', e);
            }});
        }}
        
        setTimeout(init, 100);
    </script>
</body>
</html>"""
        
        return Response(html, content_type='text/html')
    
    @http.route('/idara_tracking/devices/json', type='json', auth='user')
    def get_devices_json(self, **kwargs):
        """API endpoint to get devices as JSON for live updates"""
        devices = request.env['tracking.device'].sudo().search([('active', '=', True)])
        
        devices_data = []
        for device in devices:
            if device.latitude and device.longitude:
                devices_data.append({
                    'id': device.id,
                    'name': device.name or device.device_id or 'Unknown',
                    'device_id': device.device_id or '',
                    'latitude': float(device.latitude),
                    'longitude': float(device.longitude),
                    'speed': float(device.speed) if device.speed else 0.0,
                    'status': device.status or 'offline',
                    'driver_name': device.driver_name or '-',
                    'vehicle_id': device.vehicle_id or '',
                    'address': device.address or '-',
                    'last_update': str(device.last_update) if device.last_update else '',
                })
        
        return devices_data
    
    @http.route('/idara_tracking/device_history', type='http', auth='user', website=False)
    def device_history_viewer(self, device_id=None, **kwargs):
        """Display device history/route viewer page"""
        devices = request.env['tracking.device'].sudo().search([('active', '=', True)])
        selected_device = None
        if device_id:
            selected_device = request.env['tracking.device'].sudo().browse(int(device_id))
        
        config = request.env['tracking.config'].sudo().search([('active', '=', True)], limit=1)
        google_maps_key = config.google_maps_api_key if config else ''
        
        return request.render('idara_tracking_integration.device_history_template', {
            'devices': devices,
            'selected_device': selected_device,
            'google_maps_key': google_maps_key,
        })
    
    @http.route('/idara_tracking/get_device_history', type='json', auth='user')
    def get_device_history(self, device_id, from_datetime, to_datetime, **kwargs):
        """API endpoint to get device history data"""
        try:
            device = request.env['tracking.device'].sudo().browse(int(device_id))
            
            if not device.exists():
                return {'status': 'error', 'message': 'Device not found'}
            
            result = device.get_device_history(from_datetime, to_datetime)
            return result
            
        except Exception as e:
            import traceback
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(traceback.format_exc())
            return {'status': 'error', 'message': str(e)}
