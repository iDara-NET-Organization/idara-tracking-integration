
odoo.define('idara_tracking_integration.live_map', function (require) {
    "use strict";
    const AbstractAction = require('web.AbstractAction');
    const core = require('web.core');

    const LiveMap = AbstractAction.extend({
        template: 'IdaraLiveMap',
        start() {
            this._super();
            const map = L.map('idara_live_map').setView([24.7, 46.7], 6);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
            const markers = {};
            const load = () => {
                fetch('/idara/api/vehicles')
                .then(r => r.json())
                .then(data => {
                    data.forEach(v => {
                        if (!markers[v.id]) {
                            markers[v.id] = L.marker([v.lat, v.lng]).addTo(map);
                        } else {
                            markers[v.id].setLatLng([v.lat, v.lng]);
                        }
                    });
                });
            };
            load();
            setInterval(load, 30000);
        }
    });

    core.action_registry.add('idara_tracking_live_map', LiveMap);
});
