import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useTripStore } from '../../stores/tripStore';
import { apiClient } from '../../api/client';

function MapFitter({ markers }) {
  const map = useMap();
  useEffect(() => {
    if (markers && markers.length > 0) {
      const validBounds = markers
        .map(m => (m.lat && m.lng ? [m.lat, m.lng] : (m.coords ? m.coords : null)))
        .filter(Boolean);
      if (validBounds.length > 0) {
        map.fitBounds(validBounds, { padding: [50, 50] });
      }
    }
  }, [markers, map]);
  return null;
}

export default function MapView() {
  const { planResult, partialResult, destination } = useTripStore();
  const [locations, setLocations] = useState([]);
  
  const activeResult = planResult || (Object.keys(partialResult).length > 0 ? partialResult : null);
  const targetDest = activeResult?.destination || destination || 'Tokyo, Japan';

  useEffect(() => {
    if (activeResult) {
      apiClient.getLocations(activeResult, targetDest)
        .then((res) => {
          if (res && res.locations && Array.isArray(res.locations)) {
            setLocations(res.locations);
          }
        })
        .catch((err) => console.warn('Failed to fetch map locations:', err));
    }
  }, [activeResult, targetDest]);

  const defaultCenter = [35.6762, 139.6503]; // Default Tokyo

  const colors = {
    sightseeing: '#FF6B6B',
    hotel: '#38BDF8',
    dining: '#FF8E53',
    transport: '#4ADE80'
  };

  const activeMarkers = locations.length > 0 ? locations : [
    { name: targetDest, lat: defaultCenter[0], lng: defaultCenter[1], category: 'sightseeing' }
  ];

  return (
    <div style={{ height: '100%', width: '100%', position: 'relative' }}>
      <MapContainer center={defaultCenter} zoom={6} style={{ height: '100%', width: '100%', background: 'var(--bg-primary)' }}>
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'
        />
        {activeMarkers.map((m, idx) => {
          const lat = m.lat || (m.coords ? m.coords[0] : defaultCenter[0]);
          const lng = m.lng || (m.coords ? m.coords[1] : defaultCenter[1]);
          const catColor = colors[m.category] || '#FF6B6B';

          return (
            <CircleMarker 
              key={idx} 
              center={[lat, lng]} 
              pathOptions={{ color: catColor, fillColor: catColor, fillOpacity: 0.85 }}
              radius={9}
            >
              <Popup>
                <div style={{ color: '#0F172A', padding: '0.25rem' }}>
                  <strong style={{ fontSize: '0.95rem' }}>{m.name || m.title || targetDest}</strong>
                  {m.day && <div style={{ fontSize: '0.8rem', color: '#64748B', marginTop: '0.2rem' }}>Day {m.day}</div>}
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
        {activeMarkers.length > 0 && <MapFitter markers={activeMarkers} />}
      </MapContainer>
    </div>
  );
}
