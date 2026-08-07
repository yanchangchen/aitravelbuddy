import React from 'react';
import { useTripStore } from '../../stores/tripStore';
import { CheckCircle2, Clock, PlayCircle, XCircle } from 'lucide-react';

export default function AgentMonitor() {
  const { agentProgress, planStatus, currentNode, overallProgress } = useTripStore();

  if (planStatus === 'idle') return null;

  const nodes = [
    { id: 'itinerary_agent', name: '🗺️ Sightseeing Itinerary Agent' },
    { id: 'food_retail_agent', name: '🍽️ Food & Retail Agent' },
    { id: 'hospitality_agent', name: '🏨 Hospitality & Hotel Agent' },
    { id: 'purchasing_agent', name: '🛒 Flight & Booking Logistics' },
    { id: 'budget_guardrail', name: '💰 Budget Guardrail Audit' },
    { id: 'agent_as_judge', name: '⚖️ Agent-as-Judge Quality Audit' }
  ];

  const completedCount = nodes.filter(n => agentProgress[n.id] === 'done').length;
  const runningCount = nodes.filter(n => agentProgress[n.id] === 'running' || currentNode === n.id).length;
  const computedPercent = Math.min(100, Math.round(((completedCount + (runningCount ? 0.5 : 0)) / nodes.length) * 100));
  const percent = planStatus === 'complete' ? 100 : Math.max(overallProgress || 0, computedPercent);

  return (
    <div style={{ padding: '1rem', borderTop: '1px solid var(--border-subtle)', background: 'var(--bg-secondary)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <h3 style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '1px', margin: 0 }}>Agent Network Stream</h3>
        <span style={{ fontSize: '0.875rem', fontWeight: 600, color: planStatus === 'complete' ? 'var(--accent-green)' : 'var(--accent-coral)' }}>
          {planStatus === 'complete' ? '100% Done' : `${percent}%`}
        </span>
      </div>

      <div style={{ height: '6px', background: 'var(--bg-tertiary)', borderRadius: '3px', overflow: 'hidden', marginBottom: '1rem' }}>
        <div style={{ height: '100%', width: `${planStatus === 'complete' ? 100 : percent}%`, background: 'var(--gradient-coral)', transition: 'width 0.3s ease' }} />
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {nodes.map(node => {
          const status = agentProgress[node.id] || (planStatus === 'complete' ? 'done' : 'pending');
          const isCurrent = currentNode === node.id || status === 'running';
          
          let Icon = Clock;
          let color = 'var(--text-muted)';
          
          if (status === 'running' || isCurrent) {
            Icon = PlayCircle;
            color = 'var(--accent-blue)';
          } else if (status === 'done' || planStatus === 'complete') {
            Icon = CheckCircle2;
            color = 'var(--accent-green)';
          } else if (status === 'error') {
            Icon = XCircle;
            color = 'var(--accent-coral)';
          }

          return (
            <div key={node.id} className="agent-node" style={{ background: (status === 'running' || isCurrent) ? 'rgba(56, 189, 248, 0.12)' : 'var(--bg-tertiary)', borderLeft: `3px solid ${color}`, padding: '0.5rem 0.75rem', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Icon size={16} color={color} className={(status === 'running' || isCurrent) ? 'animate-pulse' : ''} />
              <span style={{ fontSize: '0.875rem', fontWeight: (status === 'running' || isCurrent) ? 600 : 500, color: status === 'pending' && planStatus !== 'complete' ? 'var(--text-muted)' : 'var(--text-primary)' }}>{node.name}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
