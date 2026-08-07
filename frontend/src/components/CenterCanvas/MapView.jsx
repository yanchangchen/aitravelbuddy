import React, { useState, useEffect } from 'react';
import { useTripStore } from '../../stores/tripStore';
import { apiClient } from '../../api/client';
import { MapPin, ExternalLink } from 'lucide-react';

export default function MapView() {
  const { planResult, partialResult, destination, selectedLocation, setSelectedLocation } = useTripStore();
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

  const activeQuery = selectedLocation?.name || selectedLocation?.title || selectedLocation?.query || (locations.length > 0 ? `${locations[0].title}, ${targetDest}` : targetDest);
  const googleEmbedUrl = `https://maps.google.com/maps?q=${encodeURIComponent(activeQuery)}&t=&z=13&ie=UTF8&iwloc=&output=embed`;

  return (
    <div style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column', background: 'var(--bg-primary)' }}>
      {/* Google Maps View */}
      <div style={{ flex: 1, position: 'relative', minHeight: '300px' }}>
        <iframe
          title="Google Maps Location View"
          width="100%"
          height="100%"
          style={{ border: 0, width: '100%', height: '100%' }}
          loading="lazy"
          allowFullScreen
          src={googleEmbedUrl}
        />
        <div style={{ position: 'absolute', top: '12px', left: '12px', background: 'rgba(15, 23, 42, 0.85)', backdropFilter: 'blur(8px)', padding: '0.4rem 0.8rem', borderRadius: '8px', border: '1px solid var(--border-subtle)', color: '#fff', fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.4rem', zIndex: 10 }}>
          <MapPin size={16} color="var(--accent-coral)" />
          Google Maps — {activeQuery}
        </div>
      </div>

      {/* Itinerary Location Pins Ribbon */}
      {locations.length > 0 && (
        <div style={{ height: '130px', background: 'var(--bg-secondary)', borderTop: '1px solid var(--border-subtle)', padding: '0.75rem 1rem', overflowX: 'auto', display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          {locations.map((loc, idx) => {
            const isSelected = selectedLocation && (selectedLocation.name === loc.title || selectedLocation.title === loc.title);
            const gmapsUrl = loc.google_maps_url || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(loc.title + ', ' + targetDest)}`;

            return (
              <div 
                key={idx}
                onClick={() => setSelectedLocation({ name: loc.title, title: loc.title, day: loc.day, lat: loc.lat, lng: loc.lng, category: loc.category })}
                style={{
                  minWidth: '210px',
                  maxWidth: '230px',
                  background: isSelected ? 'rgba(255, 107, 107, 0.12)' : 'var(--bg-glass)',
                  border: `1.5px solid ${isSelected ? 'var(--accent-coral)' : 'var(--border-subtle)'}`,
                  borderRadius: '10px',
                  padding: '0.75rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  flexShrink: 0
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                  <span style={{ fontSize: '0.75rem', background: 'var(--accent-coral)', color: '#fff', padding: '0.15rem 0.45rem', borderRadius: '4px', fontWeight: 700 }}>
                    {loc.day || 'Day 1'}
                  </span>
                  <a 
                    href={gmapsUrl} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    onClick={(e) => e.stopPropagation()}
                    style={{ color: 'var(--accent-blue)', display: 'flex', alignItems: 'center', gap: '0.2rem', fontSize: '0.75rem', fontWeight: 600, textDecoration: 'none' }}
                  >
                    Directions <ExternalLink size={12} />
                  </a>
                </div>
                <strong style={{ fontSize: '0.875rem', color: isSelected ? 'var(--accent-coral)' : 'var(--text-primary)', display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {loc.title || loc.name}
                </strong>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                  {loc.category || 'Sightseeing'}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
