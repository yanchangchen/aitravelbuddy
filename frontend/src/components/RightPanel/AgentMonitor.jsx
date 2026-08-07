import React from 'react';
import { useTripStore } from '../../stores/tripStore';
import { CheckCircle2, Clock, PlayCircle, XCircle } from 'lucide-react';

export default function AgentMonitor() {
  const { agentProgress, planStatus } = useTripStore();

  if (planStatus === 'idle') return null;

  const nodes = [
    { id: 'planner', name: 'Logistics Planner' },
    { id: 'researcher', name: 'Research Agent' },
    { id: 'judge', name: 'Critique Judge' },
    { id: 'finalizer', name: 'Finalizer' }
  ];

  return (
    <div style={{ padding: '1rem', borderTop: '1px solid var(--border-subtle)', background: 'var(--bg-secondary)' }}>
      <h3 style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '1px' }}>Agent Network</h3>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {nodes.map(node => {
          const status = agentProgress[node.id] || 'pending';
          
          let Icon = Clock;
          let color = 'var(--text-muted)';
          
          if (status === 'running') {
            Icon = PlayCircle;
            color = 'var(--accent-blue)';
          } else if (status === 'done') {
            Icon = CheckCircle2;
            color = 'var(--accent-green)';
          } else if (status === 'error') {
            Icon = XCircle;
            color = 'var(--accent-coral)';
          }

          return (
            <div key={node.id} className="agent-node" style={{ background: status === 'running' ? 'rgba(56, 189, 248, 0.1)' : 'var(--bg-tertiary)', borderLeft: `3px solid ${color}` }}>
              <Icon size={18} color={color} className={status === 'running' ? 'animate-pulse' : ''} />
              <span style={{ fontSize: '0.875rem', fontWeight: 500, color: status === 'pending' ? 'var(--text-muted)' : 'var(--text-primary)' }}>{node.name}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
