# Installation Guide - Idara Tracking Integration

## Prerequisites

### System Requirements
- Odoo 15.0 or higher (tested with 15.0, 16.0, 17.0)
- Python 3.7+
- PostgreSQL database
- Internet connection for API access

### Python Dependencies
```bash
pip3 install requests
```

## Installation Steps

### 1. Download and Install Module

```bash
# Navigate to your Odoo addons directory
cd /path/to/odoo/addons

# Copy the module
cp -r /path/to/idara-tracking-integration .

# Set proper permissions
chmod -R 755 idara-tracking-integration
chown -R odoo:odoo idara-tracking-integration
```

### 2. Update Odoo Apps List

```bash
# Restart Odoo service
sudo systemctl restart odoo

# Or if running manually
./odoo-bin -c /etc/odoo/odoo.conf --stop-after-init -u all -d your_database
```

### 3. Install Module via UI

1. Log in to Odoo as administrator
2. Go to **Apps** menu
3. Click **Update Apps List**
4. Search for "Idara Tracking Integration"
5. Click **Install**

### 4. Configure API Connection

1. Go to **Tracking > Configuration > API Configuration**
2. Click **Create**
3. Fill in the following:

```
Configuration Name: Idara Tracking
API Base URL: https://tracking.idara.net/api
API Key: [Your API Key]
API Hash/Token: [Your API Token]
User API Hash: [Your User API Hash - if different]
Sync Interval: 5 (minutes)
Active: ✓
```

4. Click **Save**
5. Click **Test Connection** button
6. Verify you see "Connection successful!" message

### 5. Initial Data Sync

1. In the configuration form, click **Sync Devices**
2. Wait for the sync to complete
3. Go to **Tracking > Devices > All Devices** to see imported devices
4. Click **Sync Locations** to get initial location data

## Post-Installation Configuration

### Enable Cron Jobs

Ensure Odoo cron jobs are enabled in your configuration file:

```ini
# /etc/odoo/odoo.conf
[options]
...
max_cron_threads = 2
...
```

Restart Odoo after making changes:
```bash
sudo systemctl restart odoo
```

### Set User Permissions

1. Go to **Settings > Users & Companies > Users**
2. Select a user
3. Under **Access Rights**, find "Tracking"
4. Assign appropriate role:
   - **Tracking / User**: Can view devices and locations
   - **Tracking / Manager**: Can configure API and manage all data

### Configure Sync Schedule (Optional)

To customize sync intervals:

1. Go to **Settings > Technical > Automation > Scheduled Actions**
2. Find "Tracking: Sync Device Locations"
3. Modify the interval as needed
4. Save changes

## Verification

### Test the Installation

1. **Check Device List**:
   - Go to **Tracking > Devices > All Devices**
   - Verify devices are displayed

2. **Test Live Map**:
   - Go to **Tracking > Devices > Live Map**
   - Verify map loads and shows device markers

3. **Check Location History**:
   - Go to **Tracking > History > Location History**
   - Verify location records are being created

4. **Monitor Logs**:
```bash
tail -f /var/log/odoo/odoo.log | grep tracking
```

## Troubleshooting Installation

### Module Not Appearing in Apps List

```bash
# Update apps list from command line
./odoo-bin -c /etc/odoo/odoo.conf -d your_database -u all --stop-after-init

# Check module is in addons path
grep addons_path /etc/odoo/odoo.conf
```

### Import Errors

If you get import errors, ensure all dependencies are installed:

```bash
pip3 install requests
pip3 install python-dateutil
```

### Database Issues

If installation fails, check Odoo logs:
```bash
tail -100 /var/log/odoo/odoo.log
```

Common issues:
- PostgreSQL version too old (need 9.6+)
- Insufficient database permissions
- Module dependencies not installed

### API Connection Fails

1. Verify API endpoint is accessible:
```bash
curl -I https://tracking.idara.net/api
```

2. Check firewall rules allow outbound HTTPS
3. Verify API credentials are correct
4. Check Odoo logs for detailed error messages

## Uninstallation

To remove the module:

1. Go to **Apps** menu
2. Search for "Idara Tracking Integration"
3. Click **Uninstall**
4. Confirm removal

**Note**: This will remove all tracking data from the database.

To preserve data:
1. Export location history before uninstalling
2. Backup the database
3. Use **Archive** instead of **Uninstall** if you want to disable temporarily

## Upgrading

To upgrade to a new version:

1. Backup your database
2. Replace module files with new version
3. Restart Odoo
4. Go to **Apps** menu
5. Find the module and click **Upgrade**

## Support

For installation issues:
- Check Odoo community forums
- Review module logs in Odoo
- Verify all prerequisites are met
- Ensure network connectivity to API server

## Advanced Configuration

### Multi-Company Setup

If using multi-company:
1. Create separate configurations per company
2. Set company field on tracking.config model
3. Filter devices by company

### Custom API Endpoints

If your tracking server uses different endpoints, modify:
```python
# models/tracking_api.py
def get_devices(self, config):
    result = self._make_request(config, '/your_custom_endpoint')
```

### Performance Tuning

For large fleets (100+ devices):
- Increase sync interval to 10-15 minutes
- Archive old location records periodically
- Add database indexes on frequently queried fields
- Consider using multiple configurations to distribute load
