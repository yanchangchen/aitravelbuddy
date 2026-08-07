import React from 'react';
import { useTripStore } from '../../stores/tripStore';
import TimelineView from './TimelineView';
import MapView from './MapView';
import BudgetBar from './BudgetBar';
import HotelCards from './HotelCards';
import FlightBooking from './FlightBooking';

export default function CenterCanvas() {
  const { centerView, setCenterView, planResult } = useTripStore();

  const tabs = [
    { id: 'timeline', label: 'Timeline' },
    { id: 'map', label: 'Map' },
    { id: 'split', label: 'Split View' },
    { id: 'hotels', label: 'Hotels' },
    { id: 'flights', label: 'Bookings' }
  ];

  const renderContent = () => {
    switch (centerView) {
      case 'timeline': return <div style={{ paddingBottom: '100px' }}><TimelineView /></div>;
      case 'map': return <MapView />;
      case 'hotels': return <HotelCards />;
      case 'flights': return <FlightBooking />;
      case 'split': return (
        <div style={{ display: 'flex', height: '100%' }}>
          <div style={{ flex: 1, overflowY: 'auto', paddingBottom: '100px' }}><TimelineView /></div>
          <div style={{ flex: 1 }}><MapView /></div>
        </div>
      );
      default: return <TimelineView />;
    }
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', position: 'relative' }}>
      <div style={{ display: 'flex', padding: '1rem', gap: '0.5rem', background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-subtle)' }}>
        {tabs.map(t => (
          <button 
            key={t.id}
            onClick={() => setCenterView(t.id)}
            style={{ 
              background: centerView === t.id ? 'var(--bg-tertiary)' : 'transparent',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: 'var(--radius-md)',
              color: centerView === t.id ? 'var(--text-primary)' : 'var(--text-secondary)',
              cursor: 'pointer',
              fontWeight: 500,
              transition: 'all var(--transition-fast)'
            }}
          >
            {t.label}
          </button>
        ))}
      </div>
      
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {renderContent()}
      </div>

      {planResult && <BudgetBar />}
    </div>
  );
}
