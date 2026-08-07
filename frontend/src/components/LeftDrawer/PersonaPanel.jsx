import React from 'react';
import { useTripStore } from '../../stores/tripStore';
import { Select, Card } from '../shared';

const personas = ['Solo', 'Business', 'Couple', 'Family', 'Backpacker', 'Custom'];

export default function PersonaPanel() {
  const { selectedPersona, customPersona, setPersona } = useTripStore();

  return (
    <div style={{ padding: '1rem' }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
        {personas.map(p => (
          <button 
            key={p}
            onClick={() => setPersona(p)}
            style={{ 
              padding: '0.5rem 1rem', 
              borderRadius: 'var(--radius-xl)', 
              border: `1px solid ${selectedPersona === p ? 'var(--accent-coral)' : 'var(--border-subtle)'}`,
              background: selectedPersona === p ? 'rgba(255, 107, 107, 0.1)' : 'transparent',
              color: selectedPersona === p ? 'var(--accent-coral)' : 'var(--text-primary)',
              cursor: 'pointer',
              fontSize: '0.875rem'
            }}
          >
            {p}
          </button>
        ))}
      </div>

      {selectedPersona === 'Custom' && (
        <Card className="animate-fade-in" style={{ padding: '1rem', marginTop: '1rem' }}>
          <Select label="Pace" options={['Relaxed', 'Medium', 'Fast-paced']} value={customPersona.tempo} onChange={(e) => setPersona('Custom', { tempo: e.target.value })} />
          <Select label="Dining" options={['Street Food', 'Casual', 'Fine Dining']} value={customPersona.dining} onChange={(e) => setPersona('Custom', { dining: e.target.value })} />
          <Select label="Lodging" options={['Hostel', 'Budget', 'Comfortable', 'Luxury']} value={customPersona.lodging} onChange={(e) => setPersona('Custom', { lodging: e.target.value })} />
          
          <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Special Rules</label>
          <textarea 
            className="input-field" 
            rows={3} 
            placeholder="E.g., No early mornings, vegan restaurants only..."
            value={customPersona.rules}
            onChange={(e) => setPersona('Custom', { rules: e.target.value })}
            style={{ resize: 'vertical' }}
          />
        </Card>
      )}
    </div>
  );
}
