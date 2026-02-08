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
4. Click "Test Connection" to verify
5. Click "Fetch Devices from API" to import all devices

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

To view devices on an interactive map:
1. Open `static/src/map_template.html` in a web browser
2. Or integrate it into your Odoo dashboard
3. The map uses OpenStreetMap/Leaflet.js for visualization

For production use, you can:
- Embed the map in a custom Odoo view
- Connect it to your API endpoint for live updates
- Add real-time WebSocket updates

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
