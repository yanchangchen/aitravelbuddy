import React from 'react';
import { useTripStore } from '../../stores/tripStore';
import { GlassCard, Button } from '../shared';
import { Plane, Car } from 'lucide-react';

export default function FlightBooking() {
  const { planResult, selfDrive } = useTripStore();
  
  if (!planResult || !planResult.purchasing_guide) {
    return <div style={{ padding: '2rem', textAlign: 'center' }}>No booking guide available.</div>;
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <GlassCard style={{ marginBottom: '2rem' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}><Plane color="var(--accent-blue)" /> Flights</h2>
        <div style={{ padding: '1rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-md)', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span>Outbound: JFK → NRT</span>
            <strong>$450</strong>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
            <span>Delta Airlines • Non-stop</span>
          </div>
        </div>
        <Button variant="primary">Book Flights on Skyscanner</Button>
      </GlassCard>

      {selfDrive && (
        <GlassCard>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}><Car color="var(--accent-green)" /> Car Rental</h2>
          <div style={{ padding: '1rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-md)', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span>Compact SUV • 7 Days</span>
              <strong>$210</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
              <span>Hertz Rental (Airport Pickup)</span>
            </div>
          </div>
          <Button variant="secondary">Book Car on Hertz</Button>
        </GlassCard>
      )}
    </div>
  );
}
