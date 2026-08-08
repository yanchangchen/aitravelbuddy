import React from 'react';
import { useTripStore } from '../../stores/tripStore';
import { Card, Badge } from '../shared';
import { Map as MapIcon } from 'lucide-react';

export default function SavedTrips() {
  const { savedTrips, loadSavedTrip } = useTripStore();

  if (!savedTrips || savedTrips.length === 0) {
    return (
      <div style={{ padding: '2rem 1rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        <MapIcon size={32} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
        <p>No saved trips yet.</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {savedTrips.map((trip, i) => (
        <Card 
          key={i} 
          style={{ cursor: 'pointer', padding: '1rem' }}
          onClick={() => loadSavedTrip(trip)}
        >
          <h4 style={{ margin: '0 0 0.5rem' }}>{trip.destination}</h4>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', margin: '0 0 0.5rem' }}>{trip.dates}</p>
          <Badge>{trip.persona}</Badge>
        </Card>
      ))}
    </div>
  );
}
