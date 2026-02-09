# Device Route History Feature

## Overview
This feature allows you to view the historical route of any GPS tracking device on an interactive map.

## Features

### 1. Route Visualization
- Display complete route path on Google Maps
- Highlight start point (green marker) and end point (red marker)
- Smooth polyline connecting all GPS points
- Color-coded route segments based on speed and status

### 2. Time Period Selection
- Select device from dropdown
- Choose start date and time
- Choose end date and time
- Default: Last 24 hours

### 3. Route Summary
- Total Distance traveled
- Duration of the trip
- Top Speed achieved
- Number of stops
- Total GPS points collected

### 4. Interactive Map Controls
- Zoom in/out
- Pan to explore route
- Click on markers for details
- Auto-fit route to view

## How to Use

### Method 1: From Device Form
1. Go to **Idara Tracking > Devices**
2. Open any device record
3. Click **"View Route History"** button in the header
4. A new window will open with the route history viewer
5. The device will be pre-selected
6. Adjust the date/time range as needed
7. Click **"Load Route"**

### Method 2: From Main Menu
1. Go to **Idara Tracking > Route History**
2. Select a device from the dropdown
3. Set the date and time range
4. Click **"Load Route"**

## API Integration

The feature uses the GPSWOX API endpoint:
```
GET /api/get_history
```

Parameters:
- `user_api_hash`: Authentication token (obtained via login)
- `device_id`: Device ID from GPSWOX
- `from_date`: Start date (YYYY-MM-DD)
- `from_time`: Start time (HH:MM:SS)
- `to_date`: End date (YYYY-MM-DD)
- `to_time`: End time (HH:MM:SS)
- `snap_to_road`: true/false
- `lang`: en

## Technical Details

### New Files Added
1. `models/tracking_device.py` - Added `get_device_history()` method
2. `controllers/main.py` - Added route history endpoints
3. `views/templates/device_history_template.xml` - Route viewer UI
4. `views/device_history_views.xml` - Action definition

### Controller Routes
- `/idara_tracking/device_history` - Main route history page
- `/idara_tracking/get_device_history` - JSON API endpoint

### Response Format
The API returns comprehensive route data including:
- GPS points with lat/lng coordinates
- Speed at each point
- Time stamps
- Route segments (driving, stopped, idle)
- Summary statistics

### Map Features
- Uses Google Maps JavaScript API
- Polyline for route visualization
- Custom markers for start/end points
- Info panel with route statistics
- Responsive design
- Loading indicators

## Requirements

### Odoo Dependencies
- base
- web
- fleet

### External Services
- Google Maps JavaScript API (requires valid API key)
- GPSWOX tracking platform (requires valid credentials)

## Configuration

1. Make sure Google Maps API key is configured in:
   **Idara Tracking > Configuration > Google Maps API Key**

2. Ensure GPSWOX credentials are set up:
   - API URL
   - Username
   - Password

## Troubleshooting

### No route displayed
- Check if device has data in the selected time period
- Verify GPSWOX credentials are correct
- Ensure device_id is correct

### "Authentication failed"
- Check username and password in configuration
- Verify API URL is correct

### Map not loading
- Check Google Maps API key
- Verify internet connection
- Check browser console for errors

## Future Enhancements

Potential improvements:
- Speed color coding on route
- Playback animation
- Export route to GPX/KML
- Print route report
- Multiple device comparison
- Geofence overlay
- Stop duration details
- Fuel consumption calculation
