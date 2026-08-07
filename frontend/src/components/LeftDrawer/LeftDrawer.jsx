import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Menu } from 'lucide-react';
import TripLogistics from './TripLogistics';
import PersonaPanel from './PersonaPanel';
import SavedTrips from './SavedTrips';
import { useTripStore } from '../../stores/tripStore';

const Accordion = ({ title, children, defaultOpen = false }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  return (
    <div style={{ borderBottom: '1px solid var(--border-subtle)' }}>
      <div className="accordion-header" onClick={() => setIsOpen(!isOpen)}>
        <h3 style={{ fontSize: '1rem', fontWeight: 600, margin: 0 }}>{title}</h3>
        {isOpen ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
      </div>
      {isOpen && <div>{children}</div>}
    </div>
  );
};

export default function LeftDrawer() {
  const { toggleLeftDrawer } = useTripStore();

  return (
    <>
      <div style={{ padding: '1rem', display: 'flex', alignItems: 'center', borderBottom: '1px solid var(--border-subtle)', background: 'var(--bg-secondary)', position: 'sticky', top: 0, zIndex: 10 }}>
        <button className="btn-icon" onClick={toggleLeftDrawer} style={{ marginRight: '0.5rem' }}>
          <Menu size={20} />
        </button>
        <span style={{ fontWeight: 600 }}>Trip Details</span>
      </div>
      <div style={{ flex: 1, overflowY: 'auto' }}>
        <Accordion title="📍 Trip Logistics" defaultOpen={true}>
          <TripLogistics />
        </Accordion>
        <Accordion title="🎭 Persona & Style" defaultOpen={true}>
          <PersonaPanel />
        </Accordion>
        <Accordion title="💾 Saved Trips" defaultOpen={false}>
          <SavedTrips />
        </Accordion>
      </div>
    </>
  );
}
