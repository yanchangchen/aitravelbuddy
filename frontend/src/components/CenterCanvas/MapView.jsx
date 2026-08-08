import React, { useState, useEffect, useMemo } from 'react';
import { useTripStore } from '../../stores/tripStore';
import { apiClient } from '../../api/client';
import { MapPin, ExternalLink, Navigation, Compass, Layers, Filter, Hotel, Utensils, Calendar } from 'lucide-react';
import { motion } from 'framer-motion';

export default function MapView() {
  const { planResult, partialResult, destination, selectedLocation, setSelectedLocation } = useTripStore();
  const [locations, setLocations] = useState([]);
  const [activeFilter, setActiveFilter] = useState('all');

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

  // Extract unique days for filter tabs
  const availableDays = useMemo(() => {
    const days = new Set();
    locations.forEach(loc => {
      if (loc.day && loc.day.toLowerCase().startsWith('day')) {
        days.add(loc.day);
      }
    });
    return Array.from(days).sort();
  }, [locations]);

  // Filtered locations
  const filteredLocations = useMemo(() => {
    if (activeFilter === 'all') return locations;
    if (activeFilter === 'hotels') return locations.filter(l => l.category === 'Hotel' || l.day === 'Hotel');
    if (activeFilter === 'dining') return locations.filter(l => l.category === 'Dining & Retail' || l.day === 'Dining');
    return locations.filter(l => l.day === activeFilter);
  }, [locations, activeFilter]);

  // Active query for Google Maps iframe
  const mapQuery = useMemo(() => {
    if (selectedLocation) {
      return selectedLocation.name || selectedLocation.title || selectedLocation.query || `${selectedLocation}, ${targetDest}`;
    }
    if (activeFilter !== 'all' && filteredLocations.length > 0) {
      const names = filteredLocations.slice(0, 3).map(l => l.title || l.name).join(' ');
      return `${names} ${targetDest}`;
    }
    if (locations.length > 0) {
      const topSpots = locations.slice(0, 4).map(l => l.title || l.name).join(' ');
      return `${topSpots} ${targetDest}`;
    }
    return `${targetDest} attractions`;
  }, [selectedLocation, activeFilter, filteredLocations, locations, targetDest]);

  const googleEmbedUrl = `https://maps.google.com/maps?q=${encodeURIComponent(mapQuery)}&t=&z=13&ie=UTF8&iwloc=&output=embed`;
  const fullGoogleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(mapQuery)}`;

  return (
    <div style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column', background: 'var(--bg-primary)' }}>
      {/* Top Filter Bar */}
      <div style={{ padding: '0.6rem 1rem', background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', overflowX: 'auto' }}>
          <button
            onClick={() => { setActiveFilter('all'); setSelectedLocation(null); }}
            style={{
              padding: '0.35rem 0.75rem',
              borderRadius: '20px',
              fontSize: '0.8rem',
              fontWeight: 600,
              border: 'none',
              cursor: 'pointer',
              background: activeFilter === 'all' && !selectedLocation ? 'var(--accent-coral)' : 'var(--bg-tertiary)',
              color: activeFilter === 'all' && !selectedLocation ? '#fff' : 'var(--text-secondary)'
            }}
          >
            🗺️ All Itinerary Places ({locations.length})
          </button>

          {availableDays.map(day => (
            <button
              key={day}
              onClick={() => { setActiveFilter(day); setSelectedLocation(null); }}
              style={{
                padding: '0.35rem 0.75rem',
                borderRadius: '20px',
                fontSize: '0.8rem',
                fontWeight: 600,
                border: 'none',
                cursor: 'pointer',
                background: activeFilter === day && !selectedLocation ? 'var(--accent-coral)' : 'var(--bg-tertiary)',
                color: activeFilter === day && !selectedLocation ? '#fff' : 'var(--text-secondary)'
              }}
            >
              📅 {day}
            </button>
          ))}

          <button
            onClick={() => { setActiveFilter('hotels'); setSelectedLocation(null); }}
            style={{
              padding: '0.35rem 0.75rem',
              borderRadius: '20px',
              fontSize: '0.8rem',
              fontWeight: 600,
              border: 'none',
              cursor: 'pointer',
              background: activeFilter === 'hotels' ? 'var(--accent-blue)' : 'var(--bg-tertiary)',
              color: activeFilter === 'hotels' ? '#fff' : 'var(--text-secondary)'
            }}
          >
            🏨 Hotels
          </button>

          <button
            onClick={() => { setActiveFilter('dining'); setSelectedLocation(null); }}
            style={{
              padding: '0.35rem 0.75rem',
              borderRadius: '20px',
              fontSize: '0.8rem',
              fontWeight: 600,
              border: 'none',
              cursor: 'pointer',
              background: activeFilter === 'dining' ? 'var(--accent-orange)' : 'var(--bg-tertiary)',
              color: activeFilter === 'dining' ? '#fff' : 'var(--text-secondary)'
            }}
          >
            🍽️ Dining
          </button>
        </div>

        <a 
          href={fullGoogleMapsUrl}
          target="_blank"
          rel="noopener noreferrer"
          style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '0.3rem', 
            fontSize: '0.8rem', 
            color: 'var(--accent-blue)', 
            fontWeight: 600, 
            textDecoration: 'none',
            padding: '0.3rem 0.6rem',
            borderRadius: '6px',
            background: 'rgba(56, 189, 248, 0.1)'
          }}
        >
          Open in Google Maps <ExternalLink size={13} />
        </a>
      </div>

      {/* Embedded Google Maps Frame */}
      <div style={{ flex: 1, position: 'relative', minHeight: '320px' }}>
        <iframe
          title="Google Maps Itinerary Explorer"
          width="100%"
          height="100%"
          style={{ border: 0, width: '100%', height: '100%' }}
          loading="lazy"
          allowFullScreen
          src={googleEmbedUrl}
        />
        <div style={{ position: 'absolute', top: '12px', left: '12px', background: 'rgba(15, 23, 42, 0.85)', backdropFilter: 'blur(8px)', padding: '0.4rem 0.85rem', borderRadius: '8px', border: '1px solid var(--border-subtle)', color: '#fff', fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.4rem', zIndex: 10 }}>
          <MapPin size={16} color="var(--accent-coral)" />
          <span>Viewing on Google Maps: <strong>{selectedLocation?.title || mapQuery}</strong></span>
        </div>
      </div>

      {/* Itinerary Location Pins Ribbon */}
      {filteredLocations.length > 0 && (
        <div style={{ height: '140px', background: 'var(--bg-secondary)', borderTop: '1px solid var(--border-subtle)', padding: '0.75rem 1rem', overflowX: 'auto', display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          {filteredLocations.map((loc, idx) => {
            const isSelected = selectedLocation && (selectedLocation.title === loc.title || selectedLocation.name === loc.title);
            const gmapsUrl = loc.google_maps_url || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(loc.title + ', ' + targetDest)}`;

            const badgeBg = loc.category === 'Hotel' ? 'var(--accent-blue)' : loc.category === 'Dining & Retail' ? 'var(--accent-orange)' : 'var(--accent-coral)';

            return (
              <motion.div 
                key={idx}
                whileHover={{ y: -2 }}
                onClick={() => setSelectedLocation({ name: loc.title, title: loc.title, day: loc.day, lat: loc.lat, lng: loc.lng, category: loc.category })}
                style={{
                  minWidth: '220px',
                  maxWidth: '240px',
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
                  <span style={{ fontSize: '0.75rem', background: badgeBg, color: '#fff', padding: '0.15rem 0.45rem', borderRadius: '4px', fontWeight: 700 }}>
                    {loc.day || loc.category || 'Sightseeing'}
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
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.2rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <MapPin size={12} color={badgeBg} />
                  <span>{loc.category || 'Sightseeing Attraction'}</span>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
