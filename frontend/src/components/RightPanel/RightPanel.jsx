import React from 'react';
import { useTripStore } from '../../stores/tripStore';
import { PanelRightClose } from 'lucide-react';
import ConciergeChat from './ConciergeChat';

export default function RightPanel() {
  const { toggleRightPanel } = useTripStore();

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '0.75rem 1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)' }}>
        <span style={{ fontWeight: 600 }}>AI Concierge Chat</span>
        <button className="btn-icon" onClick={toggleRightPanel}>
          <PanelRightClose size={20} />
        </button>
      </div>
      
      <div style={{ flex: 1, minHeight: 0 }}>
        <ConciergeChat />
      </div>
    </div>
  );
}
