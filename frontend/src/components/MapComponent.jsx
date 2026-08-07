import React, { useEffect, useRef } from 'react';
import L from 'leaflet';

export default function MapComponent({ legs = [], incidents = [] }) {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);

  useEffect(() => {
    if (!mapRef.current) return;

    // Destroy previous map instance if exists
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
    }

    // Default center (Europe / Transatlantic corridor)
    const map = L.map(mapRef.current, {
      center: [48.8566, 2.3522],
      zoom: 4,
      zoomControl: true
    });

    mapInstanceRef.current = map;

    // Dark style tile layer (CartoDB Dark Matter)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap &copy; CARTO',
      subdomains: 'abcd',
      maxZoom: 19
    }).addTo(map);

    const latLngs = [];

    // Draw journey legs and markers
    legs.forEach((leg) => {
      if (leg.origin_lat && leg.origin_lon) {
        const originPoint = [leg.origin_lat, leg.origin_lon];
        latLngs.push(originPoint);

        const originIcon = L.divIcon({
          className: 'custom-map-icon',
          html: `<div style="background-color: #3b82f6; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 10px #3b82f6;"></div>`
        });

        L.marker(originPoint, { icon: originIcon })
          .addTo(map)
          .bindPopup(`<b>${leg.title}</b><br/>Origin: ${leg.origin}<br/>Status: ${leg.status}`);
      }

      if (leg.dest_lat && leg.dest_lon) {
        const destPoint = [leg.dest_lat, leg.dest_lon];
        latLngs.push(destPoint);

        const destIcon = L.divIcon({
          className: 'custom-map-icon',
          html: `<div style="background-color: #10b981; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 10px #10b981;"></div>`
        });

        L.marker(destPoint, { icon: destIcon })
          .addTo(map)
          .bindPopup(`<b>${leg.title}</b><br/>Destination: ${leg.destination}`);

        // Connect with polyline path
        if (leg.origin_lat && leg.origin_lon) {
          const pathColor = leg.status === 'DELAYED' ? '#ef4444' : (leg.status === 'REBOOKED' ? '#10b981' : '#3b82f6');
          L.polyline([[leg.origin_lat, leg.origin_lon], destPoint], {
            color: pathColor,
            weight: 3,
            dashArray: leg.status === 'DELAYED' ? '6, 6' : null,
            opacity: 0.8
          }).addTo(map);
        }
      }
    });

    // Draw incident hazard zones
    incidents.forEach((inc) => {
      if (inc.lat && inc.lon) {
        const hazardPoint = [inc.lat, inc.lon];
        latLngs.push(hazardPoint);

        const hazardIcon = L.divIcon({
          className: 'custom-map-icon',
          html: `<div style="background-color: #ef4444; width: 22px; height: 22px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 15px #ef4444; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 10px;">!</div>`
        });

        L.marker(hazardPoint, { icon: hazardIcon })
          .addTo(map)
          .bindPopup(`<b>🚨 Incident Alert: ${inc.title}</b><br/>Type: ${inc.type}<br/>Severity: ${inc.severity}<br/>${inc.description}`);

        // Add danger radius circle
        L.circle(hazardPoint, {
          color: '#ef4444',
          fillColor: '#ef4444',
          fillOpacity: 0.15,
          radius: 80000
        }).addTo(map);
      }
    });

    if (latLngs.length > 0) {
      map.fitBounds(L.latLngBounds(latLngs), { padding: [40, 40] });
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [legs, incidents]);

  return (
    <div className="relative w-full h-[420px] rounded-xl overflow-hidden border border-slate-800 shadow-2xl">
      <div ref={mapRef} className="w-full h-full" />
      <div className="absolute top-3 right-3 z-[1000] bg-slate-900/90 backdrop-blur border border-slate-800 rounded-lg p-2.5 text-[11px] space-y-1.5 shadow-xl">
        <div className="font-semibold text-slate-200 border-b border-slate-800 pb-1">Map Telemetry Legend</div>
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-blue-500 inline-block" />
          <span className="text-slate-300">Scheduled Flight/Rail Leg</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block" />
          <span className="text-slate-300">Disrupted / Delay Zone</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" />
          <span className="text-slate-300">Recovered / Rebooked Route</span>
        </div>
      </div>
    </div>
  );
}
