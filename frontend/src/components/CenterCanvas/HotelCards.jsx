import React from 'react';
import { useTripStore } from '../../stores/tripStore';
import { GlassCard, Badge } from '../shared';

export default function HotelCards() {
  const { planResult } = useTripStore();
  
  if (!planResult || !planResult.hotel_recommendations) {
    return <div style={{ padding: '2rem', textAlign: 'center' }}>No hotel recommendations available.</div>;
  }

  // Mock parsing
  const hotels = [
    { name: 'Grand Plaza', rating: 5, price: 200, total: 1400, amenities: ['Pool', 'Spa', 'Free WiFi'], desc: 'Luxury stay with central access.', recommended: true },
    { name: 'City Inn', rating: 3, price: 90, total: 630, amenities: ['Free Breakfast', 'Gym'], desc: 'Budget friendly and clean.', recommended: false },
    { name: 'Boutique Stay', rating: 4, price: 150, total: 1050, amenities: ['Pet Friendly', 'Bar'], desc: 'Unique local vibe.', recommended: false },
  ];

  return (
    <div style={{ padding: '2rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem' }}>
      {hotels.map((h, i) => (
        <GlassCard key={i} style={h.recommended ? { borderColor: 'var(--accent-coral)', boxShadow: 'var(--shadow-glow)' } : {}}>
          {h.recommended && <Badge variant="approved" style={{ marginBottom: '1rem' }}>Top Pick</Badge>}
          <h3>{h.name}</h3>
          <div style={{ color: 'var(--accent-gold)', marginBottom: '0.5rem' }}>{'★'.repeat(h.rating)}</div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1rem' }}>{h.desc}</p>
          
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
            {h.amenities.map(a => <span key={a} style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-sm)' }}>{a}</span>)}
          </div>
          
          <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
            <span style={{ fontSize: '1.5rem', fontWeight: 700 }}>${h.price}</span>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>/ night</span>
          </div>
        </GlassCard>
      ))}
    </div>
  );
}
