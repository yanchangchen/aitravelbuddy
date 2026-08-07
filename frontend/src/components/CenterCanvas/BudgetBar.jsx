import React from 'react';
import { useTripStore } from '../../stores/tripStore';
import { AnimatedNumber, Select } from '../shared';
import { DollarSign, Coffee, Map, Home, Plane } from 'lucide-react';

export default function BudgetBar() {
  const { planResult, budget, currency, setLogistics } = useTripStore();
  
  if (!planResult) return null;

  // Mock calculation
  const total = 1250;
  const categories = [
    { name: 'Flights', icon: Plane, amount: 500, color: 'var(--accent-blue)' },
    { name: 'Hotels', icon: Home, amount: 400, color: 'var(--accent-coral)' },
    { name: 'Dining', icon: Coffee, amount: 200, color: 'var(--accent-orange)' },
    { name: 'Sightseeing', icon: Map, amount: 150, color: 'var(--accent-green)' }
  ];

  const pct = budget > 0 ? Math.min((total / budget) * 100, 100) : 0;

  return (
    <div style={{ position: 'sticky', bottom: 0, left: 0, right: 0, background: 'var(--bg-glass)', backdropFilter: 'blur(12px)', borderTop: '1px solid var(--border-subtle)', padding: '1rem 2rem', zIndex: 10 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '2rem' }}>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'rgba(255, 107, 107, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <DollarSign color="var(--accent-coral)" />
          </div>
          <div>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Total Estimated</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              <AnimatedNumber value={total} /> {currency}
            </div>
          </div>
        </div>

        <div style={{ flex: 1, display: 'flex', gap: '1.5rem', justifyContent: 'center' }}>
          {categories.map(c => (
            <div key={c.name} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <c.icon size={16} color={c.color} style={{ marginBottom: '0.25rem' }} />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{c.name}</span>
              <span style={{ fontWeight: 600 }}>${c.amount}</span>
            </div>
          ))}
        </div>

        <div style={{ width: '200px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '0.5rem' }}>
            <span>Budget Utilized</span>
            <span>{pct.toFixed(0)}%</span>
          </div>
          <div style={{ height: '6px', background: 'var(--bg-tertiary)', borderRadius: '3px', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${pct}%`, background: pct > 90 ? 'var(--accent-coral)' : 'var(--accent-green)', transition: 'width 1s ease' }} />
          </div>
        </div>
      </div>
    </div>
  );
}
