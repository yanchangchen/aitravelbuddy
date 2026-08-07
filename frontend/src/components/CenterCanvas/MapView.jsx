import React from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useTripStore } from '../../stores/tripStore';

function MapFitter({ markers }) {
  const map = useMap();
  React.useEffect(() => {
    if (markers && markers.length > 0) {
      const bounds = markers.map(m => [m.lat, m.lng]);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [markers, map]);
  return null;
}

export default function MapView() {
  const { planResult } = useTripStore();
  
  // Extract mock markers from plan if exists (in a real app, API would provide coords)
  const markers = [
    { id: 1, lat: 40.7128, lng: -74.0060, name: 'Sample Sightseeing', category: 'sightseeing' },
    { id: 2, lat: 40.7580, lng: -73.9855, name: 'Sample Hotel', category: 'hotel' }
  ];

  const colors = {
    sightseeing: '#FF6B6B',
    hotel: '#38BDF8',
    dining: '#FF8E53'
  };

  return (
    <div style={{ height: '100%', width: '100%' }}>
      <MapContainer center={[20, 0]} zoom={2} style={{ height: '100%', width: '100%', background: 'var(--bg-primary)' }}>
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'
        />
        {planResult && markers.map(m => (
          <CircleMarker 
            key={m.id} 
            center={[m.lat, m.lng]} 
            pathOptions={{ color: colors[m.category] || '#fff', fillColor: colors[m.category] || '#fff', fillOpacity: 0.7 }}
            radius={8}
          >
            <Popup>
              <div style={{ color: '#000' }}>
                <strong>{m.name}</strong><br/>
                <span style={{ textTransform: 'capitalize' }}>{m.category}</span>
              </div>
            </Popup>
          </CircleMarker>
        ))}
        {planResult && <MapFitter markers={markers} />}
      </MapContainer>
    </div>
  );
}
