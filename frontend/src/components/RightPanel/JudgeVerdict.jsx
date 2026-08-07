import React from 'react';
import { useTripStore } from '../../stores/tripStore';
import { Badge } from '../shared';

export default function JudgeVerdict() {
  const { planResult } = useTripStore();

  if (!planResult || !planResult.judge_verdict) return null;

  const isApproved = planResult.judge_verdict.toLowerCase().includes('approve');
  const score = planResult.judge_score || 95;

  return (
    <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border-subtle)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div>
          <h3 style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', margin: '0 0 0.25rem' }}>Judge Verdict</h3>
          <Badge variant={isApproved ? 'approved' : 'failed'}>{isApproved ? 'Approved' : 'Failed'}</Badge>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: isApproved ? 'var(--accent-green)' : 'var(--accent-coral)' }}>{score}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Quality Score</div>
        </div>
      </div>
      
      {!isApproved && (
        <div style={{ fontSize: '0.875rem', color: 'var(--accent-coral)', background: 'rgba(255, 107, 107, 0.1)', padding: '0.75rem', borderRadius: 'var(--radius-sm)' }}>
          Plan exceeds budget. Please relax budget constraints or allow cheaper alternatives.
        </div>
      )}
    </div>
  );
}
