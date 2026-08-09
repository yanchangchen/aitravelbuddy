import React, { useEffect, useState } from 'react';
import { useTripStore } from '../../stores/tripStore';
import { Card, Badge, Button } from '../shared';
import { Map as MapIcon, Trash2, FolderOpen } from 'lucide-react';

export default function SavedTrips() {
  const { savedTrips, fetchSavedTrips, loadSavedTrip, deleteSavedTrip, destination } = useTripStore();
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    fetchSavedTrips();
  }, []);

  const handleDelete = async (e, tripId, dest) => {
    e.stopPropagation();
    if (window.confirm(`Are you sure you want to delete the saved itinerary for "${dest}"?`)) {
      setDeletingId(tripId);
      try {
        await deleteSavedTrip(tripId);
      } finally {
        setDeletingId(null);
      }
    }
  };

  if (!savedTrips || savedTrips.length === 0) {
    return (
      <div style={{ padding: '2rem 1rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        <MapIcon size={32} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
        <p style={{ margin: 0, fontSize: '0.9rem' }}>No saved trips yet.</p>
        <span style={{ fontSize: '0.75rem', opacity: 0.7 }}>Saved plans will appear here.</span>
      </div>
    );
  }

  return (
    <div style={{ padding: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {savedTrips.map((trip, i) => {
        const isCurrentActive = destination && trip.destination && destination.toLowerCase().includes(trip.destination.toLowerCase());
        const tripId = trip.id || `saved_${i}`;

        return (
          <Card 
            key={tripId} 
            style={{ 
              cursor: 'pointer', 
              padding: '0.85rem 1rem',
              borderColor: isCurrentActive ? 'var(--accent-coral)' : 'var(--border-subtle)',
              background: isCurrentActive ? 'rgba(255, 107, 107, 0.05)' : undefined,
              transition: 'all 0.2s ease'
            }}
            onClick={() => loadSavedTrip(trip)}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.35rem' }}>
              <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                {trip.destination}
              </h4>
              <button
                onClick={(e) => handleDelete(e, trip.id, trip.destination)}
                disabled={deletingId === trip.id}
                title="Delete saved trip"
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  padding: '0.2rem',
                  borderRadius: '4px',
                  display: 'flex',
                  alignItems: 'center',
                  transition: 'color 0.2s ease'
                }}
                onMouseEnter={(e) => e.currentTarget.style.color = 'var(--accent-coral)'}
                onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-muted)'}
              >
                <Trash2 size={15} />
              </button>
            </div>
            
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: '0 0 0.5rem' }}>
              {trip.dates || '5 Days Plan'} • {trip.travelers || '2 Adults, 1 Child'}
            </p>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Badge variant="pending" style={{ fontSize: '0.7rem' }}>{trip.persona || 'Family'}</Badge>
              <span style={{ fontSize: '0.75rem', color: 'var(--accent-blue)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                <FolderOpen size={12} /> Load Plan
              </span>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
