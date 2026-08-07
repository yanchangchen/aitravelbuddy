import React from 'react';
import { useTripStore } from '../../stores/tripStore';
import TimelineView from './TimelineView';
import MapView from './MapView';
import BudgetBar from './BudgetBar';
import HotelCards from './HotelCards';
import FlightBooking from './FlightBooking';
import { Button } from '../shared';
import { Square } from 'lucide-react';

export default function CenterCanvas() {
  const { centerView, setCenterView, planResult, planStatus, currentNode, agentProgress, stopPlanning } = useTripStore();

  const tabs = [
    { id: 'timeline', label: 'Timeline' },
    { id: 'map', label: 'Map' },
    { id: 'split', label: 'Split View' },
    { id: 'hotels', label: 'Hotels' },
    { id: 'flights', label: 'Bookings' }
  ];

  const nodeNames = {
    itinerary_agent: '🗺️ Sightseeing Itinerary Agent',
    food_retail_agent: '🍽️ Food & Retail Agent',
    hospitality_agent: '🏨 Hospitality & Hotel Agent',
    purchasing_agent: '🛒 Flight & Booking Logistics',
    budget_guardrail: '💰 Budget Guardrail Audit',
    agent_as_judge: '⚖️ Agent-as-Judge Quality Audit'
  };

  const completedCount = Object.values(agentProgress).filter(v => v === 'done').length;
  const percent = Math.min(100, Math.round((completedCount / 6) * 100));

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
      {planStatus === 'planning' && (
        <div style={{ background: 'linear-gradient(90deg, rgba(255,107,107,0.15), rgba(56,189,248,0.15))', borderBottom: '1px solid var(--accent-coral)', padding: '0.75rem 1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="spinner" style={{ display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', border: '2px solid var(--accent-coral)', borderTopColor: 'transparent', animation: 'spin 1s linear infinite' }} />
              Running Agent Graph: {nodeNames[currentNode] || 'Initializing Collaborative Agents...'}
            </span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <span style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--accent-coral)' }}>{percent}% Complete</span>
              <Button size="sm" variant="secondary" icon={Square} onClick={stopPlanning} style={{ fontSize: '0.75rem', padding: '0.2rem 0.6rem', borderColor: 'var(--accent-coral)', color: 'var(--accent-coral)' }}>
                Stop & Show Partial Plan
              </Button>
            </div>
          </div>
          <div style={{ height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${percent}%`, background: 'var(--gradient-coral)', transition: 'width 0.3s ease' }} />
          </div>
        </div>
      )}

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
