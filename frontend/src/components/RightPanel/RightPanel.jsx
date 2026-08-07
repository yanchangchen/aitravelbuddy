import React from 'react';
import { useTripStore } from '../../stores/tripStore';
import { PanelRightClose } from 'lucide-react';
import ConciergeChat from './ConciergeChat';
import AgentMonitor from './AgentMonitor';
import JudgeVerdict from './JudgeVerdict';

export default function RightPanel() {
  const { toggleRightPanel, planStatus } = useTripStore();

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '0.75rem 1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)' }}>
        <span style={{ fontWeight: 600 }}>Concierge</span>
        <button className="btn-icon" onClick={toggleRightPanel}>
          <PanelRightClose size={20} />
        </button>
      </div>
      
      <div style={{ flex: 1, minHeight: 0 }}>
        <ConciergeChat />
      </div>

      {planStatus !== 'idle' && (
        <div style={{ flexShrink: 0, maxHeight: '50%', overflowY: 'auto' }}>
          <AgentMonitor />
          <JudgeVerdict />
        </div>
      )}
    </div>
  );
}
