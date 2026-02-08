/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class TrackingMapWidget extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.mapRef = useRef("map");
        this.map = null;
        this.markers = {};
        
        onWillStart(async () => {
            // Load Leaflet library if not already loaded
            if (!window.L) {
                await this.loadLeaflet();
            }
        });
        
        onMounted(() => {
            this.initMap();
            this.loadDevices();
            // Auto-refresh every 30 seconds
            this.interval = setInterval(() => {
                this.loadDevices();
            }, 30000);
        });
    }
    
    async loadLeaflet() {
        // Load Leaflet CSS
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
        document.head.appendChild(link);
        
        // Load Leaflet JS
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
    
    initMap() {
        const mapElement = this.mapRef.el;
        if (!mapElement) return;
        
        // Initialize map centered on Saudi Arabia
        this.map = L.map(mapElement).setView([24.7136, 46.6753], 6);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19,
        }).addTo(this.map);
    }
    
    async loadDevices() {
        try {
            const devices = await this.rpc('/tracking/devices/locations');
            this.updateMarkers(devices);
        } catch (error) {
            console.error('Error loading devices:', error);
        }
    }
    
    updateMarkers(devices) {
        if (!this.map) return;
        
        const currentDeviceIds = new Set(devices.map(d => d.id));
        
        // Remove markers for devices that no longer exist
        Object.keys(this.markers).forEach(deviceId => {
            if (!currentDeviceIds.has(parseInt(deviceId))) {
                this.map.removeLayer(this.markers[deviceId]);
                delete this.markers[deviceId];
            }
        });
        
        // Update or create markers
        devices.forEach(device => {
            if (this.markers[device.id]) {
                // Update existing marker
                this.markers[device.id].setLatLng([device.latitude, device.longitude]);
                this.markers[device.id].setPopupContent(this.getPopupContent(device));
            } else {
                // Create new marker
                const icon = this.getDeviceIcon(device.status);
                const marker = L.marker([device.latitude, device.longitude], { icon })
                    .addTo(this.map)
                    .bindPopup(this.getPopupContent(device));
                
                this.markers[device.id] = marker;
            }
        });
        
        // Fit map to show all markers
        if (devices.length > 0) {
            const bounds = L.latLngBounds(devices.map(d => [d.latitude, d.longitude]));
            this.map.fitBounds(bounds, { padding: [50, 50] });
        }
    }
    
    getDeviceIcon(status) {
        let color = 'gray';
        if (status === 'moving') color = 'green';
        else if (status === 'stopped') color = 'blue';
        else if (status === 'online') color = 'orange';
        
        return L.divIcon({
            className: 'custom-div-icon',
            html: `<div style="background-color: ${color}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white;"></div>`,
            iconSize: [20, 20],
            iconAnchor: [10, 10],
        });
    }
    
    getPopupContent(device) {
        const vehicleName = device.vehicle_name ? `<br><strong>Vehicle:</strong> ${device.vehicle_name}` : '';
        const lastUpdate = device.last_update ? new Date(device.last_update).toLocaleString() : 'N/A';
        
        return `
            <div style="min-width: 200px;">
                <h4 style="margin: 0 0 10px 0;">${device.name}</h4>
                ${vehicleName}
                <br><strong>Status:</strong> ${device.status}
                <br><strong>Speed:</strong> ${device.speed.toFixed(1)} km/h
                <br><strong>Ignition:</strong> ${device.ignition ? 'ON' : 'OFF'}
                <br><strong>Last Update:</strong> ${lastUpdate}
                <br><br>
                <a href="#" onclick="window.location.hash = 'id=${device.id}&model=tracking.device&view_type=form'; return false;">
                    View Details
                </a>
            </div>
        `;
    }
    
    willUnmount() {
        if (this.interval) {
            clearInterval(this.interval);
        }
    }
}

TrackingMapWidget.template = "idara_tracking_integration.TrackingMapWidget";

registry.category("fields").add("tracking_map", TrackingMapWidget);
