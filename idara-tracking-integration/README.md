# Idara Tracking Integration

AVL Tracking Integration module for Odoo - Connect to tracking.idara.net API and display device locations on live maps.

## Features

### Core Functionality
- **API Integration**: Seamless connection to tracking.idara.net API
- **Real-time Tracking**: Live device location updates
- **Interactive Maps**: View all devices on an interactive map using Leaflet.js
- **Device Management**: Manage and monitor multiple AVL devices
- **Location History**: Track and analyze historical location data
- **Auto-sync**: Automatic synchronization of device locations

### Device Monitoring
- View current device status (Online, Moving, Stopped, Offline)
- Monitor speed, heading, altitude, and position
- Track ignition status and power information
- View device alerts and notifications
- Individual device tracking on dedicated maps

### Data Management
- Automatic data synchronization every 5 minutes
- Manual sync options for immediate updates
- Historical location tracking and analysis
- Comprehensive device statistics

## Installation

1. Copy this module to your Odoo addons directory
2. Update the apps list in Odoo
3. Install "Idara Tracking Integration" module

## Configuration

### API Setup

1. Go to **Tracking > Configuration > API Configuration**
2. Create a new configuration:
   - **Configuration Name**: Give it a descriptive name
   - **API Base URL**: https://tracking.idara.net/api
   - **API Key**: Your API key from the tracking platform
   - **API Hash/Token**: Your API authentication token
   - **User API Hash**: (Optional) User-specific API hash
   - **Sync Interval**: Set how often to sync (default: 5 minutes)

3. Click **Test Connection** to verify the setup
4. Click **Sync Devices** to import your devices

### Device Synchronization

The module automatically syncs device locations based on the configured interval. You can also:
- Manually sync all devices: Click "Sync Devices" in configuration
- Manually sync locations: Click "Sync Locations" in configuration
- Sync individual device: Open device form and click "Sync Now"

## Usage

### Live Map View

1. Navigate to **Tracking > Devices > Live Map**
2. View all online devices on an interactive map
3. Click on markers to see device details
4. Map auto-refreshes every 30 seconds

### Device Management

1. Go to **Tracking > Devices > All Devices**
2. View devices in list, kanban, or form view
3. Filter by status (Online, Moving, Stopped, Offline)
4. Click on a device to view detailed information

### Location History

1. Navigate to **Tracking > History > Location History**
2. View all location records
3. Filter by device, date, or movement status
4. Export data for analysis

## Technical Details

### Models

- **tracking.config**: API configuration and connection settings
- **tracking.device**: AVL device information and current status
- **tracking.location**: Historical location data
- **tracking.api**: API service layer (transient model)

### Controllers

- `/tracking/devices/locations`: Get all devices locations (JSON)
- `/tracking/device/location/<id>`: Get specific device location (JSON)
- `/tracking/device/route/<id>`: Get device route history (JSON)

### Scheduled Actions

- **Sync Device Locations**: Runs every 5 minutes (configurable)
- **Sync Devices List**: Runs daily to update device list

## Security

The module includes two user groups:
- **Tracking User**: Can view devices and locations
- **Tracking Manager**: Full access including configuration

## Dependencies

- Odoo base module
- Odoo web module
- Python requests library
- Leaflet.js (loaded via CDN)

## API Endpoints Used

The module integrates with the following API endpoints:
- `/get_devices`: Fetch all devices
- `/get_device_data`: Fetch specific device location data

## Troubleshooting

### Connection Issues
1. Verify API credentials are correct
2. Check that the API URL is accessible
3. Review error messages in the configuration form
4. Check Odoo logs for detailed error information

### Sync Not Working
1. Verify cron jobs are enabled
2. Check that configuration is marked as "Active"
3. Ensure devices are active in the system
4. Review sync interval settings

### Map Not Displaying
1. Check browser console for JavaScript errors
2. Verify Leaflet.js is loading correctly
3. Ensure devices have valid latitude/longitude data
4. Check that web assets are properly loaded

## Support

For issues or questions:
- Check the Odoo logs for error details
- Review API documentation at the tracking platform
- Verify network connectivity to tracking.idara.net

## Version

- **Version**: 1.0.0
- **License**: LGPL-3
- **Odoo Version**: 15.0+ (compatible with 16.0, 17.0)

## Changelog

### Version 1.0.0
- Initial release
- API integration with tracking.idara.net
- Live map visualization
- Device and location management
- Automatic synchronization
- Historical data tracking
