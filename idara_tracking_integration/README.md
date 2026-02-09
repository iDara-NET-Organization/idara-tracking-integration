# Idara Tracking Integration

GPS Tracking and Fleet Management Module for Odoo

## Features

- **Device Management**: Register and manage GPS tracking devices
- **API Integration**: Fetch devices directly from your tracking API
- **Real-time Tracking**: Monitor device locations in real-time
- **Interactive Map**: View all devices on an interactive map
- **Fleet Management**: Track vehicles and drivers
- **Configuration**: Flexible API configuration for different tracking providers
- **Status Monitoring**: Online/Offline/Moving/Idle status tracking
- **Multi-view Support**: Dashboard, Kanban, List, Form, and Map views

## Installation

1. Copy the `idara_tracking_integration` folder to your Odoo addons directory
2. Restart Odoo server
3. Go to Apps menu
4. Click "Update Apps List"
5. Search for "Idara Tracking Integration"
6. Click Install

## Configuration

1. Go to Idara Tracking > Configuration
2. Create a new configuration
3. Enter your API credentials:
   - API URL (e.g., https://api.tracking.example.com)
   - API Key
   - Username/Password (if required)
   - **Google Maps API Key** (required for map visualization)
4. Click "Test Connection" to verify
5. Click "Fetch Devices from API" to import all devices

### Getting a Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Maps JavaScript API**
4. Go to Credentials → Create Credentials → API Key
5. Copy the API key and paste it in the configuration
6. (Optional) Restrict the API key to your domain for security

## API Integration

The module expects your API to return device data in this format:

```json
{
  "devices": [
    {
      "id": "DEVICE001",
      "name": "Vehicle 1",
      "imei": "123456789012345",
      "latitude": 24.7136,
      "longitude": 46.6753,
      "speed": 45.5,
      "status": "moving",
      "address": "Riyadh, Saudi Arabia",
      "vehicle_id": "VEH001",
      "driver_name": "Ahmad"
    }
  ]
}
```

You can customize the API integration in `models/tracking_config.py` in the `fetch_devices_from_api()` method.

## Map View

The module includes two map options:

### Option 1: Google Maps (Recommended)
1. Configure Google Maps API key in Configuration
2. Open `/idara_tracking_integration/static/src/google_map.html`
3. Replace `YOUR_GOOGLE_MAPS_API_KEY_HERE` with your actual API key
4. Open in browser to see live tracking with Google Maps

### Option 2: OpenStreetMap (Free)
1. Open `/idara_tracking_integration/static/src/map_template.html`
2. No API key required
3. Uses Leaflet.js with OpenStreetMap tiles

Both maps show:
- Device locations with colored markers (green=online, blue=moving, yellow=idle, red=offline)
- Click markers for detailed info (speed, driver, vehicle, address)
- Auto-refresh every 30 seconds
- Responsive design

For production:
- Embed maps in Odoo views using iframes
- Connect to real-time WebSocket for live updates
- Add geofencing and route history features

## Usage

### Fetch Devices
- Go to Idara Tracking > Configuration
- Select your configuration
- Click "Fetch Devices from API"

### View Devices
- Go to Idara Tracking > Devices
- See all devices in list/kanban view
- Click on any device for details
- Use "Refresh Location" to update individual device

### Dashboard
- Go to Idara Tracking > Dashboard
- Quick access to all features
- View summary and quick links

## Requirements

- Odoo 15.0 or higher
- Base module
- Web module
- Python requests library (for API calls)

## License

LGPL-3

## Author

Idara Net - https://idaranet.com

## Support

For customization or support, contact your administrator or Idara Net support team.
