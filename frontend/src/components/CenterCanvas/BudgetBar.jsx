import React from 'react';
import { useTripStore } from '../../stores/tripStore';
import { AnimatedNumber } from '../shared';
import { DollarSign, Coffee, Map, Home, Plane } from 'lucide-react';

function extractCostFromText(text, tag, defaultVal) {
  if (!text || typeof text !== 'string') return defaultVal;
  const match = text.match(new RegExp(`${tag}:?\\s*([\\d,]+\\.?\\d*)`, 'i'));
  if (match) return parseFloat(match[1].replace(/,/g, ''));
  
  const matches = text.match(/(?:S\$|\$)\s*([\d,]+\.?\d*)/g);
  if (matches && matches.length > 0) {
    let sum = 0;
    matches.forEach(m => {
      const num = parseFloat(m.replace(/[^0-9.]/g, ''));
      if (!isNaN(num) && num > 0 && num < 10000) sum += num;
    });
    if (sum > 0) return Math.min(sum, defaultVal * 3);
  }
  return defaultVal;
}

export default function BudgetBar() {
  const { planResult, partialResult, budget, currency, noBudget } = useTripStore();
  
  const activeResult = planResult || (Object.keys(partialResult).length > 0 ? partialResult : null);
  if (!activeResult) return null;

  const flightCost = extractCostFromText(activeResult.purchasing_guide, 'AIRFARE_TOTAL_SGD', 580);
  const hotelCost = extractCostFromText(activeResult.hotel_recommendations, 'HOTEL_TOTAL_SGD', 840);
  const diningCost = extractCostFromText(activeResult.food_and_retail, 'FOOD_RETAIL_TOTAL_SGD', 360);
  const sightCost = extractCostFromText(activeResult.itinerary, 'SIGHTSEEING_TOTAL_SGD', 240);

  const total = Math.round(flightCost + hotelCost + diningCost + sightCost);
  const currentCurrency = currency || 'SGD';

  const categories = [
    { name: 'Flights', icon: Plane, amount: Math.round(flightCost), color: 'var(--accent-blue)' },
    { name: 'Hotels', icon: Home, amount: Math.round(hotelCost), color: 'var(--accent-coral)' },
    { name: 'Dining', icon: Coffee, amount: Math.round(diningCost), color: 'var(--accent-orange)' },
    { name: 'Sightseeing', icon: Map, amount: Math.round(sightCost), color: 'var(--accent-green)' }
  ];

  const pct = (!noBudget && budget > 0) ? Math.min((total / budget) * 100, 100) : 100;

  return (
    <div style={{ position: 'sticky', bottom: 0, left: 0, right: 0, background: 'var(--bg-glass)', backdropFilter: 'blur(12px)', borderTop: '1px solid var(--border-subtle)', padding: '1rem 2rem', zIndex: 10 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '2rem' }}>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'rgba(255, 107, 107, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <DollarSign color="var(--accent-coral)" />
          </div>
          <div>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              {noBudget ? 'Total Estimated (Flexible Budget)' : 'Total Estimated Budget'}
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              S$ <AnimatedNumber value={total} /> {currentCurrency}
            </div>
          </div>
        </div>

        <div style={{ flex: 1, display: 'flex', gap: '1.5rem', justifyContent: 'center' }}>
          {categories.map(c => (
            <div key={c.name} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <c.icon size={16} color={c.color} style={{ marginBottom: '0.25rem' }} />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{c.name}</span>
              <span style={{ fontWeight: 600 }}>S${c.amount}</span>
            </div>
          ))}
        </div>

        <div style={{ width: '200px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '0.5rem' }}>
            <span>{noBudget ? 'Budget Allocation' : 'Budget Utilized'}</span>
            <span>{noBudget ? 'Optimal' : `${pct.toFixed(0)}%`}</span>
          </div>
          <div style={{ height: '6px', background: 'var(--bg-tertiary)', borderRadius: '3px', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${pct}%`, background: (!noBudget && pct > 90) ? 'var(--accent-coral)' : 'var(--accent-green)', transition: 'width 1s ease' }} />
          </div>
        </div>
      </div>
    </div>
  );
}
